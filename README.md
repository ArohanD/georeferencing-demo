# The Listening Machine

A monorepo for historical-map applications, shared geospatial data, processing tools, and research.

| Directory | Contents |
| --- | --- |
| [apps/viewer/](apps/viewer/) | Static Leaflet app, app build script, and browser tests |
| [tools/processing/](tools/processing/) | Python raster processing, source downloads, GeoServer publishing, and verification |
| [data/](data/) | Shared source metadata, frozen control points, reference images, and map manifests |
| [research/](research/) | Point-review page, historical research reports, and platform evaluations |
| [docs/](docs/) | Integration notes and recorded service/app validation |
| [outputs/](outputs/) | Original Collet pilot results and review images; large rasters and scratch previews are ignored |
| `deliverables/` | Ignored local scans, generated multi-map rasters, previews, and publication receipts |
| `apps/viewer/dist/` | Ignored viewer build, generated from app-owned assets only |

New applications belong under `apps/<name>/` with their own assets, scripts, and README. Shared data stays outside app folders. Paths stored in processing manifests are relative to the repository root; existing data and raster locations are preserved.

## Run the viewer

From the repository root:

```bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory apps/viewer/public
```

Open http://localhost:8000/ . Live map services require internet. See [viewer usage and browser tests](apps/viewer/README.md).

## Build and check

```bash
python3 apps/viewer/scripts/package_demo.py
python3 tools/check_layout.py
```

Deploy only `apps/viewer/dist/`. Its existing root redirect and `/preview/` URL are preserved. Building does not publish anything. See [viewer publishing](apps/viewer/deployment/README.md) for the GitHub Pages workflow and one-time setup.

## Processing and research

See [processing instructions](tools/processing/README.md) and [historical map provenance](data/historical_maps/README.md). Python dependencies belong to processing, not the static app.

To inspect research images and generated deliverables locally, serve the repository root:

```bash
python3 -m http.server 8001 --bind 127.0.0.1
```

Open http://localhost:8001/research/review.html or http://localhost:8001/deliverables/ . This broader local server is for research review, not the deployment package.

Downloaded datasets and original scans remain local and ignored where configured. Keep checksum-pinned snapshots for reproducibility. Historical validation records describe their original runs; they are not claims that remote services have been rechecked today.
