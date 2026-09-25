"""
Planet API client for downloading satellite imagery.
"""

from __future__ import annotations

import time
from pathlib import Path

import requests
from config import AOI_BBOX, PL_API_KEY, RAW_DIR

ORDERS_API = "https://api.planet.com/compute/ops/orders/v2"
DATA_API = "https://api.planet.com/data/v1/quick-search"


def _auth():
    return (PL_API_KEY, "")


def bbox_to_geojson_polygon(bbox: tuple[float, float, float, float]) -> dict:
    west, south, east, north = bbox
    return {
        "type": "Polygon",
        "coordinates": [
            [[west, south], [east, south], [east, north], [west, north], [west, south]]
        ],
    }


def search_scenes(
    bbox, year: int, item_type: str = "PSScene", max_items: int = 5
) -> list[dict]:
    """Find candidate scenes over the AOI for the given year.

    Widen `date_range` or relax `cloud_cover` if this comes back empty
    single-scene coverage of an exact AOI/year is not guaranteed.
    """
    body = {
        "item_types": [item_type],
        "filter": {
            "type": "AndFilter",
            "config": [
                {
                    "type": "GeometryFilter",
                    "field_name": "geometry",
                    "config": bbox_to_geojson_polygon(bbox),
                },
                {
                    "type": "DateRangeFilter",
                    "field_name": "acquired",
                    "config": {
                        "gte": f"{year}-01-01T00:00:00Z",
                        "lte": f"{year}-12-31T23:59:59Z",
                    },
                },
                {
                    "type": "RangeFilter",
                    "field_name": "cloud_cover",
                    "config": {"lte": 0.1},
                },
            ],
        },
    }

    resp = requests.post(DATA_API, json=body, auth=_auth())
    if not resp.ok:
        print("Planet API error:", resp.status_code, resp.text)
    resp.raise_for_status()
    return resp.json()["features"][:max_items]


def place_order(
    item_id: str, bbox, item_type: str = "PSScene", name: str = "eco-monitor-order"
) -> str:
    """Order one item, no server-side tools.

    Clipping to the AOI happens locally after download rather than via the Orders API `clip` tool,
    since that tool requires higher account permissions.
    """
    body = {
        "name": name,
        "products": [
            {
                "item_ids": [item_id],
                "item_type": item_type,
                "product_bundle": "analytic_sr_udm2",
            }
        ],
    }
    resp = requests.post(ORDERS_API, json=body, auth=_auth())
    if not resp.ok:
        print("Planet API error:", resp.status_code, resp.text)
    resp.raise_for_status()
    return resp.json()["id"]


def wait_for_order(
    order_id: str, poll_seconds: int = 15, timeout_seconds: int = 1800
) -> dict:
    """Poll until the order is 'sucess' or 'failed'."""
    url = f"{ORDERS_API}/{order_id}"
    waited = 0
    while waited < timeout_seconds:
        resp = requests.get(url, auth=_auth())
        resp.raise_for_status()
        status = resp.json()["state"]
        if status == "success":
            return resp.json()
        if status == "failed":
            raise RuntimeError(f"Planet order {order_id} failed: {resp.json()}")
        time.sleep(poll_seconds)
        waited += poll_seconds
    raise TimeoutError(f"Order {order_id} timed out after {waited} seconds")


def download_order(order_details: dict, dest_dir: Path = RAW_DIR) -> list[Path]:
    """Download every delivered asset to dest_dir. Returns local paths."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for result in order_details["_links"]["results"]:
        location = result["location"]
        name = result["name"].split("/")[-1]
        out_path = dest_dir / name
        with requests.get(location, stream=True) as r:
            r.raise_for_status()
            with open(out_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1 << 20):
                    f.writelines(chunk)

        saved.append(out_path)
    return saved


if __name__ == "__main__":
    import json

    scenes = search_scenes(AOI_BBOX, year=2023)
    print(f"Found {len(scenes)} candidate scenes")
    print(json.dumps([s["id"] for s in scenes], indent=2))
