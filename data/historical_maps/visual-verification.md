# Visual verification, 2026-10-07

Full-extent and multiple detail comparisons were inspected as rendered raster images against USGS The National Map exports. This assesses observed displacement and orientation; it does not replace independent checkpoints. No browser automation was needed to inspect the actual warped pixels. The app was not modified or smoke-tested against unpublished WMS endpoints.

## Collet

The full overview has readable upright labels, correct east/west ordering and an alpha cutout of the southeast cartouche. Bath/Pamlico detail visibly disagrees in river and town vicinity, consistent with the recorded large held-out Bath proxy discrepancy. Cape Fear detail also diverges around Wilmington and the lower river/coast. The Eno–Haw comparison shows the historical network against modern reservoirs; broad apparent agreement around Hillsborough cannot validate it because Hillsborough was a fitted town proxy. No historical road is asserted to follow a modern one. The master/web comparison quantifies conversion fidelity separately in `collet_1770/verification.json`.

## Mouzon

The Eno–Haw/Hillsborough panel shows historical rivers amid modern reservoirs, with visible displacement. The Cape Fear coastline and Wilmington vicinity are substantially displaced west of the modern features. Albemarle and the Outer Banks are likewise visibly displaced. Labels are upright and there is no east/west mirror reversal. The large displacement is a limitation of the approximate graticule placement, not evidence of validated historical route locations. The independent Trent–Neuse diagnostic is recorded in the map's own QA; do not present graticule-fitting residuals as modern accuracy.

## Moseley

The full extent is upright with the lower inset strip removed from the main-map footprint; the original scan preserves those insets. The Trent/Neuse vicinity looks comparatively close because it helped fit the affine. Cape Lookout and nearby coast retain visible differences even in the fitted region. The northeastern panel shows much stronger displacement around Albemarle/Roanoke Island. The Eno–Haw panel is at the weakly constrained northwest map edge; the historical map content there is sparse/generalized and does not establish a Hillsborough-era point match. The modern Hillsborough label alone is not evidence of a 1733 settlement control. Interior placement is unsupported by the coastal-only fit.

All three remain **approximate only**. Geographic validation requires better feature homology and spatially distributed independent checks. Rectification does not establish accuracy of historical routes or locations.
