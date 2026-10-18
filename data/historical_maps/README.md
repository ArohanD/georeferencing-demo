# Listening Machine historical-map deliverables

These outputs are for review before GeoServer publication. Read each map's QA report and status. **A technically valid GeoTIFF is not evidence of accurate historical positions.** Rectification does not establish accuracy of historical routes or locations. The Eno–Haw/Hillsborough area is an inspection area only; no Trading Path Association research corridor has been selected.

## Environment and repository inspection

Workspace: `/home/arohan/code/georef` on WSL's Linux filesystem, not `/mnt/c`. Heavy work and final ignored outputs are under `/home/arohan/code/georef/deliverables/`. The existing project is a standalone Python raster-processing pilot and a plain HTML/JavaScript Leaflet 1.9.4 viewer (`apps/viewer/public/`), with no package.json or application framework found. Historical configuration is `data/points/preview.json` plus `apps/viewer/public/preview/app.js`: pre-rendered image overlays, view bounds and eight fitted/four held-out town proxies. Those are not ground truth. Existing Collet scan, point snapshots and pilot outputs were preserved; scripts under `tools/processing/georeferencing/` create new outputs.

The original processing run occurred in a mounted environment without usable Git metadata. The current repository is organized as a monorepo; see the root README for current paths. Original scans and generated rasters remain ignored.

Existing isolated Linux environment `.venv313/` was reused. No Windows or ArcGIS Python was touched. Versions are recorded in `environment.json`, with the existing pinned `tools/processing/requirements.lock.txt`. Rasterio's bundled GDAL is used consistently rather than mixing it with the separately installed GDAL CLI. Initial free space was 912 GB and available RAM about 28 GB; bounded raster jobs used 1–2 processing threads and modest GDAL caches. No LFS or public application assets were added.

## Reproduction

From repository root, use the existing environment or create a Python 3.13 virtual environment and install the pinned binary wheels in `tools/processing/requirements.lock.txt`. Do not run the old pilot scripts merely to regenerate these new deliverables: some old scripts overwrite the pilot's review data and research outputs.

```bash
# Only needed if preserved original Collet input snapshots are absent:
bash tools/processing/fetch_sources.sh

# New outputs; initial downloads/uncached reference exports require internet.
.venv313/bin/python tools/processing/georeferencing/collet.py
.venv313/bin/python tools/processing/georeferencing/collet_evidence_packet.py
.venv313/bin/python tools/processing/georeferencing/mouzon_1775.py --fetch
.venv313/bin/python tools/processing/georeferencing/moseley_1733.py --fetch

# Consolidate packaging and independently inspect generated rasters:
.venv313/bin/python tools/processing/georeferencing/build_catalog.py
.venv313/bin/python tools/processing/georeferencing/verify.py
```

Keep the original Collet scan and `data/points/` frozen CSV snapshots. Collet's cached modern exports under `data/reference/` are preserved dependencies. Its additional exports are cached under `deliverables/collet_1770/`. New institutional scans and modern reference images are in each map's ignored deliverables directory. Download URLs, actual returned reference extents, checksums, raster bounds and model settings are recorded. Retain caches for exact reproducibility: live reference services may change. The source scan's date is distinct from its institutional digital reproduction date.

Scripts reuse completed new rasters and verify immutable source inputs; changing a model requires a versioned run and deliberate removal of only that run's outputs. Do not delete original scans or pilot assets. New control/check splits must be chosen before fitting a revised model; inspected old checks cannot be repeatedly reused to select transformations.

Open `deliverables/index.html` for the generated comparison index. Original-image evidence panels are linked where available. Static images use actual modern export extents, not prototype overlay bounds. A browser display test alone cannot validate map registration; the separate verification script checks raster structure, content and conversion fidelity, while per-map QA evaluates geographic evidence.

## Transfer and future Leaflet integration

The consolidated `integration-manifest.json` uses portable repository-relative paths, WGS84 raster-envelope bounds, explicit raster CRSs, suggested layer names, per-map status and pending publication fields. Raster bounds include transparent edges; they are derived from the files, not a historical survey boundary. The web files are EPSG:3857, tiled losslessly compressed RGBA GeoTIFF/COGs with internal overviews. Transfer the chosen web GeoTIFF and its metadata/QA to a directory accessible to the **Windows VCL GeoServer process**. Keep the master and original scan for preservation/reprocessing. No VCL filesystem path is known or invented.

GeoServer base: `https://vclvm176-164.vclgis.cnr.ncsu.edu/geoserver`. Workspace: **pending**. Publication: **pending**. Suggested coverage names: `collet_1770`, `mouzon_1775`, `moseley_1733`. No service URL is claimed to work. WSL localhost is only a local review host and has no relationship to the VCL service.

After a human chooses a workspace and publishes the GeoTIFF coverages, the existing Leaflet layer-switching logic can use `L.tileLayer.wms` with that base's WMS endpoint, the actual `workspace:layer` name, PNG and `transparent: true`. Leaflet's standard EPSG:3857 map matches the web raster CRS. Keep existing image overlays until actual GetCapabilities/GetMap requests succeed; do not paste pending placeholders into live configuration. Use bounds as `[[south, west], [north, east]]` when fitting a Leaflet view. Preserve attribution and visible approximate/provisional status beside the layer selector. This task does not change the application, configure IIS/GeoServer, publish, deploy, or request credentials.

## Human review

Collet's natural-feature packet identifies exact ambiguities at Haw–Deep, Trent–Neuse, the inundated Haw–New Hope junction and possible Yadkin–Uwharrie. Mouzon's graticule assumptions and feature candidates require modern controls before geographic validation. Moseley's coastal proxies cannot establish interior accuracy. Use source-image crops and authoritative modern/pre-impoundment evidence to decide homologous locations; do not substitute town centroids, reservoir margins or plausible modern roads. More points alone do not improve a model if their identities are weak.
