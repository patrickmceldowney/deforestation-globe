"""
Turn a raw raster into a valid Cloud-Optimized GeoTIFF: internal tiling,
overiews, correct compression. This is what tile_pyramid.py reads from.

Also handles clipping to the AOI locally.
"""

from __future__ import annotations

from pathlib import Path

import rasterio
from rasterio.mask import mask
from rasterio.warp import transform_bounds
from rio_cogeo.cogeo import cog_translate
from rio_cogeo.profiles import cog_profiles


def clip_to_bbox(
    src_path: str | Path, bbox: tuple[float, float, float, float], dst_path: str | Path
) -> Path:
    """Clip a raster to a bbox given in WSG84 and save as a COG - the same
    lon/lat convention as config.AOI_BBOX."""
    dst_path = Path(dst_path)
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    west, south, east, north = bbox

    with rasterio.open(src_path) as src:
        if src.crs is not None and src.crs.to_epsg() != 4326:
            west, south, east, north = transform_bounds(
                "EPSG:4326", src.crs, west, south, east, north
            )

        geom = [
            {
                "type": "Polygon",
                "coordinates": [
                    [
                        [west, south],
                        [east, south],
                        [east, north],
                        [west, north],
                        [west, south],
                    ]
                ],
            }
        ]

        out_image, out_transform = mask(src, geom, crop=True)
        out_meta = src.meta.copy()
        out_meta.update(
            {
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform,
            }
        )

        with rasterio.open(dst_path, "w", **out_meta) as dst:
            dst.write(out_image)

    return dst_path


def to_cog(
    src_path: str | Path, dst_path: str | Path, profile: str = "deflate"
) -> Path:
    dst_path = Path(dst_path)
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    output_profile = cog_profiles.get(profile)
    cog_translate(
        str(src_path),
        str(dst_path),
        output_profile,
        add_mask=True,
        in_memory=False,
        quiet=False,
    )
    return dst_path
