# NextGIS Web Community Edition evaluation

**NC State Listening Machine · 12 October 2026 · synthetic data only**

## Executive summary and recommendation

**Keep the existing GeoServer deployment. Consider NextGIS as a separate editing/publication pilot, not an approved replacement for sensitive research data.** This evaluation ran the requested official CE image locally, imported synthetic rasters and vectors, exercised real HTTP services, authenticated test users, and used Chromium to operate the editing interface.

NextGIS provides useful integrated editing, vector versioning, resource permissions, raster rendering, MVT, WMS/WMTS, WFS, and OGC API Features. These are substantial advantages over the project's current display-oriented integration. Three findings prevent recommending immediate replacement:

1. **Filters do not provide feature-level privacy.** An anonymous request with `fld_status__eq=approved` returned one approved feature; removing the filter or requesting the draft feature by ID returned the draft. Use physically separate private and public datasets, or develop and independently verify a server-side security mechanism.
2. **Mixed public/private services exposed private metadata.** A public OGC API Features service referencing a private layer returned that layer's geographic bounding box even after anonymous resource access was explicitly denied. Public WFS `DescribeFeatureType` returned its field schema. Feature bodies and tiles remained protected in the tested requests. Removing private references from public services mitigated these specific exposures.
3. **The tested image bundles PostgreSQL 12.22.** PostgreSQL 12 reached upstream end of life on 21 November 2024. Obtain a supported database/image upgrade path or documented vendor security maintenance before university production use. No vulnerability scan or exploit test was performed. [PostgreSQL version policy](https://www.postgresql.org/support/versioning/)

A practical pilot is: researcher edits a private working layer; reviewer copies a checked, sanitized subset into a separate public layer; public services reference only that public layer. This was demonstrated through the API. A reliable approval interface, publication automation, audit linkage, withdrawal handling, and safeguards against accidental publication still require project work.

## Environment and exact software

Runtime observations:

| Item | Observed value |
|---|---|
| Host | Ubuntu WSL2, Linux `5.15.153.1-microsoft-standard-WSL2`, linux/amd64 |
| Docker client / engine | 27.3.1 / 27.3.1; API 1.47 |
| Requested and tested image | `nextgis/nextgisweb-ce:26.07.0` |
| Repository digest | `sha256:2cf70ea28e5c9da8be36b36461776fabf7f1e7f360e15f7a7e3fdd593a7e5afa` |
| Local image ID | `sha256:414ff541c2c33702a085c1e91d0e577ed9b73898b590bd0789bb5e40a8730075` |
| Image size reported by Docker | 3,987,109,390 bytes |
| Application package versions | `nextgisweb=5.5.0`, `nextgisweb_mapserver=3.1.0`, `nextgisweb_qgis=3.9.0` |
| Container OS / Python / uWSGI | Ubuntu 24.04.4 LTS / 3.12.3 / 2.0.31 |
| Database / spatial extension | PostgreSQL 12.22 / PostGIS 3.6.4 |
| GIS/runtime libraries | GDAL 3.8.4; GEOS 3.12.1; PROJ 9.4.0; Pyramid 2.1; SQLAlchemy 2.0.49 |
| Host binding | **`127.0.0.1:18087 -> 8080/tcp`**, no database port published |
| Temporary directory | `/tmp/lm-nextgis-test-nUf72Zm7` |
| Browser | Existing local Playwright/Chromium installation; fresh browser contexts |

The distribution tag and application package version are different numbering systems. Both were recorded; no substitute image was used. Docker access initially failed inside the sandbox and succeeded through the approved execution mechanism. An initial harness error occurred before container creation; its exit trap removed that attempt's image, and all four Docker inventory comparisons were empty. The corrected second attempt completed deployment.

The only existing project material read for comparison was `docs/geoserver-integration.md`. No TPA research files or historical-map datasets were opened. Existing GeoServer endpoints were not contacted or modified. Existing browser/Python tooling was reused without installation or modification. Browser test requests to non-local hosts were blocked by the test harness.

## Results

**PASS** means the stated operation was actually observed; it does not certify all variants or production readiness. **FAIL** means a tested acceptance condition was not met. **NOT TESTED** identifies missing verification, not assumed support or failure. HTTP evidence below uses the localhost base URL above.

| Test | Result | Runtime evidence and limits |
|---|---|---|
| 1. Docker, pull, startup, UI and API | **PASS** | Engine 27.3.1 responded; requested digest pulled; uWSGI and PostgreSQL initialized; `/login` 200 HTML; authenticated `/resource/5` 200 HTML; package-version API 200. Chromium signed in as researcher. |
| 2. Raster import and XYZ-style tiles | **PASS** | Synthetic 256×256 RGB GeoTIFF upload 200, raster/style creation 201; tile `z=10,x=288,y=402` returned 200 PNG, decoded as 256×256 with nonconstant color values. |
| 2. Raster WMS and WMTS | **PASS** | WMS capabilities, WMS 1.1.1 GetMap and 1.3.0 GetMap returned 200; WMTS capabilities and GetTile returned 200. Decoded WMS/WMTS pixels, not merely status codes. |
| 2. WCS coverage delivery | **NOT TESTED** | A WCS capabilities probe against the existing WMS service returned 400. No working WCS endpoint was established; this is not evidence of universal absence. |
| 3. Point, line, polygon import and feature/GeoJSON access | **PASS** | All three imports 201; feature API 200 with expected geometry/attributes; GeoJSON exports 200 ZIP and decoded successfully. |
| 3. MVT delivery | **PASS** | Point/line/polygon tiles returned 200 `application/vnd.mapbox-vector-tile`, 222/160/166 bytes. GDAL's MVT driver decoded geometry, fields, and 4/2/2 features respectively. Four points include two API test additions. |
| 4. API creation, geometry/attribute edit, deletion | **PASS** | Researcher POST, PUT, DELETE returned 200; readback showed changed coordinates and values; deleted feature returned 404. |
| 4. Actual browser CRUD | **PASS** | Chromium UI creation and editing produced real PATCH/PUT responses. Geometry readback changed from approximately `(-78.64623,35.78466)` to `(-78.59473,35.81265)`, with attribute changes. Deletion evidence is recorded below. |
| 5. Users, role groups, authentication, authorization | **PASS** | Three groups and local users created, each 201. Correct credentials 200; wrong password 401. Public user denied private reads/writes; all three non-admin users denied user-management API access. |
| 6. Private feature bodies, exports, downloads, and tiles | **PASS** | Anonymous feature list/item, GeoJSON export, GeoTIFF download, raster XYZ, MVT, WMS GetMap, WMTS GetTile, WFS GetFeature, and OGC API Features items returned 403. Public controls returned 200 with data. |
| 6. No private information through *all* exposed service paths | **FAIL** | Public OGC collections metadata exposed private extent despite resource denial; public WFS DescribeFeatureType exposed private schema. See security findings and tested mitigation. |
| 7. Feature privacy within one shared public dataset using filters | **FAIL** | Filtered anonymous request returned approved only; unfiltered collection and direct ID returned draft, all 200. No native per-feature ACL was demonstrated. |
| 8. Researcher → reviewer → approved public subset | **PASS** | Researcher edited private data; reviewer queried approved subset and inserted it into public layer; anonymous read saw one approved feature; researcher/public writes to published layer returned 403. This was custom API orchestration, not a built-in approval workflow. |
| 9. Infrastructure inspection and backup creation | **PASS** | Inspected runtime versions, named mounts, non-root user, storage and process logs. `nextgisweb backup --one-shot` created a 313 KiB archive; 92 members, CRC check passed. |
| 9. Restore, upgrades, load/HA, university SSO | **NOT TESTED** | No restore rehearsal, upgrade/migration test, load test, failover test, or NC State identity integration. PostgreSQL support issue remains a production blocker. |

## Synthetic data and reproducible HTTP evidence

Resource IDs belong only to this disposable instance:

| Resource | ID |
|---|---:|
| Private / public / filter-demo folders | 2 / 3 / 4 |
| Private Point / LineString / Polygon | 5 / 6 / 7 |
| Private raster / raster style / WMS-WMTS service | 8 / 9 / 10 |
| Approved public points / intentionally mixed filter-demo layer | 11 / 12 |
| WFS / OGC API Features services | 13 / 14 |
| Public raster / style | 15 / 16 |

Each initial vector file held two synthetic features with `name`, `status` (`draft` or `approved`), and integer `value` (1 or 2). Points were at `[-78.65,35.78]`; lines ran from `[-78.7,35.7]` to `[-78.6,35.8]`; polygons were closed rectangles spanning those bounds. No features represent real observations or people. The raster covered longitude −78.8…−78.5 and latitude 35.6…35.9 in EPSG:4326; red/green were gradients and blue was 120. Imports targeted EPSG:3857.

Selected actual responses (credentials, cookies, and transient request IDs omitted):

```text
GET /api/component/pyramid/pkg_version                    administrator -> 200 application/json
{"nextgisweb":"5.5.0","nextgisweb_mapserver":"3.1.0","nextgisweb_qgis":"3.9.0"}

POST /api/resource/5/feature/?srs=4326                     researcher -> 200
{"id":5,"version":4}
PUT /api/resource/5/feature/5?srs=4326                     researcher -> 200
GET /api/resource/5/feature/5?srs=4326                     researcher -> 200
{"id":5,"vid":5,"geom":"POINT(-78.61 35.79)",
 "fields":{"name":"CRUD-edited","status":"draft","value":11}, ...}
DELETE /api/resource/5/feature/5                          researcher -> 200
GET /api/resource/5/feature/5                             researcher -> 404

GET /api/resource/5/feature/1                             anonymous -> 403
{"title":"Insufficient permissions",
 "message":"Insufficient 'read' permission in scope 'data' on resource id = 5.", ...}
GET /api/resource/5/export?format=GeoJSON                  anonymous -> 403
GET /api/resource/8/download                              anonymous -> 403
GET /api/component/feature_layer/mvt?resource=5&z=10&x=288&y=402
                                                         administrator -> 200, 222 bytes
                                                         anonymous -> 403
GET /api/component/render/tile?resource=9&z=10&x=288&y=402
                                                         administrator -> 200 image/png, 740 bytes
                                                         anonymous -> 403
GET /api/component/render/tile?resource=16&z=10&x=288&y=402
                                                         anonymous -> 200 image/png, 740 bytes
GET /api/component/feature_layer/mvt?resource=11&z=10&x=288&y=402
                                                         anonymous -> 200 MVT, 91 bytes
GET /api/component/feature_layer/mvt?resource=11,5&z=10&x=288&y=402
                                                         anonymous -> 403
```

For WMS 1.1.1, the successful request was:

```text
GET /api/resource/10/wms?SERVICE=WMS&REQUEST=GetMap&VERSION=1.1.1
    &LAYERS=raster&STYLES=&FORMAT=image/png&SRS=EPSG:4326
    &BBOX=-78.8,35.6,-78.5,35.9&WIDTH=256&HEIGHT=256
administrator -> 200 image/png, 911 bytes
Decoded RGBA extrema: ((0,255),(0,255),(120,120),(255,255))
anonymous -> 403 application/vnd.ogc.se_xml, 194 bytes
```

WMTS uses the **same `/wms` endpoint**, with `SERVICE=WMTS`, not `/wmts`. An initial guessed `/wmts` route returned 404 and was corrected using the shipped application source. `REQUEST=GetTile&VERSION=1.0.0&LAYER=raster&STYLE=default&TILEMATRIXSET=EPSG:3857&TILEMATRIX=10&TILECOL=288&TILEROW=402&FORMAT=image/png` returned 200 PNG to administrator and 403 to anonymous.

WFS GetCapabilities and GetFeature worked for versions **1.0.0, 1.1.0, and 2.0.0**. On public service 13, `TYPENAME=private_points` returned 403 to anonymous, while `TYPENAME=public_points` returned 200 GML containing the approved point. Administrator requests to both returned 200. WFS transactions were not tested. OGC service 14 returned a valid GeoJSON FeatureCollection for `/ogcf/collections/public_points/items`; private collection item/list requests returned 403.

### Response fingerprints

Selected response-body SHA-256 values were recorded before deleting temporary artifacts. These identify the observed bytes; they are not golden hashes for future runs.

| Request | Identity | Status / bytes | SHA-256 |
|---|---|---|---|
| `/api/component/feature_layer/mvt?resource=6&z=10&x=288&y=402` | administrator | 200 / 160 | `97835155c6bff209d02775031f14e462292395eb2a844504fb98689e923f1cb8` |
| `/api/component/render/tile?resource=9&z=10&x=288&y=402` | administrator | 200 / 740 | `2efeb2e60a79fb99df15468454ea6b758f0295aac76bb41f4120b3d69cb9d1bf` |
| `/api/resource/12/feature/1` | anonymous | 200 / 180 | `b1adf26974b347b5eb78297b0588b1b07eb6a9a9bf585dc0ead8c0ccd58b0a29` |

Selected startup output:

```text
*** Starting uWSGI 2.0.31 (64bit) on [Mon Oct 12 23:39:26 2026] ***
uWSGI http bound on 0.0.0.0:8080 fd 4
Python version: 3.12.3
*** Operational MODE: preforking ***
```

Docker inspection separately confirmed host binding `127.0.0.1:18087`, both named volume mounts, and `User=crater`.

## Security and feature-level visibility

### ACL configuration and roles

Groups `researcher`, `reviewer`, and `public` had IDs 7, 9, and 11; corresponding users had IDs 8, 10, and 12. Group membership alone is not a predefined workflow role: permissions were explicitly assigned. Anonymous access used built-in **Guest**, distinct from the authenticated sample public user.

Researchers and reviewers received private data read/write and service-connect permissions. Everyone received read access to published data; only reviewers received published data write access. Administrator access was preserved. Initially, root resource metadata was readable so data permissions could be tested independently. Later, explicit Guest/public-group `resource.read` denials on the private subtree made `/api/resource/5` return 403 as well. The documented permission model is resource-oriented; allow/deny inheritance and dependencies require careful configuration. [NextGIS permission model](https://docs.nextgis.com/docs_ngweb/source/permissions.html)

Observed authentication/authorization:

| Operation | Researcher | Reviewer | Public user | Anonymous |
|---|---:|---:|---:|---:|
| Correct local authentication/current user | 200 | 200 | 200 | 200 Guest |
| Read private feature collection | 200 | 200 | 403 | 403 |
| Create private feature | 200 | 200 | 403 | 403 |
| Read published collection | 200 | 200 | 200 | 200 |
| Update published feature | 403 | 200 | 403 | 403 |
| List managed user accounts | 403 | 403 | 403 | 403 |

Invalid researcher credentials returned **401**, not an anonymous success. The browser also authenticated through the login form and session cookie. TLS, SSO, MFA, account recovery, password policy, and brute-force protections were not assessed.

### Confirmed filter bypass

On deliberately public layer 12:

```text
GET /api/resource/12/feature/?fld_status__eq=approved  anonymous -> 200, one approved feature
GET /api/resource/12/feature/                         anonymous -> 200, draft + approved
GET /api/resource/12/feature/1                        anonymous -> 200
{"id":1,"vid":1,"geom":"POINT(-8755277.950890968 4270391.783600916)",
 "fields":{"name":"Point draft","status":"draft","value":1}, ...}
```

Anonymous MVT access also returned that layer's tile (141 bytes). A `status` field is ordinary editable data, not a security decision. The test establishes that query filtering cannot protect drafts; it does not prove that no extension or custom PostGIS design could implement row security. Such alternatives were **NOT TESTED**. The vendor describes map/table filters as ways to change which features are displayed, consistent with this finding. [Filter documentation](https://nextgis.com/blog/filters-in-nextgis-web/)

### Confirmed metadata exposure through mixed services

A deliberately public OGC API Features service referenced both private layer 5 and public layer 11. After explicit anonymous `resource.read` denial on the private folder:

```text
GET /api/resource/5                                     anonymous -> 403
GET /api/resource/14/ogcf/collections/private_points/items
                                                       anonymous -> 403
GET /api/resource/14/ogcf/collections/private_points     anonymous -> 200
... "id":"private_points", "title":"Private points",
"extent":{"spatial":{"bbox":[[-78.65,35.78,-78.64313354492187,35.78849461197884]],
"crs":"http://www.opengis.net/def/crs/OGC/1.3/CRS84"}} ...
```

The public `/collections` listing exposed the same private extent. For a sparse or single-point dataset, an extent can disclose a sensitive location. Similarly, anonymous WFS 2.0 `DescribeFeatureType&TYPENAME=private_points` returned 200 XML with `geom`, `name`, `status`, and `value` definitions. These are observed metadata disclosures; no claim is made that WFS returned private feature bodies.

**Tested mitigation:** remove private-layer entries from public service 13's `layers` and service 14's `collections`. Public collections then contained only `public_points`; the private OGC collection and items paths returned 404; WFS private DescribeFeatureType returned 422 “Unknown layer” instead of a schema. Public/private separation must include service configuration, not only the underlying layer's ACL.

Some capabilities requests still returned 200 without private data access, including the private WMS service's capabilities. A 200 capabilities response is not proof of data access; conversely, a 403 feature response does not prove complete confidentiality. Attachment listing and feature count were also tested and returned 403 for the private layer; populated attachments and every possible ancillary endpoint were not exhaustively audited.

### Data sovereignty

This test kept uploaded data and PostgreSQL storage in local named volumes. It needed no NextGIS cloud account for local users. This supports an on-premise architecture, **not** a blanket assurance of no outbound communications. The browser geometry editor offered an OpenStreetMap basemap; external requests were blocked during this evaluation. Production should review basemaps, search/geocoding, analytics, optional integrations, outbound server traffic, support procedures, and backups against research-data obligations. A complete egress/telemetry audit was **NOT TESTED**.

## Editing experience and publication workflow

The researcher signed in, opened **Point → Feature table**, clicked **Create**, entered fields, opened **Geometry**, placed a point on the map, and saved. The actual browser submitted batch PATCH for creation and PUT for updates. The editor has Attributes, Description, Attachments, and Geometry tabs, with Create/Modify/Move controls and undo. Attribute changes and a geometry replacement were read back from the server. API responses included feature version identifiers, and the interface exposed Version history. Conflict resolution and multi-user concurrent edits were not tested.

Browser evidence:

```text
PATCH /api/resource/5/feature/?dt_format=iso -> 200 [{"id":9,"version":11}]
fields: {"name":"Browser CRUD final2","status":"draft","value":42}
geom: POINT(-8754858.464479735 4271031.5003780415)

PUT /api/resource/5/feature/9?dt_format=iso -> 200 {"id":9,"version":13}
fields: {"name":"Browser edited final2","status":"draft","value":44}
geom: POINT(-8749125.687358346 4274872.461049371)

GET /api/resource/5/feature/9?srs=4326 -> 200
geom: POINT(-78.59473327636717 35.81264732352025)
```

Chromium selected the feature, clicked Delete, and confirmed the dialog:

```text
DELETE /api/resource/5/feature/  body: [{"id":9}] -> 200 [9]
GET /api/resource/5/feature/9 -> 404 "Feature not found"
```

These requests came from UI interactions, not injected browser-side fetch calls; the subsequent readback used the browser's authenticated HTTP context.

The table/editor is a plausible improvement for researchers who should not need GIS server administration. The synthetic point workflow was usable with a blank basemap. Line/polygon imports and delivery were tested, but their browser drawing workflows, accessibility, mobile editing, large attachment handling, and user training needs were not evaluated. A separately configured editable Web Map was not built; this browser test used the layer's feature-table geometry editor.

The publication demonstration used administrator-provisioned destinations and these API steps:

1. Researcher edited private layer 5; public users could not retrieve its features.
2. Reviewer queried `GET /api/resource/5/feature/?fld_status__eq=approved`, obtaining one feature.
3. Acting **as reviewer**, the harness copied that feature's geometry and fields with `POST /api/resource/11/feature/` → 200.
4. Anonymous `GET /api/resource/11/feature/` returned one approved feature; researcher create/update attempts returned 403.
5. Public WFS/OGC services were restricted to layer 11. Public raster used a separate resource as well.

The administrator created layers and ACLs; the reviewer account did not require administrator privileges to publish into the prepared layer. This is a working pattern, not an automatic approval system. The project must implement reviewer decisions, controlled field redaction, stable source-to-public IDs, attribution/provenance, idempotent updates, withdrawal/deletion, concurrency handling, and an audit trail. Do not treat a researcher-editable `approved` value as reviewer authorization. Attachments, descriptions, historical versions, precision reduction, and service references also need publication rules.

## Architecture, storage, backup, and hosting

Observed architecture:

```text
Browser / HTTP clients
        |
127.0.0.1:18087 (host publishing only)
        |
CE container: uWSGI + Python/Pyramid NextGIS application
        |-- GDAL / QGIS / MapServer rendering components
        |-- embedded PostgreSQL 12 + PostGIS
        |-- /opt/crater/data    -> named data volume
        `-- /opt/crater/backup  -> named backup volume
```

uWSGI listens on `0.0.0.0:8080` **inside the isolated container**; the Docker host mapping is loopback-only. The image ran as user `crater`, not root. PostgreSQL and the application share one container. The observed image has no configured Docker healthcheck; this test used restart policy `no`. At one post-test snapshot, Docker reported **1.39 GiB** memory usage and **1.01% CPU**; this is not a sizing benchmark. The small test used about **70 MiB** of data storage and **320 KiB** of backup storage. Real rasters, pyramids, attachments, database growth, versions, and backups will dominate capacity.

Startup logs included PostgreSQL initialization and uWSGI 2.0.31 startup, with Python 3.12.3 and prefork workers. A warning stated that slow uploads could be rejected with harakiri enabled without post buffering; large uploads and proxy timeouts need testing. The large bundled image simplifies installation but places database and geospatial dependency patching within the image lifecycle. The official repository recommends Compose for continuous use and a TLS-terminating reverse proxy. [Official CE deployment instructions](https://github.com/nextgis/nextgisweb_ce)

Runtime backup command:

```text
docker exec lm-nextgis-test-nUf72Zm7 \
  nextgisweb backup --one-shot /opt/crater/backup/evaluation.ngwbackup
-> /opt/crater/backup/evaluation.ngwbackup
-> 313 KiB; 92 ZIP members; zipfile.testzip() returned None
-> archive top-level entries: '.', 'component', 'postgres'
```

This demonstrates archive creation/integrity only. **Restore and disaster recovery remain NOT TESTED.** PostgreSQL plus filesystem blobs must be backed up together; the documented application backup/restore tools address both. Production additionally needs protected configuration/secrets, off-host encrypted backup copies, retention/access controls, restore drills, and rollback rehearsals. A backup volume on the same host is not disaster recovery. [Backup and restore documentation](https://docs.nextgis.com/docs_ngweb_dev/doc/admin/backup_restore.html)

University hosting should use a maintained Linux server/VM with an assigned service owner, TLS, monitoring, a supported database lifecycle, documented upgrades, and institutional identity integration. Local WSL2 is adequate for this evaluation; availability, patch ownership, and continuity were not demonstrated. CE licensing/support terms and an SBOM/security-maintenance commitment should be reviewed before adoption; open-source availability does not establish a university support arrangement.

## Comparison with the existing GeoServer integration

The existing side of this comparison is **repository documentation**, not a fresh test or infrastructure inventory. `docs/geoserver-integration.md` records a Leaflet 1.9.4 static viewer consuming WMS 1.1.1 in EPSG:3857 from the NC State GeoServer, along with earlier successful raster/browser checks. No research imagery was opened for this evaluation.

| Concern | Existing project evidence | NextGIS evidence / migration implication |
|---|---|---|
| Current raster viewer | Documented `L.tileLayer.wms`, PNG, WMS 1.1.1, EPSG:3857 | Matching protocol family works with synthetic data; URLs, resource IDs/layer keys, ACLs, styles, CRS and bounds must be reconfigured and tested. No drop-in endpoint compatibility claim. |
| Researcher editing | Referenced integration describes display and review pages, not a hosted feature editor | Built-in feature-table geometry/attribute editor worked in Chromium. |
| Vector API / MVT | Current deployment's vector capabilities and plugins were not inspected | Feature API, GeoJSON, MVT, WFS and OGC API Features were verified here. This does not imply GeoServer cannot provide equivalents. |
| Private/public approval | Existing authorization/workflow configuration unknown | Resource ACLs work for tested data requests; shared-layer filters fail privacy; mixed-service metadata exposure needs separation. |
| Operational footprint | Existing installation is already in use; its exact software/dependencies were not inventoried | New ~4 GB image, embedded PostgreSQL/PostGIS and file storage; added backup/upgrade responsibilities and PostgreSQL EOL concern. |
| Migration risk | Existing public raster integration has documented checks | Synthetic success does not validate original raster sizes, styles, georeferencing, all OGC clients, URLs, performance, or existing security rules. |

Prefer a parallel isolated editing pilot and an explicit publication boundary before proposing a raster-server replacement. Do not migrate sensitive data on the strength of these small functional tests alone.

## Reproduction instructions

Use only newly generated synthetic files. Resource IDs may differ on a rerun. Pin the digest above, use unique `lm-nextgis-test-` names, register cleanup before pulling/creating anything, and record baseline container/volume/network/image IDs. Never remove an image that existed beforehand or is used by another container. Explicitly mount **both** declared image volumes to avoid anonymous persistent volumes.

Equivalent deployment command, after creating the two named volumes and network:

```bash
# Set these to the unique names recorded in your test manifest.
# Do not reuse names from an earlier or another person's test.
docker run -d --name "$test_name" --network "$test_network" \
  -p 127.0.0.1:18087:8080 \
  -e NEXTGISWEB__CORE__LOCALE__DEFAULT=en \
  -v "$test_data_volume:/opt/crater/data" \
  -v "$test_backup_volume:/opt/crater/backup" \
  nextgis/nextgisweb-ce@sha256:2cf70ea28e5c9da8be36b36461776fabf7f1e7f360e15f7a7e3fdd593a7e5afa server
```

The official CE README provides the initial local administrator login. Use it only for this disposable loopback instance; generate random researcher/reviewer/public passwords in a mode-0600 temporary file. Do not put credentials in URLs, preserved logs, or this report.

Generate the raster inside your dedicated temporary directory using Python with NumPy and Rasterio (this run reused an existing environment):

```python
import numpy as np, rasterio
from rasterio.transform import from_bounds
rgb = np.zeros((3, 256, 256), dtype='uint8')
rgb[0] = np.arange(256, dtype='uint8')
rgb[1] = np.arange(256, dtype='uint8')[:, None]
rgb[2] = 120
with rasterio.open('synthetic.tif', 'w', driver='GTiff', width=256,
                  height=256, count=3, dtype='uint8', crs='EPSG:4326',
                  transform=from_bounds(-78.8,35.6,-78.5,35.9,256,256),
                  photometric='RGB') as dst:
    dst.write(rgb)
```

Create the three GeoJSON FeatureCollections using the geometries/attributes specified above. For each file, multipart `POST /api/component/file_upload/` with field `file`; use the returned `upload_meta[0]` as `source` in resource creation:

```json
{
  "resource": {
    "cls": "vector_layer",
    "display_name": "Point",
    "parent": {"id": 2}
  },
  "vector_layer": {
    "source": {"id": "UPLOAD_ID", "name": "Point.geojson", "size": 357},
    "srs": {"id": 3857}
  }
}
```

POST all resource payloads to `/api/resource/`. Raster creation uses `cls=raster_layer` and a `raster_layer` section containing the uploaded source and SRS. Create a child `raster_style`. WMS resource class is `wmsserver_service`, whose `layers` entries contain `keyname`, `display_name`, `resource_id` (the style ID), and nullable `min_scale_denom`/`max_scale_denom`. WFS class/section is `wfsserver_service` with `layers`; OGC class/section is `ogcfserver_service` with **`collections`**. Each vector service entry uses layer `resource_id`, `keyname`, `display_name`, and `maxfeatures:1000`. [Resource creation API](https://docs.nextgis.com/docs_ngweb_dev/doc/developer/create.html)

Create local groups/users through `/api/component/auth/group/` and `/api/component/auth/user/`; user payload includes `keyname`, `display_name`, temporary `password`, and `member_of:[GROUP_ID]`. Discover built-in IDs from the user/group APIs rather than assuming them. Update a resource ACL with `PUT /api/resource/ID`:

```json
{"resource":{"permissions":[
  {"action":"allow","principal":{"id":7},"identity":"",
   "scope":"data","permission":"read","propagate":true}
]}}
```

That example is one rule, **not a complete ACL**: preserve administrator access, add required `resource.read`, and apply the role matrix above. Private layer data read/write belongs to researcher/reviewer groups; public layer write belongs only to reviewers. Deny Guest and public-group resource reads on the private subtree. Configure public services with only public data; temporarily mix a private reference into a synthetic-only public service to reproduce the metadata finding, then remove it.

Run the HTTP requests above with administrator, researcher, reviewer, public, and fresh anonymous clients. Check bodies and binary formats, not just 200 codes. Use `ogrinfo -al TILE.pbf` to decode saved MVT; unzip GeoJSON exports and parse their features; decode PNGs and check pixels. Verify invalid credentials separately. For the browser, use a fresh Chromium context, block non-local requests, sign in as researcher, open `/resource/POINT_ID/feature/`, and operate Create/Edit/Delete plus Geometry. Wait for map interactions/state updates before saving; capture PATCH/PUT/DELETE responses and verify server readback. Creation uses PATCH in this UI, while editing uses PUT—initial harness waits assuming otherwise timed out and were corrected.

Finally, stop/remove the exact recorded test container, then its two volumes and network. Remove the newly pulled image only if absent from the baseline and unused by unrelated containers. Compare all four before/after Docker inventories, check exact resource names no longer exist, verify the port is closed, and remove the exact dedicated temporary directory after copying sanitized evidence into the report. Use an exit/signal trap and an independent cleanup check; do not use prune commands or wildcard deletion.

## Unresolved limitations

- No load, concurrency/conflict, large raster, large vector, sustained availability, or performance comparison.
- No restore/recovery, image upgrade, PostgreSQL migration, SSO/MFA, TLS/proxy, or production deployment test.
- No full endpoint penetration test, vulnerability scan, egress audit, or cache/CDN revocation test. Application tile caching was disabled in the tested raster style.
- No native per-feature ACL or custom database row security demonstration; no approval automation was implemented in the project.
- No WFS transactions, WCS delivery, populated attachment security, browser line/polygon drawing, or separate editable Web Map test.
- No claim that all GeoServer functionality, plugins, styles, projections, client behavior, or operational capabilities have replacements.

## Cleanup verification

**PASS — cleanup completed and independently verified.**

The lifecycle script registered EXIT/INT/TERM/HUP cleanup before the image pull and recorded resource creation in a manifest. It also had a one-hour stop condition. A failed first attempt exercised the exit cleanup. At the end of the successful run, `docker stop --time 30` stopped the application, and the lifecycle exit trap removed the exact container, both volumes, network, and newly downloaded image. Image removal was conditional on absence from the pre-test inventory and absence of any container using it; no force image removal or prune command was used.

| Created resource | Final verification |
|---|---|
| Container `lm-nextgis-test-nUf72Zm7` | Stopped, removed; exact Docker inspect failed because absent |
| Volume `lm-nextgis-test-nUf72Zm7-data` | Removed, including PostgreSQL and uploaded data; exact inspect absent |
| Volume `lm-nextgis-test-nUf72Zm7-backup` | Removed, including test backup archive; exact inspect absent |
| Network `lm-nextgis-test-nUf72Zm7-net` | Removed; exact inspect absent |
| Image `nextgis/nextgisweb-ce:26.07.0` and tested image ID | Removed; tag absent and image-ID inventory restored to baseline |
| Temporary directory `/tmp/lm-nextgis-test-nUf72Zm7` | Removed with an exact-path guarded operation; 75 temporary files removed; existence check false |
| Local test port 18087 | Connection refused (`connect_ex=111`) after cleanup |

An independent Docker enumeration, after the exit trap completed, compared **sets of full IDs/names**, not just counts:

```text
containers: before=5  after=5  added=[]  removed=[]
volumes:    before=5  after=5  added=[]  removed=[]
networks:   before=4  after=4  added=[]  removed=[]
images:     before=15 after=15 added=[]  removed=[]
exact test container, volumes, network and image: absent
/tmp/lm-nextgis-test-nUf72Zm7 exists: false
```

No test resource could not be removed. Generated GeoTIFF/GeoJSON/MVT/PNG files, browser screenshots, harness scripts, intermediate logs, backup data, database contents, session state, and random test credentials were removed. Existing resources and pre-existing Python/browser installations were retained. **Only this Markdown report, with minimal sanitized evidence embedded, remains from the evaluation.**
