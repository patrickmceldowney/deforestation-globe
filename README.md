# deforestation-globe

Ecological change monitoring on a 3D globe. Planet imagery -> Python processing pipeline -> static tile pyramids -> Cesium globe with a timeline slider and layer toggles (satellite / NDVI / forest-loss)

## How it fits together
```
Planet API (Orders/Data, PSScene, ARPS)
      |
      v     
pipeline/
      |
      v
object storage
      |
      v
web/             
```

There is deliberatly no live tile server in v1. Tiles are rendered once, during the pipeline run, and server as static files. See the pipeline README for when that stops being true.

## Repo layout
- `pipeline/`: Python. Fetches imagery, does change detection, writes Cloud-optimized GeoTIFFs, cuts them into static tile pyramids, uploads everything to object storage.
- `web/`: Next.js. UI only. No heavy compute. Reads a manifest that describes which layers/years/AOIs exist and renders the Cesium globe.
- `data/`: local scratch space for pipeline runs. Not committeed; COGs and tiles live in object storage, not git.

## First run
1. `pipeline/` - Get one AOI, one year, one layer (RGB) end to end - see `pipeline/README.md`
2. `web/` - point Cesium at the tiles that produced, confirm it renders - see `web/README.md`
3. Only after that works, widen to more years/layers and build the real manifest + UI controls
