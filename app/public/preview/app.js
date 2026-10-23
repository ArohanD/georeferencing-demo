'use strict';
(() => {
  const config = window.HISTORICAL_MAP_CONFIG;
  const el = id => document.getElementById(id);
  const map = L.map('map', {minZoom: 5, maxZoom: config.terrain.maxZoom});
  L.control.scale({imperial: false}).addTo(map);
  let base, overlay, terrain, terrainMode;
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
    el('layer-diagnostic').hidden = !el('visible').checked;
    el('layer-diagnostic').textContent = ' ' + layer.diagnostic + ' These are uncertain historical correspondences, not survey-grade accuracy estimates.';
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
      zIndex: 3, maxNativeZoom: 12, updateWhenIdle: true
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
      attribution: selected.attribution, maxNativeZoom: selected.maxZoom, maxZoom: config.terrain.maxZoom, zIndex: 1
    });
    monitor(base, 'base-status', selected.label).addTo(map);
  }

  config.terrain.modes.forEach(item => el('terrain').add(new Option(item.label, item.id)));
  el('terrain').value = config.terrain.defaultMode;
  config.terrain.examples.forEach(item => el('terrain-location').add(new Option(item.label, item.id)));
  config.terrain.slopeLegend.forEach(item => {
    const row = document.createElement('div');
    const swatch = document.createElement('img');
    swatch.src = item.image;
    swatch.alt = '';
    row.append(swatch, document.createTextNode(item.label));
    el('slope-legend').append(row);
  });

  function showTerrain(force = false) {
    const source = config.terrain.modes.find(item => item.id === el('terrain').value);
    const inBounds = map.getBounds().intersects(L.latLngBounds(config.terrain.bounds));
    const enabled = source.id !== 'none';
    const detailed = map.getZoom() >= config.terrain.minZoom;
    el('terrain-opacity').disabled = !enabled;
    el('terrain-key').hidden = !enabled;
    el('slope-legend').hidden = source.id !== 'slope';
    el('terrain-hint').textContent = !enabled ? 'Terrain hidden.' : !inBounds
      ? 'Outside North Carolina coverage. Choose NC overview or a river example.'
      : !detailed ? `Zoom in to level ${config.terrain.minZoom}+ to load terrain. Inspect here jumps to detail.`
      : map.getZoom() < 12 ? 'Terrain overview: zoom in or use Inspect here to examine banks and approaches. Transparent gaps mean no data.'
      : 'Inspect banks, terraces and approaches. Transparent gaps mean no data, not flat terrain.';
    if (overlay && map.hasLayer(overlay) && enabled && detailed) {
      el('terrain-hint').textContent += ' Historical map is visible; hide it for a clear terrain view.';
    }
    if (!enabled || !inBounds || !detailed) {
      if (terrain) map.removeLayer(terrain);
      terrain = null;
      status('terrain-status', 'Terrain hidden.');
      return;
    }
    if (!force && terrain && terrainMode === source.id) return;
    if (terrain) map.removeLayer(terrain);
    terrainMode = source.id;
    terrain = window.createTerrainLayer({...source, attribution: config.terrain.attribution}, {
      minZoom: config.terrain.minZoom, maxZoom: config.terrain.maxZoom,
      tileSize: 512, bounds: config.terrain.bounds, noWrap: true,
      opacity: Number(el('terrain-opacity').value) / 100,
      zIndex: 2, updateWhenIdle: true, keepBuffer: 1
    });
    monitor(terrain, 'terrain-status', source.label).addTo(map);
  }

  el('terrain').addEventListener('change', () => showTerrain());
  el('terrain-opacity').addEventListener('input', event => {
    if (terrain) terrain.setOpacity(Number(event.target.value) / 100);
    el('terrain-percent').textContent = event.target.value + '%';
  });
  el('terrain-location').addEventListener('change', () => {
    const example = config.terrain.examples.find(item => item.id === el('terrain-location').value);
    if (example.center) map.setView(example.center, config.terrain.inspectZoom);
    else map.fitBounds(config.terrain.bounds);
  });
  el('inspect').addEventListener('click', () => map.setZoom(Math.max(map.getZoom(), config.terrain.inspectZoom)));
  map.on('moveend', () => showTerrain());

  el('historical-layer').addEventListener('change', () => {showHistorical(); map.fitBounds(bounds());});
  el('visible').addEventListener('change', () => {showHistorical(); showTerrain();});
  el('basemap').addEventListener('change', showBase);
  el('fit').addEventListener('click', () => map.fitBounds(bounds()));
  el('retry').addEventListener('click', () => {showBase(); showHistorical(); showTerrain(true);});
  el('opacity').addEventListener('input', event => {
    if (overlay) overlay.setOpacity(Number(event.target.value) / 100);
    el('percent').textContent = event.target.value + '%';
  });
  const initial = config.terrain.examples.find(item => item.id === config.terrain.defaultExample);
  el('terrain-location').value = initial.id;
  // Shared links contain display settings only, never credentials or research data.
  function restoreView() {
    const state = window.ViewState.parse(location.hash, {
      base: config.basemaps, terrain: config.terrain.modes, historical: config.layers
    }, config.terrain.maxZoom);
    if (!state) return false;
    for (const [key, id] of [['base', 'basemap'], ['terrain', 'terrain'], ['historical', 'historical-layer']]) {
      if (state[key] !== undefined) el(id).value = state[key];
    }
    for (const [key, id, output] of [['opacity', 'opacity', 'percent'], ['terrainOpacity', 'terrain-opacity', 'terrain-percent']]) {
      if (state[key] !== undefined) {
        el(id).value = String(state[key]);
        el(output).textContent = el(id).value + '%';
      }
    }
    if (state.visible !== undefined) el('visible').checked = state.visible;
    if (state.center) {
      map.setView(state.center, state.zoom, {animate: false});
      if (![...el('terrain-location').options].some(option => option.value === 'shared')) {
        const option = new Option('Shared view', 'shared');
        option.disabled = true;
        el('terrain-location').add(option);
      }
      el('terrain-location').value = 'shared';
      return true;
    }
    return false;
  }
  // Establish a valid map before applying URL options; malformed values keep safe defaults.
  map.setView(initial.center, config.terrain.inspectZoom);
  const plants = window.createPlantLayer(map);
  restoreView();
  plants.restore(new URLSearchParams(location.hash.slice(1)), {initial: true});
  showBase();
  showHistorical();
  showTerrain();
  window.addEventListener('hashchange', () => {
    restoreView();
    plants.restore(new URLSearchParams(location.hash.slice(1)));
    showBase(); showHistorical(); showTerrain(true);
  });
  el('share-view').addEventListener('click', async () => {
    const center = map.getCenter().wrap();
    const params = window.ViewState.serialize({
      lat: center.lat, lng: center.lng, zoom: map.getZoom(),
      base: el('basemap').value, terrain: el('terrain').value,
      historical: el('historical-layer').value, visible: el('visible').checked,
      opacity: el('opacity').value, terrainOpacity: el('terrain-opacity').value
    });
    plants.serialize(params);
    const url = new URL(location.href);
    url.hash = params.toString();
    el('share-panel').hidden = false;
    el('share-url').value = url.href;
    el('share-status').textContent = 'Copy this link to reopen the same map view. Private previews require university GitHub access.';
    map.invalidateSize({pan: false});
    el('share-url').focus();
    el('share-url').select();
    try {
      await navigator.clipboard.writeText(url.href);
      el('share-status').textContent = 'Link copied. Private previews require university GitHub access.';
    } catch (_) {
      // The selectable link remains usable when clipboard access is unavailable or denied.
    }
  });
})();
