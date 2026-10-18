# Collet 1770: feasibility verdict

**A useful regional demonstration is possible, but this result remains provisional.** The pilot delivers an actual affine georeferencing attempt, a validated COG, a portable offline preview and an auditable control table. It does not establish settlement-level historical positions. Treat roughly **1:1,000,000 to 1:2,000,000** as an exploratory viewing range, not a certified accuracy scale; an 8 km error remains conspicuous even there. Do not infer precision from 100 m output pixels. Detail views deliberately expose misalignment.

## Evidence and what was tested

Used the Library of Congress **Copy 1** of John Collet's *A compleat map of North-Carolina from an actual survey*, published by S. Hooper in London, 1770. The complete 13,949 × 9,524 JP2 is preserved, with checksum and download URL in `data/metadata/source.json`. LOC catalogs a 1770 map rather than a later reproduction; this pilot downloaded its full-dimension service derivative, not its TIFF master. UNC's supplied UUIDs returned access-app shells; neither identity was verified. NCpedia independently points to UNC's legacy Collet record `ncmaps/467`. Mouzon fallback was unnecessary. Other ArcGIS resources describe other maps, not independent Collet ground truth.

The entire image and enlarged regional crops were visually inspected, followed by individual original-pixel crops. Coverage extends from coastal NC to the western Piedmont/Blue Ridge edge, with parts of Virginia and South Carolina. North is approximately up. There is a pronounced central join/fold, minor paper discoloration, margins and decorative material; no separate geographical inset was identified. The lower-right dedication cartouche and marginal scale/borders are conservatively masked; the complete image remains untouched. Some adjacent ocean/marginal geography is deliberately lost to the mask.

The actual upper-left inscription reads **82°19′ west longitude from London** and **6 degrees of longitude from Currituck Inlet**. The border has historical degree/minute subdivisions. This establishes printed conventions, not a WGS84 conversion: the historical London reference, survey error and the old inlet's position would still need investigation. No graticule coordinate was used in fitting. See `outputs/crop-legend.jpg`.

Sixteen candidates were recorded: **8 fit, 4 check, 4 excluded**. Twelve are generalized town symbols matched to sourced USGS GNIS populated-place coordinates (NAD83, EPSG:4269), not municipal centroids or map-label positions. Historic-core evidence is summarized in `reference-research.md`; it supports identities but does not turn GNIS proxies into surveyed colonial landmarks. Confidence is therefore medium in identity and low-to-medium in exact position. Bethania/Salem have distinct symbols and GNIS records; other towns with the same names were avoided. Brunswick Town and Cross Creek remain excluded pending specific historical matches. The Haw–Deep junction was investigated as a potential natural anchor but neither a defensible exact pixel nor historical channel equivalence was established; no coordinate was fabricated. Current inlets and shorelines were not treated as unchanged.

The fitting/check split was fixed before first fitting and has not been tuned. One unweighted least-squares affine model was fitted in **EPSG:32119 (NAD83 / North Carolina, metres)**. A polynomial or TPS was not justified by the quantity of exact anchors or the uneven distribution. An affine has constant deformation and no local folds. Its singular scales are about 51.27 and 44.05 metres per original pixel (ratio 1.164); this captures image-to-ground scale differences, not independently measured map distortion. Mask adjustments for decoration did not change the transformation or point errors.

## Error and spatial coverage

| Measurement | Sample | RMSE | Median | Maximum |
|---|---:|---:|---:|---:|
| Fitting residuals | 8 towns | 6.84 km | 4.53 km | 13.73 km |
| Held-out positional discrepancies | 4 towns | 8.02 km | 5.53 km | 13.08 km |

| Independent town proxy | Region | Error |
|---|---|---:|
| Salem | western Piedmont, near Bethania fitting point | 1.34 km |
| Tarboro | inland coastal plain | 8.96 km |
| Hertford | northeast, near Edenton fitting point | 2.11 km |
| Bath | Pamlico region | 13.08 km |

These four are independent of **model fitting**, not independent surveys of 1770 ground positions. They share GNIS methodology and map-symbol generalization; Salem and Hertford are close to fitting towns. No southern, far-western or Outer Banks independent check was established. This small, nonrandom sample cannot establish a mapwide accuracy confidence interval. Errors include reference-proxy ambiguity, manual selection and historical cartographic error. Town symbols span many scan pixels; exact buildings are unresolved.

Bath is displaced mostly east (~12.84 km east, 2.50 km north); Tarboro mostly south (~7.99 km south, 4.05 km west). Salem and Hertford are the relatively better checks. Among fitting points, New Bern has the largest residual (13.73 km) and Halifax is also poor (9.87 km). Low residuals at Bethania/Hillsborough/Edenton are fitting evidence only. These statements concern sampled town vicinity, not all rivers or roads between them.

Static overview and four detail comparisons were generated against saved USGS Topo exports. USGS returned extents, including aspect-ratio adjustments, are used exactly. The browser shows the fitting hull: western mountains, large portions of South Carolina, Outer Banks and southernmost coast are extrapolation or weakly constrained. The coast and Cape Fear detail visibly diverge in places; river and shore migration plus historical surveying prevent treating discrepancies as a single correction field. No new anchors were inserted to force a match. Uniform affine warping cannot correct all local differences, and this pilot has not measured each river or coastal segment.

## Technical result and repeatability

The raster is a **7,390 × 4,271, four-band RGBA COG**, EPSG:32119, 100 m grid, DEFLATE compression, 512-pixel tiles and 2/4/8/16 overviews. Source reduction uses Lanczos, warp uses bilinear resampling, overviews use average; explicit alpha excludes margins/cartouche and exterior. Black is not a nodata value. The 100 m grid is approximately twice native fitted scan spacing and suitable for regional display, not a positional accuracy promise. `outputs/cog-validation.json` records strict rio-cogeo validation with no warnings/errors plus CRS, alpha and overview checks. This verifies packaging, not historical accuracy.

Another MGIST student needs this directory (especially immutable input snapshots), Python 3.13, the pinned binary-wheel environment, and the README commands. No proprietary license, system GDAL build, or ArcGIS installation is needed. Processing is offline; only initial package/source downloads require internet. The local viewer vendors Leaflet and uses saved reference exports. Exact inputs, versions, affine coefficients, pixel convention, mask, separate error rows and selection hashes are included. The current viewer JavaScript and local asset delivery were checked; no interactive browser engine was available for a full UI smoke test. Static rendered comparisons were visually inspected.

## Human review and hosting

Additional human matching could materially improve confidence and perhaps registration, but better controls cannot guarantee removal of the original map's errors. Prioritize colonial-core matches at Bath and New Bern; resolve Brunswick Town ruins and Cross Creek/Campbellton; then seek southern and western anchors and defensible river junctions. `research/review.html` is one consolidated request with annotated original-image crops, modern GNIS-centered views, coordinates and a decision for each point. Edit `data/points/review.csv`. The original columns remain baseline evidence; correction fields require CRS and citation. Because the held-out errors are now visible, **reserve fresh checks for any revised model**; the existing four then become diagnostic points.

For public hosting, first decide whether a clearly labeled regional interpretive layer is sufficient or whether better control evidence is required. Retain attribution, version/provenance, uncertainty and explicit exclusions. Then choose a portable tile service or configure COG range requests/CORS and browser rendering; if using ArcGIS Enterprise, verify its support for this CRS, alpha and overviews and generate a suitable service/cache. Review basemap hosting/reuse requirements independently; local saved USGS exports are a pilot convenience. Add accessibility/mobile browser testing and protect against users interpreting zoom as accuracy. No public deployment, paid resource, or Enterprise server change was performed.
