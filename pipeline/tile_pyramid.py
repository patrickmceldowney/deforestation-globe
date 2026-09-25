"""
Cut a COG into a static {z}/{x}/{y}.png tile pyramid, rendered once, not
per-request. This is the file that replaces a live tiler for v1.
"""

from __future__ import annotations

import json
from pathlib import Path

import mercantile
import numpy as np
from PIL import Image
from rio_tiler.colormap import cmap as default_cmaps
from rio_tiler.io import Rasterio

from config import LayerDef


def _tiles_for_bounds(
    bounds: tuple[float, float, float, float], min_zoom: int, max_zoom: int
):
    """Yield for every tile intersecting bounds at each zoom."""
    for z in range(min_zoom, max_zoom + 1):
        for tile in mercantile.tiles(*bounds, [z]):
            yield tile.z, tile.x, tile.y


def render_tile(
    cog_path: str, z: int, x: int, y: int, layer: LayerDef
) -> Image.Image | None:
    """Render one tile as a PIL image, or None if the tile has no data."""
    with Rasterio(cog_path) as src:
        try:
            img = src.tile(x, y, z)
        except Exception:
            return None

        if layer.kind == "rgb":
            arr = img.data
            return Image.fromarray(np.moveaxis(arr[:3], 0, -1), mode="RGB")

        if layer.kind == "single_band_continuous":
            colormap = default_cmaps.get(layer.colormap or "viridis")
            img.rescale(in_range=[layer.rescale], out_range=[(0, 255)])
            img_colored = img.apply_colormap(colormap)
            arr = np.moveaxis(img_colored.data, 0, -1)
            return Image.fromarray(arr, mode="RGBA")

        if layer.kind == "categorical":
            # TODO: swap in real discrete colormap keyed to loss-year
            # values once change_detection.py produces real output.
            # Currently rendering as a flat semi-transparent red mask
            band = img.data[0]
            rgba = np.zeros((*band.shape, 4), dtype="uint8")
            rgba[band > 0] = [220, 50, 47, 200]
            return Image.fromarray(rgba, mode="RGBA")

        raise ValueError(f"Unknown layer kind: {layer.kind}")


def build_pyramid(
    cog_path: str,
    layer: LayerDef,
    year: int,
    out_dir: Path,
    min_zoom: int,
    max_zoom: int,
) -> int:
    """Render every tile for one layer/year. Returns count of tiles written."""
    with Rasterio(cog_path) as src:
        bounds = src.geographic_bounds

    written = 0
    for z, x, y in _tiles_for_bounds(bounds, min_zoom, max_zoom):
        tile_img = render_tile(cog_path, z, x, y, layer)
        if tile_img is None:
            continue

        tile_dir = out_dir / layer.id / str(year) / str(z) / str(x)
        tile_dir.mkdir(parents=True, exist_ok=True)
        tile_img.save(tile_dir / f"{y}.png")
        written += 1

    return written


def write_manifest(
    manifest_path: Path,
    aoi_name: str,
    aoi_bbox: tuple,
    layers: list[LayerDef],
    years: list[int],
    public_base_url: str,
) -> None:
    """The contract file `web/` reads. Keep this shape stable - changing it means updating web/lib/layers.ts too."""
    manifest = {
        "aoi": {"name": aoi_name, "bbox": list(aoi_bbox)},
        "years": years,
        "layers": [
            {
                "id": l.id,
                "label": l.label,
                "kind": l.kind,
                "tileUrlTemplate": f"{public_base_url}/tiles/{l.id}/{{year}}/{{z}}/{{x}}/{{y}}.png",
            }
            for l in layers
        ],
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest))
