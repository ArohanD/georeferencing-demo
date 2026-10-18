# Map processing

Run commands from the repository root. These tools use repository-relative paths resolved from their source location, so their data paths also work when invoked from another directory.

- `georeferencing/`: multi-map preparation, evidence packets, review, catalog generation, and raster verification.
- `fetch_sources.sh`, `prepare_points.py`, `process.py`, `download_references.py`, `build_review.py`: original Collet pilot pipeline.
- `verify.py`, `check_server.py`: original pilot provenance/raster and local HTTP checks.
- `publish_historical_maps.py`, `test_publish_historical_maps.py`: scoped GeoServer publisher and offline tests.

Create a Python 3.13 environment and install `tools/processing/requirements.lock.txt`, or use the existing `.venv313` environment. The viewer has no Python package dependencies.

```bash
python3.13 -m venv .venv313
.venv313/bin/python -m pip install -r tools/processing/requirements.lock.txt
.venv313/bin/python tools/processing/test_publish_historical_maps.py
.venv313/bin/python tools/processing/verify.py
.venv313/bin/python tools/processing/georeferencing/verify.py
```

Raster verification requires the preserved local inputs and generated rasters. See [map reproduction instructions](../../data/historical_maps/README.md) for downloads and individual map workflows, and [publication instructions](../../docs/colonial-map-publication.md) for publishing.

The pilot scripts write `data/points/preview.json`, `outputs/`, and `research/review.html`. They do not generate the live viewer. Regenerating the pilot changes research outputs; it is not an app build step. The research page links to shared data and images and should be served from the repository root.

Input checksums and source scans are preserved. Do not regenerate frozen controls or tune models as part of routine app maintenance.
