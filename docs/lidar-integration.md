# NC LiDAR terrain integration

Implemented on `app-lidar`, branched directly from `app` (`5c541da`). The requested scope is anywhere in North Carolina, both hillshade and slope, using a public source. The app remains plain HTML/JavaScript with the existing Leaflet library and historical WMS layer.

## Verified sources (2026-10-12)

NC OneMap offers matching LiDAR-derived raster products:

- [DEM03 hillshade service](https://services.nconemap.gov/secure/rest/services/Elevation/DEM03_hillshade/ImageServer) and [provenance](https://services.nconemap.gov/secure/rest/services/Elevation/DEM03_hillshade/ImageServer/info/iteminfo): elevation-derived shaded terrain from NC Floodplain Mapping Program LiDAR processed by NC Emergency Management.
- [DEM03 slope service](https://services.nconemap.gov/secure/rest/services/Elevation/DEM03_slope/ImageServer) and [units](https://services.nconemap.gov/secure/rest/services/Elevation/DEM03_slope/ImageServer/info/iteminfo): slope in degrees. Its [legend](https://services.nconemap.gov/secure/rest/services/Elevation/DEM03_slope/ImageServer/legend?f=pjson) runs from 0 to 90 degrees; the original swatches are embedded in the public configuration, without recoloring or inventing thresholds.

The catalog describes a 3-foot DEM. Both service pixel grids report 3.125 US survey feet, approximately 0.95 m, in NAD83(2011) North Carolina State Plane feet. This is a source cell size, not an accuracy guarantee. The returned map is server-resampled for the requested view. Acquisition date is not supplied in the top-level metadata checked here; do not label it current or assume one acquisition date statewide. Data availability and quality may vary across the state.

USGS 3DEP was also inspected, but its multi-resolution DEM service was not needed because NC offers both requested products from the same DEM family. There is no silent fallback to a different resolution or source.

## Rendering and controls

`terrain-layer.js` subclasses Leaflet's tile layer only to construct [ArcGIS exportImage requests](https://developers.arcgis.com/rest/services-reference/enterprise/export-image/). It derives square Web Mercator BBOX coordinates from the Leaflet tile grid and explicitly sends `bboxSR=3857`, `imageSR=3857`, `size=512,512`, `format=png32`, `f=image` and bilinear interpolation. The server handles reprojection from its native CRS. Ordinary image requests use trusted HTTPS with no credentials or CORS-dependent browser fetch.

At zoom levels below 12 or outside the configured NC envelope, terrain requests are suspended and the interface explains how to return to coverage/detail. The rectangular coverage bound is a request envelope, not a guarantee that every pixel has data. Terrain can be displayed through zoom 19. Raster requests occur as the user pans/zooms; no full-state raster download or local LiDAR processing is needed.

Draw order: basemap (1), terrain (2), historical map (3). Terrain and historical opacities are independent. The app starts with hillshade at the Eno River public example and historical visibility off. Historical tiles retain a maximum native zoom of 12; higher zooms resample those existing pixels rather than suggesting newly precise historical registration. The USGS basemap similarly resamples beyond its supported native zoom.

The source and slope legend remain visible on the map. Terrain failure/loading messages are independent of basemap/historical status; Retry recreates active layers. Turning terrain off removes its tiles/legend but retains the basemap. The original approximate historical-alignment notice remains visible.

## Interpretation

Hillshade can help inspect terrain form and possible approaches. Slope provides gradient context; its 0–90 degree legend is not a classification of crossing suitability. Water, flattened surfaces, bridges, vegetation filtering artifacts, later earthworks, erosion and dataset age can complicate interpretation. Modern terrain cannot determine an historical crossing or channel depth. Public river examples are navigation aids only; no crossing candidates are inferred, marked or saved.

No research archive, sensitive site data, network drive, database credential, server setting or GeoServer security configuration was accessed or changed for this view.

## Validation and deployment

The browser suite `scripts/test_terrain.cjs` checks real PNG images at public river examples, the slope legend, independent opacity, historical/terrain ordering, detailed zoom/pan requests, statewide navigation, terrain-off behavior, outage/retry recovery and mobile layout. `scripts/test_viewer.cjs` checks the retained historical-map and basemap controls. Live responses are checked for status, image format, HTTPS and projected BBOX consistency. Screenshots are visually inspected; this validates display, not historical correspondence or terrain accuracy.

Build with `python3 scripts/package_demo.py`; output is `publish/app-lidar/`. No raw rasters, proof-of-concept point data or archive material enter this allowlisted payload. If hosting uses a restrictive Content Security Policy, permit image requests to `https://services.nconemap.gov`, the existing GeoServer/OSM/USGS origins, and `data:` for the embedded provider legend. Validate again from the deployed origin. No deployment or push is performed as part of this implementation.

Final validation: the terrain suite passed with 84 successful live terrain responses; the retained viewer suite passed with 81 WMS responses. Script syntax, package hashes/links/source parity, image-content checks and Git whitespace checks also passed. See `lidar-verification.json` and `lidar-sources.json`. Local screenshots are preserved in the ignored `deliverables/lidar-preview/` folder.
