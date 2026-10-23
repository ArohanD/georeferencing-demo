'use strict';
// Pure shared-link parsing/serialization. Applying state remains the app's job.
const viewState = (() => {
  function parse(hash, choices, maxZoom) {
    const params = new URLSearchParams(hash.replace(/^#/, ''));
    if (params.get('view') !== '1') return null;
    const state = {};
    for (const key of ['base', 'terrain', 'historical']) {
      const value = params.get(key);
      if (choices[key].some(option => option.id === value && (key !== 'historical' || Boolean(option.available)))) state[key] = value;
    }
    for (const key of ['opacity', 'terrainOpacity']) {
      const value = params.get(key);
      if (value !== null && value.trim() !== '' && Number.isFinite(Number(value)) && Number(value) >= 0 && Number(value) <= 100) {
        state[key] = Number(value);
      }
    }
    if (['0', '1'].includes(params.get('visible'))) state.visible = params.get('visible') === '1';
    const coordinates = ['lat', 'lng', 'zoom'].map(key => params.get(key));
    if (coordinates.every(value => value !== null && value.trim() !== '' && Number.isFinite(Number(value)))) {
      const [lat, lng, zoom] = coordinates.map(Number);
      if (Math.abs(lat) <= 85.051129 && Math.abs(lng) <= 180 && Number.isInteger(zoom) && zoom >= 5 && zoom <= maxZoom) {
        state.center = [lat, lng]; state.zoom = zoom;
      }
    }
    return state;
  }
  function serialize(state) {
    return new URLSearchParams({
      view: '1', lat: state.lat.toFixed(6), lng: state.lng.toFixed(6), zoom: String(state.zoom),
      base: state.base, terrain: state.terrain, historical: state.historical,
      visible: state.visible ? '1' : '0', opacity: String(state.opacity), terrainOpacity: String(state.terrainOpacity)
    });
  }
  return {parse, serialize};
})();
if (typeof module !== 'undefined' && module.exports) module.exports = viewState;
else window.ViewState = viewState;
