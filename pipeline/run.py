from __future__ import annotations

import click
import cog_export
import planet_client
import tile_pyramid
from config import (
    AOI_BBOX,
    AOI_NAME,
    COG_DIR,
    LAYERS,
    MANIFEST_PATH,
    PUBLIC_TILES_BASE_URL,
    RAW_DIR,
    TILE_DIR,
    TILE_MAX_ZOOM,
    TILE_MIN_ZOOM,
    YEARS,
)


@click.command()
@click.option(
    "--skip-order",
    is_flag=True,
    help="Reuse files already in data/raw/ instead of hitting Planet.",
)
@click.option(
    "--years",
    default=None,
    help="Comma-separated years to override config.YEARS, e.g. 2022,2023",
)
def main(skip_order: bool, years: str | None):
    target_years = [int(y) for y in years.split(",")] if years else YEARS

    for year in target_years:
        click.echo(f"--- {year} ---")

        if not skip_order:
            scenes = planet_client.search_scenes(AOI_BBOX, year=year)
            if not scenes:
                click.echo(f"   no scenes found for {year}, skipping.")
                continue
            item_id = scenes[0]["id"]
            order_id = planet_client.place_order(item_id, AOI_BBOX)
            click.echo(f"   order placed: {order_id}, pollilng...")
            order = planet_client.wait_for_order(order_id)
            raw_paths = planet_client.download_order(order)
        else:
            raw_paths = sorted(RAW_DIR.glob(f"*{year}*.tif"))
            if not raw_paths:
                click.echo(
                    f"   no raw files found for *{year}*.tif in data/raw/, skipping."
                )
                continue

        raw_path = raw_paths[0]

        clipped_path = COG_DIR / f"clipped_{year}.tif"
        cog_export.clip_to_bbox(raw_path, AOI_BBOX, clipped_path)

        # RGB layer: COG straight from the raw scene
        rgb_cog = COG_DIR / f"rgb_{year}.tif"
        cog_export.to_cog(raw_path, rgb_cog)

        for layer in LAYERS:
            if layer.id == "rgb":
                cog_path = rgb_cog
            else:
                # TODO: Wire real computation in once RGB is confirmed working end to end
                click.echo(
                    f"   skipping '{layer.id}' - not wired to real computation yet."
                )
                continue

            n = tile_pyramid.build_pyramid(
                str(cog_path), layer, year, TILE_DIR, TILE_MIN_ZOOM, TILE_MAX_ZOOM
            )
            click.echo(f"   {layer.id}/{year}: wrote {n} tiles.")

    tile_pyramid.write_manifest(
        MANIFEST_PATH, AOI_NAME, AOI_BBOX, LAYERS, target_years, PUBLIC_TILES_BASE_URL
    )
    click.echo(f"manifest written to {MANIFEST_PATH}")
    click.echo(f"next: python upload.py")


if __name__ == "__main__":
    main()
