#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")/../.."
mkdir -p data/original data/reference data/metadata apps/viewer/public/preview
# Do not overwrite preserved source files. --fail prevents saving HTTP error pages.
fetch() { if [ ! -s "$2" ]; then curl --fail --location --retry 2 "$1" -o "$2"; fi; }
fetch 'https://www.loc.gov/item/83693769/?fo=json' data/metadata/loc-item.json
fetch 'https://tile.loc.gov/storage-services/service/gmd/gmd390/g3900/g3900/ar150000.jp2' data/original/collet-1770-loc-copy1.jp2
fetch 'https://prd-tnm.s3.amazonaws.com/StagedProducts/GeographicNames/Topical/PopulatedPlaces_National_Text.zip' data/reference/PopulatedPlaces_National_Text.zip
fetch 'https://prd-tnm.s3.amazonaws.com/StagedProducts/GeographicNames/Topical/PopulatedPlaces_National_Text.xml' data/metadata/gnis-populated.xml
fetch 'https://prd-tnm.s3.amazonaws.com/StagedProducts/GeographicNames/Topical/HistoricalFeatures_National_Text.zip' data/reference/HistoricalFeatures_National_Text.zip
fetch 'https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer?f=pjson' data/metadata/usgs-topo-service.json
fetch 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js' apps/viewer/public/preview/leaflet.js
fetch 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css' apps/viewer/public/preview/leaflet.css
fetch 'https://raw.githubusercontent.com/Leaflet/Leaflet/v1.9.4/LICENSE' apps/viewer/public/preview/LEAFLET-LICENSE
printf '%s\n' 'ddda5ee92d091ed5aca1ee8d63d43b6f349264770073041ea4be60a523705591  data/original/collet-1770-loc-copy1.jp2' | sha256sum --check
