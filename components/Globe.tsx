"use client";

import { useEffect, useRef } from "react";

export default function Globe() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let viewer: import("cesium").Viewer | undefined;
    let cancelled = false;

    async function init() {
      window.CESIUM_BASE_URL = "/_next/static/Cesium/";

      const { Viewer, Ion } = await import("cesium");

      if (cancelled || !containerRef.current) return;

      Ion.defaultAccessToken =
        process.env.NEXT_PUBLIC_CESIUM_ION_TOKEN ?? "";

      viewer = new Viewer(containerRef.current, {
        animation: false,
        timeline: false,
        baseLayerPicker: false,
        geocoder: false,
        homeButton: false,
        navigationHelpButton: false,
        sceneModePicker: false,
      });
    }

    init();

    return () => {
      cancelled = true;

      if (viewer && !viewer.isDestroyed()) {
        viewer.destroy();
      }
    };
  }, []);

  return <div ref={containerRef} className="h-full w-full" />;
}
