# Collet 1770 — approximate only

This dataset reproduces the existing frozen town-proxy affine experiment and packages it for GeoServer review. It is **not** a newly validated historical registration. The original source and pilot outputs are preserved. Modern GNIS populated-place coordinates do not establish the position of colonial town symbols; the legacy CSV rows remain proxies, not accepted exact geographic controls.

## Source and visual inspection

Library of Congress Copy 1, John Collet, London: S. Hooper, May 1, 1770. Preserved full-dimension institutional JP2: `data/original/collet-1770-loc-copy1.jp2`, 13,949 × 9,524, 20,059,574 bytes. Its SHA-256 was rechecked against the recorded institutional download. Full image shows the title, main North Carolina map, portions of Virginia and South Carolina, central join/fold, decorative southeast cartouche and marginal scales. No independent geographical inset was identified. Original printed date is 1770; digital reproduction date is unknown. The original JP2 remains unaltered. Source metadata records acquisition and attribution.

The existing polygon visibility mask is retained. It removes the cartouche and margins conservatively, and consequently clips some adjacent geography. It does not erase white map content: transparency is a separate alpha band, with no white/black RGB nodata rule. The complete scan preserves everything.

## Method and measured discrepancies

Unweighted affine fitted in EPSG:32119 (NAD83 / North Carolina, metres) to eight legacy town proxies. Four proxy checks were frozen before the original fit; this run reproduces the coefficients without tuning. These are independent of fitting, **not independent validation of historical ground positions**. The control table is below the requested 12–20 credible controls because additional credible exact anchors have not been established. Do not reinterpret legacy proxies as accepted features merely to achieve that count.

- Eight fitting proxies: RMSE **6,844.78 m** (see exact values in `manifest.json` and `errors.csv`).
- Four held-out proxy discrepancies: RMSE **8,023.09 m**, maximum **13,077.54 m**; rounding here is approximate, exact machine-readable values govern.
- Independent geographic-checkpoint accuracy: **not established**.

The original checks at Salem, Tarboro, Hertford and Bath are retained. They have now been examined, so a future revised model requires fresh reserved checkpoints. No higher-order polynomial or TPS is warranted by the weak controls; small training residuals would not demonstrate better registration. No historical route or modern road was used as a control.

## Spatial limitations and review

Far west, southern edge and Outer Banks lack independent checks. Areas outside the eight-point fitting envelope are extrapolation. Generalized coastlines, changed channels and map compilation distortions can depart substantially from modern reference geography. The Eno–Haw/Hillsborough preview is a **provisional inspection area**, not a selected Trading Path Association corridor or project boundary. Hillsborough is a fitting proxy, so its apparent agreement supplies no independent validation. Jordan and Falls reservoirs substantially changed the modern regional appearance; do not force old tributaries onto modern lake shores.

The overview and Salem, Bath, Cape Fear and Eno–Haw comparisons overlay the raster at 55% on USGS The National Map exports. Their exact returned extents, including any service aspect-ratio adjustment, are used. They expose discrepancies, not certify accuracy. The broad original scan footprint is retained in raster bounds even where alpha is zero. Manifest geographic bounds are raster envelopes, not validated surveyed map limits.

See `evidence/` for additional natural-feature review when present. The existing review packet in `research/review.html` remains available. Prioritize exact feature identification at Haw–Deep and Trent–Neuse, historical channel stability, and well-distributed western/southern controls before upgrading status. Existing town evidence and original rejected candidates are in `research/reports/reference-research.md`, `legacy_candidates.csv`, and the retained review packet; Brunswick Town, Cross Creek and unresolved Haw–Deep were never fitted.

## Outputs and regeneration

Run `.venv313/bin/python tools/processing/georeferencing/collet.py` from the project root. It verifies the scan checksum and frozen point-table hashes, independently reconstructs the affine, and produces outputs under ignored `deliverables/collet_1770/` without modifying the existing viewer or pilot output. It reuses completed new rasters; remove only those new deliverables deliberately when rebuilding after a versioned input change. See consolidated reproduction instructions for initial source/reference acquisition.

Master: `collet_1770_approximate_master_32119.tif`, EPSG:32119, 100 m grid. Web derivative: `collet_1770_approximate_web_3857.tif`, EPSG:3857, 125 Web Mercator units per pixel. Both are tiled DEFLATE COGs with internal overviews and RGBA. Source reduction to 6,975 × 4,762 uses Lanczos, followed by bilinear warp and average overviews. The master preserves the established pilot sampling; it is not a native-pixel archival replacement for the JP2. Pixel size is not positional accuracy. Actual dimensions, bounds, sizes, checksums and structural validation are in the per-map manifest.

The QGIS `.points` file uses EPSG:32119 target coordinates and negative source Y (QGIS image convention); CSV coordinates remain original upper-left pixel-edge origin, X right, Y down. Checks are disabled in the QGIS file. The required residual columns are placeholders; `errors.csv` is the authoritative computed discrepancy table. Loading those proxies does not make them approved historical controls.

Publication workspace and layer publication are pending. Suggested layer `collet_1770`. No server has been changed. **Rectification does not establish the accuracy of historical routes or locations.**
