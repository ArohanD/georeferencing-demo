'use strict';
// ArcGIS ImageServer exports for Leaflet's Web Mercator tile grid.
// The server reprojects its native NC State Plane rasters; image bytes need no CORS fetch.
window.createTerrainLayer = (source, options) => {
  const ImageTiles = L.TileLayer.extend({
    getTileUrl(coords) {
      const size = this.getTileSize();
      const nw = coords.scaleBy(size);
      const se = nw.add(size);
      const topLeft = L.CRS.EPSG3857.project(this._map.unproject(nw, coords.z));
      const bottomRight = L.CRS.EPSG3857.project(this._map.unproject(se, coords.z));
      const params = new URLSearchParams({
        f: 'image', format: 'png32', bboxSR: '3857', imageSR: '3857',
        bbox: [topLeft.x, bottomRight.y, bottomRight.x, topLeft.y].join(','),
        size: `${size.x},${size.y}`, interpolation: 'RSP_BilinearInterpolation'
      });
      return `${source.endpoint}/exportImage?${params}`;
    }
  });
  return new ImageTiles('', {...options, attribution: source.attribution});
};
