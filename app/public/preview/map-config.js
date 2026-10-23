'use strict';
// Public browser configuration; no credentials or build-time environment variables.
// Bounds/credits from data/historical_maps/integration-manifest.json and per-map manifests.
window.HISTORICAL_MAP_CONFIG = {
  endpoint: 'https://vclvm176-164.vclgis.cnr.ncsu.edu/geoserver/history/wms',
  version: '1.1.1', // EPSG:3857 x/y BBOX; avoids WMS 1.3.0 geographic axis ambiguity.
  format: 'image/png',
  checkedOn: '2026-10-18',
  timeoutMs: 20000,
  basemaps: [
    {
      id: 'osm', label: 'OpenStreetMap', maxZoom: 19,
      url: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    },
    {
      id: 'usgs', label: 'USGS Topographic', maxZoom: 16,
      url: 'https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}',
      attribution: '<a href="https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer">USGS The National Map and contributors</a>'
    },
    {id: 'none', label: 'None'}
  ],
  terrain: {
    bounds: [[33.75, -84.33], [36.59, -75.40]],
    minZoom: 5, maxZoom: 19, inspectZoom: 16, defaultExample: 'eno', defaultMode: 'none',
    attribution: '<a href="https://services.nconemap.gov/secure/rest/services/Elevation">NC OneMap · NC Floodplain Mapping Program / NC Emergency Management</a>',
    modes: [
      {id: 'hillshade', label: 'NC LiDAR hillshade', endpoint: 'https://services.nconemap.gov/secure/rest/services/Elevation/DEM03_hillshade/ImageServer'},
      {id: 'slope', label: 'NC LiDAR slope', endpoint: 'https://services.nconemap.gov/secure/rest/services/Elevation/DEM03_slope/ImageServer'},
      {id: 'none', label: 'Off'}
    ],
    // Public navigation examples, not proposed or validated historical crossings.
    examples: [
      {id: 'state', label: 'North Carolina overview'},
      {id: 'french-broad', label: 'French Broad · Asheville example', center: [35.592, -82.568]},
      {id: 'eno', label: 'Eno River · Hillsborough example', center: [36.07, -79.10]},
      {id: 'haw', label: 'Haw River · Saxapahaw example', center: [35.947, -79.321]},
      {id: 'neuse', label: 'Neuse River · Smithfield example', center: [35.511, -78.35]}
    ],
    // Original NC service legend swatches, captured 2026-10-12; slope is in degrees.
    slopeLegend: [{"label": "90\u00b0 \u00b7 steep", "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAACXBIWXMAAAAAAAAAAAHqZRakAAAAT0lEQVQ4jeWUsQ0AMQgDbYkyKfL7rwqkyApXIL0HOBnbwi21IFWmQ5vCPYUWDTw0ED95PnB+hrhDfIc/bBnP8KOB01t2N/ixKx1VaQooSRd16Q8hzMyREgAAAABJRU5ErkJggg=="}, {"label": "", "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAACXBIWXMAAAAAAAAAAAHqZRakAAAAYElEQVQ4jc3SyQ2AMBQD0Yn0hTjRf5lBkEWgJDQxB1zAO9hOa7GQMudIkbvFwbFBlCmCQNyvB7JDXCYIRLbB8sig2iEQ1QZPG+ziDwGi2qPoHeort9+D/fdgGy6YxnDFDxjdLEWDRcapAAAAAElFTkSuQmCC"}, {"label": "0\u00b0 \u00b7 flat", "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAACXBIWXMAAAAAAAAAAAHqZRakAAAAIUlEQVQ4jWP8+/cvAzUBE1VNGzVw1MBRA0cNHDVwCBkIAEMfAx/78kANAAAAAElFTkSuQmCC"}]
  },
  layers: [
    {
      id: 'collet_1770', label: 'Collet 1770',
      name: 'history:collet_1770', available: true,
      bounds: [[33.20633801651209, -82.89696376311606], [37.13076192130217, -74.5875473850105]],
      attribution: '<a href="https://www.loc.gov/resource/g3900.ar150000/">Library of Congress, Geography and Map Division</a>',
      diagnostic: 'Collet: approximately 8 km RMSE across four held-out town proxies.'
    },
    {
      "id": "wimble_1738",
      "label": "Wimble 1738",
      "name": "history:wimble_1738",
      "available": true,
      "bounds": [
        [
          33.38386554099789,
          -79.21559606346874
        ],
        [
          36.36069944629204,
          -73.82907304106705
        ]
      ],
      "attribution": "<a href=\"https://digital.lib.ecu.edu/1068\">Joyner Library, East Carolina University · NC Archives reproduction</a> · <a href=\"https://rightsstatements.org/vocab/InC-EDU/1.0/\">Educational use</a>",
      "diagnostic": "Wimble: approximately 21.3 km RMSE across three held-out cape proxies."
    },
    {
      "id": "bowen_1747",
      "label": "Bowen 1747 · coastal NC excerpt",
      "name": "history:bowen_1747",
      "available": true,
      "bounds": [
        [
          33.44890092237239,
          -80.07100881818707
        ],
        [
          36.80557338937635,
          -74.68111711346994
        ]
      ],
      "attribution": "<a href=\"https://dlg.usg.edu/record/guan_hmap_hmap1747b6\">Hargrett Library, University of Georgia / Digital Library of Georgia</a>",
      "diagnostic": "Bowen coastal NC excerpt: approximately 13.9 km RMSE across three held-out cape proxies."
    },
    {
      id: 'moseley_1733', label: 'Moseley 1733 · approximate',
      name: 'history:moseley_1733', available: true,
      bounds: [[32.716677734594775, -80.51817232695029], [36.6901681903715, -74.78579792016258]],
      attribution: '<a href="https://digital.lib.ecu.edu/62315">East Carolina University, J. Y. Joyner Library, East Carolina Manuscript Collection MC0017</a>',
      diagnostic: 'Moseley: approximate historical-map visualization. Approximately 20.45 km positional discrepancy (RMSE) was recorded across two coastal checks; interior accuracy remains unvalidated. This is not a comprehensive accuracy assessment. Publishing does not improve georeferencing.'
    }
  ]
};
