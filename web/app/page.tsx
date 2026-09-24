import CesiumGlobeClient from "./globe/CesiumGlobeClient";

export default function Home() {
  return (
    <main className="w-screen h-screen m-0">
      <CesiumGlobeClient />
    </main>
  );
}
