'use strict';
// Public browser configuration; no credentials or build-time environment variables.
// Bounds/credits copied from data/historical_maps/integration-manifest.json.
window.HISTORICAL_MAP_CONFIG = {
  endpoint: 'https://vclvm176-164.vclgis.cnr.ncsu.edu/geoserver/history/wms',
  version: '1.1.1', // EPSG:3857 x/y BBOX; avoids WMS 1.3.0 geographic axis ambiguity.
  format: 'image/png',
  checkedOn: '2026-10-12',
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
  layers: [
    {
      id: 'collet_1770', label: 'Collet 1770',
      name: 'history:collet_1770', available: true,
      bounds: [[33.20633801651209, -82.89696376311606], [37.13076192130217, -74.5875473850105]],
      attribution: '<a href="https://www.loc.gov/resource/g3900.ar150000/">Library of Congress, Geography and Map Division</a>',
      diagnostic: 'Collet: approximately 8 km RMSE across four held-out town proxies.'
    },
    {
      id: 'moseley_1733', label: 'Moseley 1733 · unavailable',
      name: 'history:moseley_1733', available: false,
      bounds: [[32.716677734594775, -80.51817232695029], [36.6901681903715, -74.78579792016258]],
      attribution: '<a href="https://digital.lib.ecu.edu/62315">East Carolina University, J. Y. Joyner Library, East Carolina Manuscript Collection MC0017</a>',
      diagnostic: 'Moseley: approximately 20.5 km RMSE across two held-out coastal proxies.'
    }
  ]
};
