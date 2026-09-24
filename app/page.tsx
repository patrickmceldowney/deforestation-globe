"use client";

import Globe from "@/components/Globe";

export default function Home() {

  return (
    <main className="relative h-screen w-screen">
      <Globe />

      {/*<div className="absolute bottom-8 left-1/2 w-3/4 -translate-x-1/2">
        <Timeline year={year} onYearChange={setYear} />
      </div>*/}
    </main>
  );
}
