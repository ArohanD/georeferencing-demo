> Historical integration record. For current serving, packaging, and verification commands, use [the viewer README](../app/README.md). The former integration-branch offline controls and `publish/geoserver-demo/` package are not part of the current viewer.

# GeoServer historical-map integration

The plain HTML/JavaScript application retains Leaflet 1.9.4. There is no package.json, application framework, bundler or TypeScript step. The default view now streams Collet from GeoServer over an OpenStreetMap basemap. The original local Collet overlays, five USGS views, point/error diagnostics, review page and reports remain available. Mouzon is excluded.

**Approximate historical-map alignment. For visual comparison only; not suitable for locating routes or sites precisely.** Collet: approximately 8 km RMSE across four held-out town proxies. Moseley: approximately 20.5 km RMSE across two held-out coastal proxies. These uncertain historical correspondences are not survey-grade accuracy estimates.

## Run and configure

From the repository root:

```bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory app/public
```

Open http://localhost:8000/preview/ . The default live layers need internet. Choose **Collet 1770 · local pilot overlay** and **USGS · local reference** for offline comparison. Local reference imagery covers only the selected view. The proxy points refer to Collet, not Moseley.

`app/public/preview/map-config.js` centralizes the HTTPS WMS endpoint, exact layer names, WMS version, format, bounds, attribution, publication flags, basemap and loading timeout. There are **no application environment variables** or secrets. `data/points/preview.json` retains the original local-view/proxy data. Bounds and historical credits were copied from `data/historical_maps/integration-manifest.json`; that older processing manifest's pending publication fields are not the live service authority.

The viewer uses `L.tileLayer.wms`, WMS 1.1.1, EPSG:3857, PNG with transparency and an empty styles parameter (server default). Leaflet generates new meter-based BBOX requests on pan/zoom. Both basemap and historical layers use Web Mercator. Raster-envelope bounds include transparent margins; they are not surveyed boundaries. Initial view fits Collet's full bounds. Visibility, opacity, fit and retry controls do not require a page reload.

Layer failures and a 20-second loading timeout leave the rest of the application usable. Retry imagery or select the local layers. Failure to fetch local proxy data does not block live WMS. Moseley's availability is an explicitly verified configuration flag, not a browser capabilities fetch; update it after publication and image verification.

## Live verification — 2026-10-12

See `geoserver-verification.json` for the capabilities summary, formats, advertised URLs, bounds and response hashes.

- Endpoint: `https://vclvm176-164.vclgis.cnr.ncsu.edu/geoserver/history/wms`.
- WMS 1.3.0 GetCapabilities: HTTP 200, update sequence 317. Workspace-scoped capabilities advertise the local name `collet_1770`; qualified `history:collet_1770` successfully rendered via GetMap.
- Explicit Collet CRS entries: EPSG:3857 and CRS:84. The parent also advertises inherited CRS support including EPSG:4326. PNG, JPEG, GIF, TIFF/GeoTIFF and other formats are listed; the integration uses PNG.
- Advertised operation URLs use trusted HTTPS at `https://vclvm176-164.vclgis.cnr.ncsu.edu/geoserver/history/ows?SERVICE=WMS&`.
- A 1000 × 578 PNG GetMap covering the manifest's EPSG:3857 extent returned actual Collet imagery, inspected visually. Browser tiles also rendered above OSM. This checks rendering and broad regional placement, not geographic accuracy.
- Moseley is absent from capabilities. A direct `history:moseley_1733` GetMap returned an XML `LayerNotDefined` exception inside HTTP 200. It is disabled in the selector, with bounds and attribution ready.
- Chromium loaded live imagery with normal certificate validation. No credentials, authentication redirects, HTTP image URLs, mixed-content errors or CORS failures were observed. Ordinary cross-origin image tiles do not require CORS-enabled fetches. The server did not advertise an Access-Control-Allow-Origin header on capabilities; this viewer does not fetch capabilities in the browser or export pixels to canvas.

## Validation results

Source and generated-package Chromium suites both passed, each observing 63 successful live PNG WMS responses. Visibility, opacity, pan/zoom, all five local views, proxy controls, unavailable Moseley, server outage/retry, missing local data, slow-response timeout and mobile layout passed. JavaScript syntax checks, the existing 47-input provenance/numeric/COG audit, Git whitespace checks, and package checksums/local HTML links passed. The static artifact contains 83 files (36.37 MiB). See `browser-verification.json` for the recorded test results. Local screenshots are in `deliverables/geoserver-integration/` (ignored; not part of the deployment payload).

No browser verification was performed from a deployed HTTPS application origin; that remains a post-deployment check. No code/build blocker remains for Collet. Moseley publication is the remaining layer-specific blocker.

## Repeat verification

Syntax and existing raster/local-asset verification:

```bash
node --check app/public/preview/app.js
node --check app/public/preview/map-config.js
.venv313/bin/python tools/processing/verify.py
```

The existing audit checks provenance, numeric diagnostics, COG validity and local links; it does not run a browser. Browser tests are separate and require live GeoServer/OSM access. Install test-only tooling outside the project:

```bash
npm install --prefix /tmp/georef-browser --no-audit --no-fund playwright
PLAYWRIGHT_BROWSERS_PATH=/tmp/georef-browser/browsers /tmp/georef-browser/node_modules/.bin/playwright install chromium
NODE_PATH=/tmp/georef-browser/node_modules PLAYWRIGHT_BROWSERS_PATH=/tmp/georef-browser/browsers node app/scripts/test_viewer.cjs
```

Keep the localhost server running. The test checks real PNG tile responses, visibility, opacity, new zoom/pan requests, all local views, point controls, attribution, disabled Moseley, missing local data, simulated server failure, retry, loading timeout and mobile width. Screenshots and a JSON result are written to `/tmp/georef-validation`. Optional positional arguments set the viewer URL and evidence output directory. The two shell variables above configure the test tools only.

## Build and deployment preparation

The existing GitHub `main` history contains a static display package, including a root redirect and `.nojekyll`; no deployment workflow was found. The local folder additionally contains processing assets and local changes. Git was restored from `origin/main` without checking out or overwriting working files, then branch `feat/geoserver-historical-maps` was created. Pre-existing differences, including missing root deployment files, remain preserved. Do not publish the entire working folder or indiscriminately stage its untracked files.

Build with the existing allowlisted packager, now targeting a separate ignored directory:

```bash
python3 app/scripts/package_demo.py
python3 -m http.server 8001 --bind 127.0.0.1 --directory publish/geoserver-demo
```

Open http://localhost:8001/ . The package includes the new configuration, live viewer, original local comparison assets, root redirect, generated report HTML, `.nojekyll` and a checksummed `PUBLICATION-MANIFEST.json`. No GeoTIFFs, original scans, research archive, credentials, database settings or Python environment are needed. The packager checks unexpected files and credential patterns in the permitted payload. It preserves other existing `publish/` contents.

To test the generated package while the repository-root server is running:

```bash
NODE_PATH=/tmp/georef-browser/node_modules PLAYWRIGHT_BROWSERS_PATH=/tmp/georef-browser/browsers node app/scripts/test_viewer.cjs http://127.0.0.1:8000/publish/geoserver-demo/preview/ /tmp/georef-package-validation
```

**Next deployment step:** review the branch changes and the generated package, then obtain authorization to publish. Deploy only the contents of `publish/geoserver-demo/` to the static hosting root/project subpath. If continuing with GitHub Pages, first confirm its configured publishing branch/folder or workflow in repository Settings → Pages, and deliver this artifact to that destination. No push, commit, hosting change or deployment was performed here. `app/scripts/verify_public.py` compares the public site with this new artifact and should run only after an authorized deployment; it is not a local build test.

A host with a restrictive Content-Security-Policy must permit images from the GeoServer HTTPS origin and `https://tile.openstreetmap.org`, plus the bundled local assets. Keep HTTPS certificate validation enabled. Recheck imagery from the deployed origin, since localhost verification cannot certify a future hosting policy or future VCL availability. No IIS, firewall, GeoServer security or PostgreSQL changes were needed for Collet.

## Publish Moseley on the VCL server

Only the administrator should perform these steps; no server configuration was changed in this task.

1. In GeoServer's **Stores**, select an existing Moseley GeoTIFF store if present. Otherwise choose **Add new Store → GeoTIFF**, workspace `history`, and a descriptive store name such as `moseley_1733`.
2. Point it to `file:///C:/GIS590_adutt2/Data/HistoricalMaps/moseley_1733-approximate-web.cog.tif`. Confirm the file exists and the GeoServer service account can read it. Save the store.
3. Click **Publish** for its coverage. Set the layer name to `moseley_1733`. Confirm native and declared CRS are EPSG:3857 for this web raster. Do not label meter coordinates EPSG:4326. Compute native bounds from the data and geographic bounds from the native bounds. Enable and advertise the layer, use the default raster style, and save.
4. Check the workspace GetCapabilities and Layer Preview. Verify a transparent PNG GetMap with `layers=history:moseley_1733`, `srs=EPSG:3857`, WMS 1.1.1 and bounds approximately `-8963241.943041157,3857757.7715218626,-8325116.943041157,4396007.771521863`. Check actual imagery, not just HTTP 200.
5. After verification, set Moseley's `available` to `true` in `app/public/preview/map-config.js`, change its label to `Moseley 1733 · live GeoServer`, update `checkedOn`, and rerun imagery/browser checks and the static build. Keep its accuracy disclaimer and ECU attribution.

The store/coverage workflow is documented in GeoServer's [GeoTIFF publishing guide](https://docs.geoserver.org/main/en/user/gettingstarted/image-quickstart/); CRS, bounding-box and enabled/advertised options are described in its [Layers documentation](https://docs.geoserver.org/stable/en/user/data/webadmin/layers/).
