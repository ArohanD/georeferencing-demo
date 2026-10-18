# The Listening Machine — historical maps and LiDAR terrain

The `app` branch includes public North Carolina LiDAR-derived **hillshade and slope**, streamed from NC OneMap. It opens at a labeled public Eno River example with LiDAR off by default; pan anywhere in North Carolina or use Explore → North Carolina overview. The other public examples cover the French Broad, Haw and Neuse rivers. These are navigation examples, not proposed historical crossings.

All commands below run from the repository root.

## Use

```bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory apps/viewer/public
```

Open http://localhost:8000/ . Live imagery requires internet.

- **Terrain:** choose NC LiDAR hillshade, NC LiDAR slope, or Off. No terrain imagery is requested until you enable a terrain layer. Terrain opacity blends it with the selected basemap. Slope includes the provider's legend in degrees.
- **Explore:** navigate to the state overview or public river examples. **Inspect here** zooms the current center to detail. Terrain loads at zoom 5–19, including statewide views. Overview images show broad terrain; zoom in to examine banks and approaches. Requests remain fixed at 512 × 512 pixels per tile.
- **Historical layer / Show historical / Opacity:** compare Collet 1770, Wimble 1738, or Bowen 1747 (coastal NC excerpt) with the terrain independently. Historical imagery starts hidden to make terrain legible. **Fit** returns to the historical map extent. Moseley remains unavailable pending GeoServer publication.
- **Basemap:** OpenStreetMap, USGS Topographic, or None. **Retry** reloads active imagery after service errors.

For crossing research, start with hillshade to examine channel form, banks, terraces and possible approaches; switch to slope to compare gradients. Lower terrain opacity to locate named rivers on the basemap. Modern topography alone does not establish historical crossings or water depth. Acquisition age, erosion, engineering works and water treatment affect interpretation. Transparent gaps indicate absent coverage, not flat ground.

Approximate historical-map alignment. For visual comparison only; not suitable for locating routes or sites precisely. Collet's approximately 8 km, Moseley's 20.5 km, Wimble's 21.3 km, and Bowen's 13.9 km RMSE are uncertain historical proxy diagnostics, not survey-grade accuracy estimates. Wimble and Bowen use three held-out cape proxies each; shoreline changes add uncertainty. ECU's Wimble reproduction is marked for educational use; its rights link is retained in map attribution.

## Sources and configuration

See [LiDAR sources and verification](../../docs/lidar-integration.md). NC OneMap describes these products as derived from a 3-foot LiDAR DEM; the service reports a 3.125 US survey-foot pixel grid (about 0.95 m). Zooming closer does not improve the source resolution. This app displays derived raster terrain, not a raw 3D point cloud.

Public endpoints, bounds, source credits, example views and display options are in `apps/viewer/public/preview/map-config.js`. Leaflet 1.9.4 and its license remain bundled. `apps/viewer/public/preview/terrain-layer.js` requests projected PNG imagery from the provider; no framework, dependency, API key, database or app environment variable was added. No private research data is loaded or published.

## Build

```bash
python3 apps/viewer/scripts/package_demo.py
python3 -m http.server 8001 --bind 127.0.0.1 --directory publish/app-lidar
```

Review http://localhost:8001/ . Only `publish/app-lidar/` is the deployment artifact; it contains nine app/assets files plus a checksummed manifest. Other local processing/archive files are excluded. Nothing is pushed or published by these commands. The build includes the two published colonial map configurations.

## Verify

```bash
node --check apps/viewer/public/preview/app.js
node --check apps/viewer/public/preview/map-config.js
node --check apps/viewer/public/preview/terrain-layer.js
npm install --prefix /tmp/georef-browser --no-audit --no-fund playwright
PLAYWRIGHT_BROWSERS_PATH=/tmp/georef-browser/browsers /tmp/georef-browser/node_modules/.bin/playwright install chromium
NODE_PATH=/tmp/georef-browser/node_modules PLAYWRIGHT_BROWSERS_PATH=/tmp/georef-browser/browsers node apps/viewer/scripts/test_terrain.cjs
NODE_PATH=/tmp/georef-browser/node_modules PLAYWRIGHT_BROWSERS_PATH=/tmp/georef-browser/browsers node apps/viewer/scripts/test_viewer.cjs
```

Keep the localhost server running. Optional test arguments are the viewer URL and evidence output directory. Test-only shell variables configure Playwright; the app itself needs none. Tests cover actual imagery, Web Mercator tile extents, terrain/source selection, opacity, historical comparison, regional examples, pan/zoom, loading/errors/retry, and mobile layout. Results and screenshots go under `/tmp/georef-lidar-validation` for terrain, and the original viewer suite's configured output directory.

The [original GeoServer notes](../../docs/geoserver-integration.md#publish-moseley-on-the-vcl-server) retain Moseley's publication steps. Their older local-comparison/build descriptions apply to the integration branch.
