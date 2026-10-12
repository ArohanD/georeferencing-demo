# The Listening Machine — historical-map prototype

The Leaflet viewer now streams `history:collet_1770` from the NC State VCL GeoServer over HTTPS above OpenStreetMap. The original local Collet overlays, USGS references, point diagnostics and review links remain available. Moseley is configured but disabled until publication is verified. Mouzon is not included.

**Approximate historical-map alignment. For visual comparison only; not suitable for locating routes or sites precisely.** Collet's approximately 8 km RMSE (four held-out town proxies) and Moseley's approximately 20.5 km RMSE (two held-out coastal proxies) describe uncertain historical correspondences, not survey-grade accuracy estimates.

See [GeoServer integration and deployment](docs/geoserver-integration.md) for verification results, server publication steps and the static build. All public endpoint/layer settings are in `preview/map-config.js`; no environment variables, credentials or database connection are needed.

## Original Collet pilot

**Completed provisional attempt, not a verified historical registration.** Eight town-symbol/GNIS proxies fit an affine transformation. Four towns reserved before fitting have **8.02 km RMSE**, with errors from **1.34 to 13.08 km**. Useful for broad regional interpretation; unsuitable for locating historical roads, parcels or settlements. COG file structure passed strict validation; that does not certify positional accuracy.

## Open from Windows

In your **WSL Ubuntu terminal**:

```bash
cd /home/arohan/code/georef
.venv313/bin/python -m http.server 8000 --bind 127.0.0.1
```

Then open **http://localhost:8000/preview/** in your Windows browser. Stop with Ctrl+C. WSL2 localhost forwarding normally makes this available on Windows; if forwarding is disabled, open that URL in a WSL browser or enable Windows/WSL localhost forwarding. Do not change the bind address to expose the server. No deployment performed.

The default live view requires internet. For offline comparison choose **Collet 1770 · local pilot overlay** and **USGS · local reference**. The five reference images, local historical overlays and Leaflet remain bundled. Visibility, opacity, view selection, reference points and displacement lines are available. All point popups state the proxy limitation. High zoom is for inspection, not an accuracy claim.

## Main outputs

- [Feasibility report](reports/feasibility.md)
- [Provisional COG / GeoTIFF](outputs/collet-1770-provisional.cog.tif) — EPSG:32119, 100 m pixels, RGBA
- [Static overview](outputs/overview-comparison.png); details: [Salem](outputs/salem-comparison.png), [Bath](outputs/bath-comparison.png), [Hertford](outputs/hertford-comparison.png), [Cape Fear](outputs/cape-fear-comparison.png)
- [One consolidated review request](preview/review.html), with annotated crops and modern views; [editable CSV](data/points/review.csv)
- [Candidates](data/points/candidates.csv), [fitting points](data/points/fitting.csv), [checks](data/points/checks.csv), [pixel conventions and frozen split](data/points/selection.json)
- [Transformation/settings](outputs/transformation.json), [errors](outputs/errors.csv), [COG validation](outputs/cog-validation.json)
- [Original institutional scan](data/original/collet-1770-loc-copy1.jp2), [source metadata and SHA-256](data/metadata/source.json), [environment versions](data/metadata/environment.json)

## Reproduce in WSL

Tested: Ubuntu 24.04 / WSL2, Python 3.13.2, Rasterio 1.5.1 with bundled GDAL 3.12.4, PyProj 3.8.0. The existing GDAL 3.9.3 CLI was inspected but not used. No ArcGIS/QGIS installations changed. The complete dependency lock is [requirements.lock.txt](requirements.lock.txt). These binary wheels form one compatible project environment; do not install Python `gdal` against a different system GDAL.

Already provisioned here: use `.venv313/bin/python`. For a fresh checkout with Python 3.13 available:

```bash
python3.13 -m venv .venv313
.venv313/bin/python -m pip install --only-binary=:all: -r requirements.lock.txt
bash scripts/fetch_sources.sh
.venv313/bin/python scripts/prepare_points.py
.venv313/bin/python scripts/process.py
.venv313/bin/python scripts/download_references.py
.venv313/bin/python scripts/build_review.py
.venv313/bin/python scripts/verify.py
.venv313/bin/python scripts/check_server.py
```

Source acquisition, package installation and uncached USGS exports require internet. Cached reference images are reused. All processing and review generation run offline once inputs exist. Allow several minutes and roughly 2 GB free disk / 2 GB available RAM. GDAL is installed from prebuilt wheels, not compiled. The failed `.venv` Python 3.12 bootstrap is unused because Ubuntu's ensurepip was absent; use `.venv313`.

`prepare_points.py` reconstructs the original manually selected points and never overwrites an existing review CSV. It **does not import your corrections**. Preserve this experiment; make a new version and reserve new checks before testing corrections. The scripts verify the original image and frozen CSV hashes. Reference snapshots and `data/metadata/input-checksums.json` pin the inputs: upstream GNIS and USGS maps are mutable, so fresh downloads in a later year may differ. Retain the supplied snapshots for exact reproduction.

## Project layout and attribution

`data/original` preserves the scan; `data/metadata` stores catalogs, provenance, versions and checksums; `data/reference` stores GNIS and USGS snapshots; `data/points` stores decisions; `scripts` reproduces processing; `outputs` holds derivatives; `preview` is the local viewer; `reports` documents evidence and limitations. `outputs/*working*` and `*intermediate*` are regenerable scratch files.

Historical scan: **Library of Congress, Geography and Map Division**, [Collet item 83693769, Copy 1](https://www.loc.gov/resource/g3900.ar150000/), cataloged London: S. Hooper, 1770. The downloaded JP2 is an institutional scan derivative, not the TIFF master or a later printed reproduction. LOC states its digitized map content is free to use and reuse unless otherwise advised; no restrictive advisory identified here. [USGS GNIS](https://www.usgs.gov/us-board-on-geographic-names/download-gnis-data) metadata states no use restrictions and requests acknowledgment. Modern maps: **USGS The National Map** and contributors, with the full credit in [service metadata](data/metadata/usgs-topo-service.json). Leaflet 1.9.4 retains its [BSD license](preview/LEAFLET-LICENSE).

UNC record identities remain unresolved behind an access page. Other supplied ArcGIS maps were verified only at the metadata level and were not used as controls. See [reference research](reports/reference-research.md).
