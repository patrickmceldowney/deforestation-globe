"use client";

import { useEffect, useRef, useState } from "react";
import * as Cesium from "cesium";
import "cesium/Build/Cesium/Widgets/widgets.css";
import {
  fetchManifest,
  tileUrlForYear,
  type Manifest,
  type LayerManifestEntry,
} from "@/lib/layers";

Cesium.Ion.defaultAccessToken = "";

export default function CesiumGlobe() {
  const containerRef = useRef<HTMLDivElement>(null);
  const viewerRef = useRef<Cesium.Viewer | null>(null);
  const layerRefs = useRef<Record<string, Cesium.ImageryLayer>>({});

  const [manifest, setManifest] = useState<Manifest | null>(null);
  const [year, setYear] = useState<number | null>(null);
  const [activeLayerIds, setActiveLayerIds] = useState<Set<string>>(new Set());

  // Load manifest once
  useEffect(() => {
    fetchManifest().then((m) => {
      setManifest(m);
      setYear(m.years[m.years.length - 1]);

      const defaultOn = m.layers.find((l) => l.id === "rgb");
      setActiveLayerIds(new Set(defaultOn ? [defaultOn.id] : []));
    });
  }, []);

  // Init viewer once
  useEffect(() => {
    if (!containerRef.current || viewerRef.current) return;

    const viewer = new Cesium.Viewer(containerRef.current, {
      baseLayerPicker: false,
      geocoder: false,
      homeButton: false,
      sceneModePicker: false,
      navigationHelpButton: false,
      timeline: false,
      animation: false,
      baseLayer: false,
    });

    viewerRef.current = viewer;

    return () => {
      viewer.destroy();
      viewerRef.current = null;
    };
  }, [containerRef]);

  // fly to AOI once we know it
  useEffect(() => {
    const viewer = viewerRef.current;
    if (!viewer || !manifest) return;

    const [west, south, east, north] = manifest.aoi.bbox;
    viewer.camera.flyTo({
      destination: Cesium.Rectangle.fromDegrees(west, south, east, north),
      duration: 1.5,
    });
  }, [manifest]);

  // Sync active layers + year to Cesium imagery layers
  useEffect(() => {
    const viewer = viewerRef.current;

    if (!viewer || !manifest || year === null) return;

    for (const layerDef of manifest.layers) {
      const shouldBeOn = activeLayerIds.has(layerDef.id);
      const existing = layerRefs.current[layerDef.id];

      if (!shouldBeOn) {
        if (existing) {
          viewer.imageryLayers.remove(existing, true);
          delete layerRefs.current[layerDef.id];
        }
        continue;
      }

      // Swap the provider on year change rather than trying to animate
      // opacity between two loaded layers
      if (existing) {
        viewer.imageryLayers.remove(existing, true);
      }

      const provider = new Cesium.UrlTemplateImageryProvider({
        url: tileUrlForYear(layerDef, year),
        minimumLevel: 8, // keep in sync with pipeline TILE_MIN_ZOOM
        maximumLevel: 15, // keep in sync with pipeline TILE_MAX_ZOOM
      });

      const newLayer = viewer.imageryLayers.addImageryProvider(provider);
      layerRefs.current[layerDef.id] = newLayer;
    }
  }, [manifest, year, activeLayerIds]);

  function toggleLayer(id: string) {
    setActiveLayerIds((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }

  return (
    <div className="relative w-full h-full">
      <div ref={containerRef} className="w-full h-full">
        {manifest && year !== null && (
          <div className="absolute top-3 right-3 bg-[rgba(20, 20, 20, 0.85)] text-white py-3 px-4 rounded-lg font-sans text-[14px] w-55 z-10">
            <div className="mb-2 font-semibold">{manifest.aoi.name}</div>

            {manifest.layers.map((layer: LayerManifestEntry) => (
              <label key={layer.id} className="mb-1 block">
                <input
                  type="checkbox"
                  checked={activeLayerIds.has(layer.id)}
                  onChange={() => toggleLayer(layer.id)}
                />{" "}
                {layer.label}
              </label>
            ))}

            <div className="mt-3">
              <input
                className="w-full"
                type="range"
                min={manifest.years[0]}
                max={manifest.years[manifest.years.length - 1]}
                step={1}
                value={year}
                onChange={(e) => setYear(Number(e.target.value))}
              />
              <div className="text-center">{year}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
