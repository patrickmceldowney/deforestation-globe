/**
 * Reads manifest.json, produced by pipeline/tile_pyramid.py. This is the contract between the
 * two halves of the repo - if the manifest shape changes on the pipeline side, this is the
 * only file that should need to change here
 */
export type LayerKind = "rgb" | "singe_band_continuous" | "categorical";

export interface LayerManifestEntry {
  id: string;
  label: string;
  kind: LayerKind;
  /* Contains {year}, {z}, {x}, {y} plaeholders - swap them in per-layer */
  tileUrlTemplate: string;
}

export interface Manifest {
  aoi: {
    name: string;
    bbox: [west: number, south: number, east: number, north: number];
  };
  years: number[];
  layers: LayerManifestEntry[];
}

const MANIFEST_URL =
  process.env.NEXT_PUBLIC_MANIFEST_URL ?? "/data/manifest.json";

export async function fetchManifest(): Promise<Manifest> {
  const res = await fetch(MANIFEST_URL, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(
      `Failed to fetch manifest from ${MANIFEST_URL}: ${res.status}`,
    );
  }

  return res.json();
}

/**
 * Resolves the layer's tile URL for a given year, ready to hand to Cesium's
 * UrlTemplateImageryProvider (which fills in {z}/{x}/{y} itself)
 */
export function tileUrlForYear(
  layer: LayerManifestEntry,
  year: number,
): string {
  return layer.tileUrlTemplate.replace("{year}", year.toString());
}
