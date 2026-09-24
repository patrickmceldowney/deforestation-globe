# web

Next.js UI. No heavy compute here - reads `manifest/json` (produced by the pipeline,
fetched from object storage or copied locally for dev) and renders a Cesium globe
with layer toggles + a year slider.

## Setup

```bash
cd web
npm install
```

Cesium needs its static asset files (workers, images) available at runtime. `next.config.js` in this
project copies them into `public/cesium` at build time via `copy-webpack-plugin`. If you switch to
turbopack and hit issues with Cesium not loading, fall back to Webpack mode for dev rather than
fighting the asset copying.

## Local dev with a manifest

For local development before you have real tiles in a bucket:

1. Run the pipeline once (see `pipeline/README.md`) to produce `data/output/manifest.json` and a small tile set.
2. Point `NEXT_PUBLIC_MANIFEST_URL` in `.env.local` at either:

- a local static copy (`cp -r ../data/output public/data` and use `/data/manifest.json`), or
- the real public URL once tiles are uploaded to R2/S3

## Key files

- `lib/layers.ts` - fetches and types the manifest; this is the only file that needs to change if the manifest shape changes.
- `app/globe/CesiumGlobe.tsx` - the actual globe, imagery layers, and timeline slider wiring.
- `app/page.tsx` - thin page shell
