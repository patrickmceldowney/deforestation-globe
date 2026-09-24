"use client";

import dynamic from "next/dynamic";

const CesiumGlobe = dynamic(() => import("./CesiumGlobe"), {
  ssr: false,
});

export default function CesiumGlobeClient() {
  return <CesiumGlobe />;
}
