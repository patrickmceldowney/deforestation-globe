from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# --- paths ---

ROOT = Path(__file__).parent
DATA_DIR = ROOT.parent / "data"
RAW_DIR = DATA_DIR / "raw"
COG_DIR = DATA_DIR / "cog"
TILE_DIR = DATA_DIR / "output" / "tiles"
MANIFEST_PATH = DATA_DIR / "output" / "manifest.json"

for d in (RAW_DIR, COG_DIR, TILE_DIR):
    d.mkdir(parents=True, exist_ok=True)

# --- Planet credentials ---

PL_API_KEY = os.environ.get("PL_API_KEY", "")

# --- object storage ---

S3_ENDPOINT_URL = os.environ.get("S3_ENDPOINT_URL", "")
S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY", "")
S3_SECRET_KEY = os.environ.get("S3_SECRET_KEY", "")
S3_BUCKET = os.environ.get("S3_BUCKET", "eco-monitor-tiles")
PUBLIC_TILES_BASE_URL = os.environ.get("PUBLIC_TILES_BASE_URL", "")

# --- area of interest ---
# Get this from geojson.io
#
AOI_BBOX = (-60.20, -3.20, -60.00, -3.00)
AOI_NAME = "example-aoi"

YEARS = [2021, 2022, 2023]

# --- layers ---
# Each layer maps to one tile pyramid per year. `kind` controls how
# cog_export.py and tile_pyramid.py render it.


@dataclass
class LayerDef:
    id: str  # used in tile paths and manifest.json
    label: str  # shown in UI toggle
    kind: str  # "rgb" | "single_band_continuous" | "categorical"
    colormap: str | None = None  # rio-tiler colormap name, if applicable
    rescale: tuple[float, float] | None = None  # e.g. (0.0, 1.0)


LAYERS: list[LayerDef] = [
    LayerDef(id="rgb", label="Satellite", kind="rgb"),
    LayerDef(
        id="ndvi",
        label="NDVI",
        kind="single_band_continuous",
        colormap="rdylgn",
        rescale=(-1.0, 1.0),
    ),
    LayerDef(id="loss", label="Forest Loss", kind="categorical", colormap="loss_year"),
]

TILE_MIN_ZOOM = 8
TILE_MAX_ZOOM = 15
