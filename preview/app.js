'use strict';
(() => {
  const config = window.HISTORICAL_MAP_CONFIG;
  const el = id => document.getElementById(id);
  const map = L.map('map', {minZoom: 5, maxZoom: 12});
  L.control.scale({imperial: false}).addTo(map);
  let base, overlay;
  const selection = () => config.layers.find(layer => layer.id === el('historical-layer').value);
  const bounds = () => selection().bounds;
  const status = (id, message, failed = false) => {
    el(id).textContent = message;
    el(id).style.color = failed ? '#a21c12' : '';
    el(id).hidden = !failed && /loaded\.|hidden\.$/.test(message);
  };

  // Keep errors local to the affected layer. Removing a layer cancels its timeout.
  function monitor(layer, id, label) {
    let timer, failures = 0;
    const active = () => map.hasLayer(layer);
    function loading() {
      clearTimeout(timer);
      failures = 0;
      status(id, `${label}: loading…`);
      timer = setTimeout(() => {
        if (active()) status(id, `${label}: taking too long. Check your connection and retry.`, true);
      }, config.timeoutMs);
    }
    layer.on('add', loading);
    layer.on('loading', loading);
    layer.on('tileerror', () => {
      failures++;
      if (active()) status(id, `${label}: imagery unavailable or incomplete. Check your connection and retry.`, true);
    });
    layer.on('load', () => {
      clearTimeout(timer);
      if (active()) status(id, failures ? `${label}: some imagery failed. Check your connection and retry.` : `${label}: loaded.`, failures > 0);
    });
    layer.on('remove', () => clearTimeout(timer));
    return layer;
  }

  config.layers.forEach(layer => {
    const option = new Option(layer.label, layer.id);
    option.disabled = !layer.available;
    el('historical-layer').add(option);
  });
  el('historical-layer').value = config.layers.find(layer => layer.available).id;
  config.basemaps.forEach(base => el('basemap').add(new Option(base.label, base.id)));

  function showHistorical() {
    if (overlay) map.removeLayer(overlay);
    const layer = selection();
    if (!el('visible').checked) {
      status('layer-status', 'Historical map hidden.');
      return;
    }
    const opacity = Number(el('opacity').value) / 100;
    if (!layer || !layer.available) return;
    overlay = L.tileLayer.wms(config.endpoint, {
      layers: layer.name, version: config.version, format: config.format,
      transparent: true, styles: '', crs: L.CRS.EPSG3857,
      bounds: layer.bounds, opacity, attribution: layer.attribution,
      zIndex: 2, updateWhenIdle: true
    });
    monitor(overlay, 'layer-status', layer.label).addTo(map);
  }

  function showBase() {
    if (base) map.removeLayer(base);
    const selected = config.basemaps.find(item => item.id === el('basemap').value);
    if (!selected.url) {
      status('base-status', 'Basemap hidden.');
      return;
    }
    base = L.tileLayer(selected.url, {
      attribution: selected.attribution, maxZoom: selected.maxZoom, zIndex: 1
    });
    monitor(base, 'base-status', selected.label).addTo(map);
  }

  el('historical-layer').addEventListener('change', () => {showHistorical(); map.fitBounds(bounds());});
  el('visible').addEventListener('change', showHistorical);
  el('basemap').addEventListener('change', showBase);
  el('fit').addEventListener('click', () => map.fitBounds(bounds()));
  el('retry').addEventListener('click', () => {showBase(); showHistorical();});
  el('opacity').addEventListener('input', event => {
    if (overlay) overlay.setOpacity(Number(event.target.value) / 100);
    el('percent').textContent = event.target.value + '%';
  });
  map.fitBounds(bounds());
  showBase();
  showHistorical();
})();
