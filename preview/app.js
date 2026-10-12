'use strict';
(() => {
  const config = window.HISTORICAL_MAP_CONFIG;
  const el = id => document.getElementById(id);
  const map = L.map('map', {minZoom: 5, maxZoom: 12});
  L.control.scale({imperial: false}).addTo(map);
  const points = L.layerGroup();
  let data, base, overlay;
  const selection = () => config.layers.find(layer => layer.id === el('historical-layer').value);
  const view = () => data && data.views.find(v => v.name === el('view').value);
  const bounds = () => selection() ? selection().bounds : view().leaflet_bounds;
  const status = (id, message, failed = false) => {
    el(id).textContent = message;
    el(id).style.color = failed ? '#a21c12' : '';
  };

  // Keep errors local to the affected layer. Removing a layer cancels its timeout.
  function monitor(layer, id, label, tiled) {
    let timer, failures = 0;
    const active = () => map.hasLayer(layer);
    function loading() {
      clearTimeout(timer);
      failures = 0;
      status(id, `${label}: loading…`);
      timer = setTimeout(() => {
        if (active()) status(id, `${label}: taking too long. Retry imagery or choose a local layer.`, true);
      }, config.timeoutMs);
    }
    layer.on('add', loading);
    if (tiled) layer.on('loading', loading);
    layer.on(tiled ? 'tileerror' : 'error', () => {
      failures++;
      if (active()) status(id, `${label}: imagery unavailable or incomplete. Retry imagery or choose a local layer.`, true);
    });
    layer.on('load', () => {
      clearTimeout(timer);
      if (active()) status(id, failures ? `${label}: some imagery failed. Retry imagery or choose a local layer.` : `${label}: loaded.`, failures > 0);
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
  const localOption = new Option('Collet 1770 · local pilot overlay', 'local');
  localOption.disabled = true;
  el('historical-layer').add(localOption);

  function syncPoints() {
    const applicable = data && (!selection() || selection().id === 'collet_1770');
    el('points').disabled = !applicable;
    if (applicable && el('points').checked) points.addTo(map);
    else map.removeLayer(points);
  }

  function showHistorical() {
    if (overlay) map.removeLayer(overlay);
    const layer = selection();
    el('diagnostic').textContent = layer ? layer.diagnostic : config.layers[0].diagnostic + ' Local pilot preview.';
    syncPoints();
    if (!el('visible').checked) {
      status('layer-status', 'Historical map hidden.');
      return;
    }
    const opacity = Number(el('opacity').value) / 100;
    if (layer) {
      if (!layer.available) return;
      overlay = L.tileLayer.wms(config.endpoint, {
        layers: layer.name, version: config.version, format: config.format,
        transparent: true, styles: '', crs: L.CRS.EPSG3857,
        bounds: layer.bounds, opacity, attribution: layer.attribution,
        zIndex: 2, updateWhenIdle: true
      });
    } else {
      const v = view();
      overlay = L.imageOverlay(`../outputs/${v.name}-overlay.png`, v.leaflet_bounds, {
        opacity, zIndex: 2, attribution: config.layers[0].attribution
      });
    }
    monitor(overlay, 'layer-status', layer ? layer.label : 'Local Collet overlay', !!layer).addTo(map);
  }

  function showBase() {
    if (base) map.removeLayer(base);
    const local = el('basemap').value === 'local';
    if (local) {
      const v = view();
      base = L.imageOverlay(`../data/reference/${v.name}-modern.jpg`, v.leaflet_bounds, {
        attribution: 'USGS The National Map', zIndex: 1
      });
    } else {
      base = L.tileLayer(config.basemap.url, {
        attribution: config.basemap.attribution, maxZoom: 19, zIndex: 1
      });
    }
    monitor(base, 'base-status', local ? 'USGS local reference (selected view only)' : 'OpenStreetMap', !local).addTo(map);
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
  el('points').addEventListener('change', syncPoints);
  el('view').addEventListener('change', () => {
    if (el('basemap').value === 'local') showBase();
    if (!selection()) showHistorical();
    map.fitBounds(view().leaflet_bounds);
  });
  map.fitBounds(bounds());
  showBase();
  showHistorical();

  // Local reference failure must not prevent the live WMS viewer from working.
  fetch('data.json').then(response => {
    if (!response.ok) throw Error('Cannot load local reference data');
    return response.json();
  }).then(d => {
    data = d;
    d.views.forEach(v => el('view').add(new Option(v.name, v.name)));
    el('view').disabled = false;
    el('basemap').querySelector('[value="local"]').disabled = false;
    localOption.disabled = false;
    const color = {fit: '#1761a0', check: '#b44112', excluded: '#666'};
    d.points.filter(p => p.role !== 'excluded' && p.latlng).forEach(p => {
      const text = `${p.point_id} ${p.feature_name} (${p.role})\nGNIS ${p.gnis_id}, NAD83 town proxy.\n${p.matching_rationale}\n${p.ambiguity}`;
      const popup = document.createElement('div');
      popup.textContent = text;
      popup.style.whiteSpace = 'pre-line';
      const tooltip = document.createElement('span');
      tooltip.textContent = `${p.point_id} ${p.feature_name}`;
      const marker = p.role === 'check'
        ? L.rectangle([[p.latlng[0] - .008, p.latlng[1] - .01], [p.latlng[0] + .008, p.latlng[1] + .01]], {color: color[p.role], fillOpacity: .85, weight: 2})
        : L.circleMarker(p.latlng, {radius: 6, color: color[p.role], fillOpacity: .85});
      marker.bindTooltip(tooltip).bindPopup(popup).addTo(points);
      const symbolPopup = document.createElement('span');
      symbolPopup.textContent = `${p.point_id}: transformed historical symbol`;
      L.circleMarker(p.predicted_latlng, {radius: 5, color: color[p.role], fillOpacity: 0, weight: 2}).bindPopup(symbolPopup).addTo(points);
      L.polyline([p.latlng, p.predicted_latlng], {color: color[p.role], weight: 2}).addTo(points);
    });
    L.polyline(d.hull, {color: '#333', weight: 1.5, dashArray: '6 6'})
      .bindTooltip('Fitting-point convex hull; outside is extrapolation').addTo(points);
    syncPoints();
  }).catch(error => {
    el('error').textContent = `${error.message}. Local overlays and points are unavailable; the live map remains usable. Serve the project using the README localhost command.`;
  });
})();
