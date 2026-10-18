# Mouzon 1775 — approximate only

This is a reproducible **initial graticule placement**, not a defensible modern geographic registration. The files are technically ready for a GeoServer GeoTIFF store, but should be presented only as an explicitly approximate historical-map preview. The one coarse independent Trent–Neuse shoreline check is displaced about **43.97 km** in EPSG:5070. Its roughly 1 km correspondence uncertainty is an assessment, not a measured uncertainty interval. One check is not spatial validation; regional RMSE and accuracy are unknown. Do not use the map for locating routes, settlements, or research-corridor boundaries.

## Source verification

Original LOC full-resolution JP2: `deliverables/mouzon_1775/original.jp2`, 17109 × 12467 RGB pixels, 38,434,242 bytes. The catalog's ~640 MB TIFF is the full-size scan master; the JP2 is the catalog’s highest-resolution JP2 variant and has much smaller acquisition/storage cost. TIFF dimensions were not separately verified. JP2 source compression may be lossy; subsequent COG compression is lossless. Catalog item 74692510 and the visible title identify Henry Mouzon; the imprint visibly reads May 30, 1775. There is no separate printed reproduction date identified. The digital scan date is unknown. LOC source metadata, rights, URL, checksum, and original dimensions are in source.json and the preserved loc-item.json.

Visual inspection confirmed North and South Carolina, parts of Georgia and western Indian frontiers. Place names and river labels are legible at full resolution. Cloth-mounted sections have conspicuous horizontal and vertical seams and fold deterioration. Two unrelated inset maps, Port Royal and Charlestown, occupy the lower right and are excluded by alpha. Insets remain in the original scan. Main-map margins are masked geometrically; legitimate white paper inside the main-map footprint is retained. The cartouche remains as original map content. No historical paths are matched to modern roads.

## Initial placement and verification

Twelve visually read printed graticule ticks give eight longitude-only and four latitude-only constraints. These are not geographic control points: a longitude tick supplies no latitude observation, and vice versa. They are recorded separately in graticule_ticks.csv rather than disguising them as complete GCPs. An affine transformation fits the two coordinate axes independently. The printed “Longitude West from London” is provisionally equated to Greenwich. The actual historical reference meridian and projection remain unestablished; the rectilinear border is treated as an affine latitude/longitude grid solely for initial placement. This uncertainty and the large independent discrepancy preclude promotion to usable georeferencing. No polynomial or TPS was attempted: there are no sufficiently distributed modern controls to justify them.

Ticks were selected from half-size image crops. CSV coordinates have already been converted to original-image pixels; (0,0) is the upper-left outer pixel corner, x increases right, y increases down. Tick-reading precision is approximately ±10 original pixels. placement.json records affine coefficients, geometry masks, and per-axis fit residuals. Component RMS residuals are 1014.90 m (longitude direction) and 206.92 m (latitude direction). These are single-axis constraints, not two-dimensional modern error vectors. Those residuals are converted to meters in a local equirectangular CRS (+proj=eqc +lat_ts=34 +lon_0=-80 +datum=WGS84 +units=m); they describe consistency of printed ticks with the assumed affine grid, **not modern positional accuracy**. Residuals are not Web Mercator distances.

The transformation was frozen before inspecting the independent modern shoreline location; it was not adjusted afterward. The historical north-bank cusp where the Trent joins the Neuse was visually selected near New Bern, and compared with the cusp visible on a cached USGS National Map export. Image coordinates, exact USGS returned extent, coordinate conversion and EPSG:5070 displacement are recorded in checkpoints.csv and review.json. The historical selected point is (13302.375, 3695.375). The modern selected pixel center is (445.5, 320.5) in a 900×700 USGS image. These represent a coarse estuarine shoreline feature, **not a town centroid**. Shore modifications and broad estuary depiction prevent treating this as a precise survey monument. The error is large enough to diagnose gross mismatch despite that uncertainty. No accepted modern fitting points exist: control_points.csv is deliberately header-only.

## Human review packet

Annotated historical crops and a marked modern image are in the deliverables directory:

- `neuse-trent-candidate-annotated.png` and `neuse-trent-modern-annotated.png`: verify that the chosen historical cusp represents the modern Trent–Neuse north-bank cusp, allowing shoreline change. This point was used only as a coarse check.
- `eno-haw-candidate-annotated.png` and `eno_haw_hillsborough-comparison.png`: the Eno/Little/Flat river network is depicted east of Hillsborough; the modern reference shows Falls Lake across the network. The exact historical junction and a pre-impoundment authoritative reference are needed before choosing a fit point. A Hillsborough town-symbol/modern-centroid shortcut was rejected.
- `coastal-inlets-candidate-annotated.png`: New River/Bogue inlet candidates were withheld because dynamic barrier-inlet geography needs independent change-history evidence.
- `graticule-review.png`: annotated overview of the initial-placement ticks. Longitude/latitude assumptions need cartographic specialist review before considering any graticule-based adjustment.

The provisional Eno–Haw/Hillsborough area is an inspection area, not a selected capstone corridor. Its river network is visible, but no local accuracy has been established. Western frontier geography, edges, coastlines, and seam-adjacent areas have no independent validation. The tick envelope surrounds much of the paper, but that does not establish geographic control over the interior. All geographic bounds describe this approximate transformation, not verified map coverage.

## Files and reproduction

From repository root:

```bash
.venv313/bin/python tools/processing/georeferencing/mouzon_1775.py --fetch
```

This fetches missing institutional sources and USGS exports, creates the source-preserving affine COG master and the EPSG:3857 derivative, renders full-extent and detail comparisons, and regenerates the review packet. Omit --fetch for offline processing once inputs are cached. Existing rasters/reference downloads are reused; original-source SHA-256 is enforced before fitting. To change fitting methodology, use a new version/output directory and reserve new independent checks; do not repeatedly tune against C01. Retain the cached USGS exports for exact reproduction because live basemaps can change.

Dependencies use the existing isolated Linux `.venv313` and `tools/processing/requirements.lock.txt`, plus shared `tools/processing/georeferencing/common.py`. No Windows or ArcGIS Python environment is changed. Versions are in environment.json. The master retains full source pixels in EPSG:4326 with the documented affine transform; it uses tiled DEFLATE compression, internal overviews and RGBA. The web derivative is EPSG:3857, 100 m pixels, tiled lossless DEFLATE with internal overviews and alpha. Its pixel size is a serving/detail choice, not positional accuracy; the original master preserves more source detail. No unnecessary full-resolution RGB copies remain. Raster dimensions, bounds, overview levels, file sizes, checksums and strict COG structural validation are in manifest.json.

Full extent and at least three local views use cached USGS National Map exports. Their actual returned extents, not assumed request extents, determine image alignment. Modern reference and 55% overlay panels permit orientation, gross displacement, seams, footprint and label inspection. GeoServer workspace and publication remain pending; no endpoint has been published. Rectification does not establish the accuracy of historical routes or locations.

Final visual QA: full extent and Eno–Haw, Albemarle, and Cape Fear comparisons were opened and inspected. North is up, labels are not mirrored, the two insets are absent, and main-map white content survives. Gross western displacement of the coast is clearly visible, consistent with the 43.97 km coarse check. This is geographic mismatch inherent to the current initial placement, not a claim that the raster is correctly registered.
