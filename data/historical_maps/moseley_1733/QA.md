# Moseley 1733 — approximate only

The completed raster package is technically ready for a **clearly labeled approximate preview** in GeoServer. It is not defensible as a validated historical registration. Four coastal proxies support a single affine placement; two geographically separated coastal checks reserved before fitting expose large errors. No interior accuracy estimate exists.

| Metric in EPSG:32119 meters | Result |
|---|---:|
| Fitting points | 4 |
| Fit RMSE | 3,196.58 m |
| Largest fit residual | 5,053.73 m |
| Independent diagnostic checks | 2 |
| Check RMSE | 20,454.52 m |
| Roanoke Island north-tip check | 12,183.09 m |
| Winyah Bay inlet-mouth check | 26,236.37 m |

The held-out checks were never fitted or used to choose a transformation. They are shoreline proxies subject to migration, generalization and different mouth definitions, so their discrepancies are **not survey-grade accuracy measurements**. Small fit residuals would not validate this map. Second-order polynomial and TPS were not attempted because the number, reliability and distribution of controls do not support them. No adjustment was made after inspecting checkpoint errors.

The ECU cartouche was visually checked and reads **1733**; the full scan and edition crop are retained. The finding aid now leads to an aggregate item with newer scan 62315 and older six-scan mosaic 51135. Native 15000-wide requests returned 504 twice; the practical 10000 × 7918 full-frame image succeeded. This is an institutional full-image derivative, not a screenshot. Its embedded JPEG compression is preserved in the original; subsequent raster compression is lossless. Visible folds, tonal variation and sheet seams remain. Source metadata distinguishes the original map date from the unknown digitization date and excludes the distinct 1737 map.

Manual inspection used labeled historical capes and a river confluence, compared with USGS The National Map exports. `points.csv` preserves original image coordinates, reference image coordinates, actual returned modern extents via evidence URLs, confidence and the frozen split. `selection.json` documents pixel conventions, preview-to-original conversion and rejected candidate types. Broad channel or shoreline positions are approximate visual selections, not surveyed monuments. Annotated original-resolution historical crops and corresponding marked modern views allow review of all six choices. The QGIS point file uses negative image Y, EPSG:4326 map coordinates and disables the checks.

The master is EPSG:32119 at 100 m pixels; the serving derivative is EPSG:3857 at 125 m pixels. These resolutions retain regional label readability at practical output sizes and do not indicate positional accuracy. Rasterio/GDAL write tiled DEFLATE COGs with internal overviews and RGBA. The mask removes neatline margins and the entire inset strip, retaining a conservative southwest mainland strip; some main-map ocean/title-area context is deliberately trimmed. The original preserves all insets. No white-color key is used, so legitimate white map content remains opaque. Output bounding rectangles include transparent margins; they are not geographic truth for historical features.

Both COGs passed strict structural validation, open with explicit CRS, contain nonconstant RGB pixels, and have alpha outside the main footprint. Full-extent and detailed overlay previews were visually inspected: orientation is correct, the coast lies in the expected region, and substantial historical/modern differences remain. This confirms packaging and broad placement, not accuracy. The full extent overlay covers the actual output bounds. Detail previews cover Cape Fear, Neuse/Trent and Cape Lookout, northeast coast, Winyah Bay, and Eno–Haw/Hillsborough.

**Eno–Haw / Hillsborough is an inspection area only.** It falls outside the coastal control envelope. The preview reveals gross mismatch between historical upper drainage and modern rivers; the historical Virginia-border/upper drainage is displaced into this area. No route or settlement inference should be drawn from that apparent overlap. The west, northwest and edges are unsupported extrapolation, and the southeast ocean has no independent control. Winyah Bay is a particularly poor fit.

Human review should first assess whether the selected coastal proxies represent comparable geometry at all. Compare `M01`–`M06` historical and modern images; M06 is especially ambiguous because modern jetties and historical barrier islands change the inlet-mouth definition. Then establish independently supported interior river correspondences, researching dams, historical names and channel changes before replacing this attempt. Existing checks are already exposed and should not be repeatedly used to tune a replacement. Reserve new checks for any revised fit.

Rectification does not establish the accuracy of historical paths, routes, settlements or other locations. Historical paths remain evidence of historical cartography. Publication workspace and service URL remain pending; no server was modified.
