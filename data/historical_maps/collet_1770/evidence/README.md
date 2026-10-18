# Collet natural-feature review, 2026-10-07

No additional accepted control or checkpoint is established by this packet. The existing town-proxy fit remains approximate only. Four visually inspected natural-feature candidates are recorded with native-image crop coordinates in `candidates.json`; their approximate crosshair positions must not be imported as accepted GCPs. Candidate image positions were selected on the original-resolution scan, not predicted from the old affine transformation. No modern coordinate is asserted.

Open `deliverables/collet_1770/evidence/review.html` from the repository root. Regenerate with `.venv313/bin/python tools/processing/georeferencing/collet_evidence_packet.py`. The script uses the original JP2, cached New Bern reference, and bounded USGS map exports. Downloaded modern snapshots are cached in ignored deliverables; small request/response metadata and SHA-256 checksums are preserved here. No heavyweight warp is performed.

| ID | Finding | Exact remaining decision |
|---|---|---|
| C01 | The Haw and Deep join visibly south of the New Hope tributary on Collet. USGS documents Jordan Dam 4.1 miles upstream of the Haw–Deep confluence. This distinguishes the non-inundated junction from C03. | Select a sourced modern channel-center junction from USGS hydrography/topography, assess channel movement since 1770, and decide whether the historical centerline geometry supports that same target. The crosshair is approximate and needs independent reviewer confirmation. |
| C02 | New Bern is visibly at a narrow stylized Trent/Neuse junction on the scan; USGS describes the modern mouth as an estuary. | Define the homologous feature: bank apex versus channel center. A nearby gauge coordinate is not the junction; the existing GNIS town coordinate is not a replacement. Consider generalized estuary-width depiction before choosing a point. |
| C03 | Collet labels New Hope Creek flowing into Haw. NC DEQ documents the dam below the Haw/New Hope junction and lake storage in New Hope basin. | Exclude modern shoreline points. Recover the original channel junction from pre-impoundment topographic survey with known datum before reconsidering. |
| C04 | A tributary joins the Yadkin on the inspected scan; its label requires contextual confirmation. NC Trails identifies the Uwharrie confluence at Morrow Mountain and the Yadkin name change at Lake Tillery. | Confirm the historical tributary label and use pre-impoundment mapping to distinguish channel junction from reservoir margins. Excluded at this stage. |

The Haw–Deep candidate is the highest priority for human review and is relevant to the provisional Eno–Haw area, but the packet supplies too few spatially distributed verified controls for a defensible new fit. It deliberately leaves reference coordinates blank. New independent checkpoints must be reserved before fitting any expanded model; previously inspected town checks are diagnostic evidence, not a fresh model-selection holdout.

## Authoritative evidence

- [USGS Cape Fear flow-loss study](https://nc.water.usgs.gov/projects/capefear_flowloss/overview.html): Jordan Lake operational since February 1982; dam 4.1 miles above the Haw–Deep confluence. This supports distinguishing the two junctions, not historical channel stability.
- [NC DEQ Jordan Lake background](https://www.deq.nc.gov/about/divisions/water-resources/water-planning/basin-planning/jordan-lake-water-supply-allocation/background-information): dam immediately downstream of Haw/New Hope confluence.
- [USGS Water Supply Paper 2221](https://pubs.usgs.gov/wsp/2221/report.pdf): Trent joins Neuse at New Bern; estuarine setting and mouth widths. Does not establish an exact map-control coordinate.
- [USGS gauge 02092576](https://waterdata.usgs.gov/monitoring-location/USGS-02092576/): nearby Trent River/US 70 station has documented coordinates but represents a gauge location, not the historical junction. Rejected as a substitute control.
- [NC Trails Yadkin River State Trail](https://trails.nc.gov/state-trails/yadkin-river-state-trail): Uwharrie confluence at Morrow Mountain; Lake Tillery setting.
- Modern snapshots: [USGS The National Map](https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer), exact export requests and returned extents in adjacent JSON.

Rectification does not establish the accuracy of historical routes or locations. No road alignment, town centroid, reservoir margin, or other historical map output was accepted as modern ground truth.
