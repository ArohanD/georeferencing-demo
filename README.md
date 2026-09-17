# The Listening Machine — Collet 1770 demo

Public historical-map georeferencing proof of concept for an NC State MGIST capstone.

**Provisional regional overlay:** four held-out town proxies give an 8.02 km RMSE, with a maximum error of 13.08 km. This is not a source of precise historical settlement, road or parcel locations. Eight town proxies fit one affine model; four were reserved before fitting. The demo includes an opacity slider, modern reference maps, point discrepancies, static comparisons, a feasibility report and review materials.

Open the GitHub Pages website linked in this repository’s About section. For local use, run `python -m http.server 8000 --bind 127.0.0.1` from this folder and open http://localhost:8000/preview/ . All imagery and Leaflet are bundled; there are no third-party map requests, API keys, analytics or paid services in the viewer.

## Included material

- `preview/`: viewer and annotated point-review page.
- `outputs/`: display overlays, comparisons, crops and selected method/error records.
- `reports/`: feasibility and source research, with browser-readable HTML copies.
- `data/`: selected reference images, control-point tables and source credits.

This repository is a display package. It deliberately excludes the source scan, full COG, processing scratch files, Python environment and machine-specific metadata. It is not the complete reproducibility archive. Public corrections should not contain personal or confidential information; the current review CSV is a blank response template with baseline candidates.

## Attribution and reuse

Historical scan: Library of Congress, Geography and Map Division, [John Collet, A compleat map of North-Carolina from an actual survey, London: S. Hooper, 1770, Copy 1](https://www.loc.gov/resource/g3900.ar150000/). See `data/metadata/source.json` for provenance and stated reuse terms.

Modern maps: USGS The National Map and its credited contributors; full attribution is preserved in `data/metadata/usgs-topo-service.json`. Reference town coordinates: USGS GNIS, NAD83. Leaflet 1.9.4 is provided under its BSD license in `preview/LEAFLET-LICENSE`. The map’s historical content reflects its time; inclusion is not endorsement.

No additional blanket license is asserted over third-party material or the project’s original writing/code. Retain source credits and the provisional-accuracy notice when sharing the demo.
