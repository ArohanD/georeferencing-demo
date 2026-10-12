# The Listening Machine — map app

The `app` branch is the minimal GIS590 historical-map viewer: a full-height Leaflet map with **Layer, Opacity, Retry, Fit, Show, and Basemap** controls. Basemaps are OpenStreetMap, USGS Topographic, and None. Attribution and the approximate-alignment notice remain visible; loading/failure messages appear only when needed.

Collet streams from the NC State VCL GeoServer. Moseley remains disabled until publication is verified. No point diagnostics, local raster snapshots, reports, database connection, credentials, or research archive are loaded by the app. The complete comparison/proof-of-concept viewer is preserved on `feat/geoserver-historical-maps` at commit `46f04ac`. Older local processing files are retained on disk but excluded from the app and its deployment package.

## Run

```bash
python3 -m http.server 8000 --bind 127.0.0.1
```

Open http://localhost:8000/ . Internet is required for live imagery.

Public endpoint/layer/basemap settings are centralized in `preview/map-config.js`. No application environment variables or build dependencies are required. Leaflet 1.9.4 is bundled with its license.

## Build

```bash
python3 scripts/package_demo.py
python3 -m http.server 8001 --bind 127.0.0.1 --directory publish/app
```

Review http://localhost:8001/ . Deploy only the contents of `publish/app/` after approval; it contains the viewer, Leaflet, root redirect and a checksummed manifest. The rest of this working folder is not a deployment payload. Nothing is pushed or published by these commands.

## Check

```bash
node --check preview/app.js
node --check preview/map-config.js
npm install --prefix /tmp/georef-browser --no-audit --no-fund playwright
PLAYWRIGHT_BROWSERS_PATH=/tmp/georef-browser/browsers /tmp/georef-browser/node_modules/.bin/playwright install chromium
NODE_PATH=/tmp/georef-browser/node_modules PLAYWRIGHT_BROWSERS_PATH=/tmp/georef-browser/browsers node scripts/test_viewer.cjs
```

Keep the localhost server running. The browser suite checks live WMS PNGs, basemap switching, visibility/opacity, pan/zoom, retry/outage behavior, timeout handling and mobile layout. Its optional arguments are the viewer URL and evidence output directory. The environment variables above apply to test tooling only.

## Historical alignment and publication

Approximate historical-map alignment. For visual comparison only; not suitable for locating routes or sites precisely. Collet's approximately 8 km RMSE across four held-out town proxies and Moseley's approximately 20.5 km across two held-out coastal proxies are uncertain historical correspondences, not survey-grade accuracy estimates.

The [original integration notes](docs/geoserver-integration.md#publish-moseley-on-the-vcl-server) retain the exact Moseley publication steps and original service findings; their local-comparison/build descriptions apply to the integration branch. After publishing and verifying `history:moseley_1733`, enable it in `preview/map-config.js` and update its label. No server change is needed for Collet.
