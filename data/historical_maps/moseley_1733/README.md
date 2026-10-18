# Moseley 1733 reproducible approximate preview

Outputs are in `deliverables/moseley_1733/`, ignored local storage associated with this Linux repository. Transfer `moseley_1733-approximate-web.cog.tif` for an explicitly approximate GeoServer preview; preserve `moseley_1733-approximate-master.cog.tif` and the original JPEG locally. Suggested layer name: `moseley_1733`. Workspace and publication remain pending.

From the repository root, using the existing isolated Linux environment and `tools/processing/requirements.lock.txt`:

```bash
.venv313/bin/python tools/processing/georeferencing/moseley_1733.py --fetch
```

Without `--fetch`, processing and all detail previews use cached inputs offline. The full-extent preview uses cached full-modern files; `--fetch` enables its retrieval. The script verifies pinned source, point and reference hashes before fitting, keeps finished rasters when present, and regenerates lightweight previews/metadata. To intentionally recompute rasters, move the existing two output COGs into an archival folder first; the source and reference images can be reused. No existing original is overwritten.

Exact reproduction requires retaining cached USGS images and JSON responses, whose hashes are pinned. A fresh upstream USGS export can change (including its temporary URL); a hash mismatch stops processing. Treat such an input change as a separate reviewed dataset version rather than silently updating the frozen inputs.

`source.json`, `selection.json`, `points.csv`, `control_points.csv`, `checkpoints.csv`, `errors.json`, `manifest.json`, `environment.json` and `QA.md` contain provenance, decisions and results. `qgis.points` is an optional QGIS Georeferencer import (map CRS EPSG:4326). Its stored residual columns are placeholders; use `errors.json` for measured meter errors. Controls were digitized before fitting; they are deliberately sparse because credible interior matches were not established.

Review `preview-full-extent.jpg`, five detail overlays plus the regional overview, and the paired `M01`–`M06` crop/reference images in the deliverables directory. `edition-1733-cartouche.jpg` verifies the map date. The source has two independent coastal diagnostic checks with approximately **20.45 km RMSE**, so status remains **approximate only**.
