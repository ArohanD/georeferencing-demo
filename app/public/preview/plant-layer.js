'use strict';
// Isolated optional layer; shared app owns the map and URL serialization.
window.createPlantLayer = function (map) {
  const taxa = [
    {id: 55844, name: 'Vinca minor', label: 'Lesser periwinkle', code: 'Vm', color: '#6331a0', clue: 'May persist around old homesites and cemeteries in North Carolina. Modern landscaping and spreading garden escapes can look similar; a sighting does not establish a historic site.'},
    {id: 53326, name: 'Vinca major', label: 'Greater periwinkle', code: 'VM', color: '#136c78', clue: 'May reflect earlier ornamental planting around homesites. Also spreads through suburban woodland; the stronger local cemetery association concerns Vinca minor. A sighting cannot date land use.'},
    {id: 53597, name: 'Narcissus', label: 'Daffodils · genus incl. species/hybrids', code: 'N', color: '#8b6500', clue: 'Long-lived bulbs may survive former gardens or cemetery plantings. Modern gardens and discarded bulbs are alternatives. This genus-level group includes species and hybrids; sightings cannot date planting.'},
    {id: 126583, name: 'Hemerocallis fulva', label: 'Orange daylily', code: 'Hf', color: '#b83e13', clue: 'May persist or escape from former homesteads and cemeteries. Modern planting and roadside spread are common alternatives; a sighting does not locate a former building.'}
  ];
  const byId = new Map(taxa.map(t => [t.id, t]));
  const el = id => document.getElementById(id);
  const selected = new Set(taxa.map(t => t.id));
  const group = L.layerGroup();
  const renderer = L.canvas({padding: 0.3});
  let dataset, loading = false, loadError = false;
  const markers = new Map();
  const counts = new Map(taxa.map(t => [t.id, 0]));
  let selectedMarkers = [];
  const container = el('plant-taxa');
  for (const taxon of taxa) {
    const label = document.createElement('label');
    const input = document.createElement('input');
    input.type = 'checkbox'; input.checked = true; input.value = taxon.id;
    input.id = `plant-${taxon.id}`;
    const badge = document.createElement('span');
    badge.className = 'plant-badge'; badge.style.backgroundColor = taxon.color;
    badge.textContent = taxon.code;
    const text = document.createElement('span');
    text.textContent = `${taxon.name} — ${taxon.label}`;
    const count = document.createElement('span');
    count.id = `plant-count-${taxon.id}`;
    label.append(input, badge, text, count); container.append(label);
    const tip = document.createElement('div');
    tip.id = `plant-clue-${taxon.id}`; tip.className = 'plant-clue';
    tip.setAttribute('role', 'tooltip'); tip.textContent = taxon.clue;
    tip.hidden = true; document.body.append(tip);
    input.setAttribute('aria-describedby', tip.id);
    let hideTimer;
    const hideTip = () => { clearTimeout(hideTimer); tip.hidden = true; };
    const showTip = () => {
      clearTimeout(hideTimer); tip.hidden = false;
      const rect = label.getBoundingClientRect();
      tip.style.left = `${Math.max(8, Math.min(rect.left, innerWidth - tip.offsetWidth - 8))}px`;
      const top = rect.top >= tip.offsetHeight + 14 ? rect.top - tip.offsetHeight - 6 : rect.bottom + 6;
      tip.style.top = `${Math.max(8, Math.min(top, innerHeight - tip.offsetHeight - 8))}px`;
    };
    // Mounted outside the scrolling legend so the explanation is never clipped.
    label.addEventListener('mouseenter', showTip);
    label.addEventListener('mouseleave', () => { hideTimer = setTimeout(hideTip, 150); });
    input.addEventListener('focus', showTip);
    input.addEventListener('blur', hideTip);
    tip.addEventListener('mouseenter', () => clearTimeout(hideTimer));
    tip.addEventListener('mouseleave', hideTip);
    document.addEventListener('keydown', event => { if (event.key === 'Escape') hideTip(); });
    document.addEventListener('scroll', hideTip, true);
    window.addEventListener('resize', hideTip);
    input.addEventListener('change', () => {
      hideTip();
      if (input.checked) selected.add(taxon.id); else selected.delete(taxon.id);
      render();
    });
  }
  function popup(feature) {
    const p = feature.properties;
    const div = document.createElement('div'); div.className = 'plant-popup';
    const heading = document.createElement('strong');
    heading.textContent = `${p.taxon_name} (${p.taxon_rank})`; div.append(heading);
    const quality = {research: 'Research Grade', needs_id: 'Needs ID — identification not settled', casual: 'Casual — review source identification and evidence'};
    const cultivation = {cultivated: 'Marked cultivated', not_marked_cultivated: 'Not marked cultivated (not proof of wild origin)', unknown: 'Cultivation status unknown'};
    for (const line of [
      `Observed: ${p.observed_on || 'date unknown'}`,
      `Identification: ${quality[p.quality_grade] || 'Unknown'}`,
      cultivation[p.cultivation] || cultivation.unknown,
      `Reported location accuracy: ${p.accuracy_m} m (not independently verified)`,
      `Observer credit: ${p.attribution}`,
      `Observation license: ${p.license.toUpperCase()}${p.license === 'cc-by-nc' ? ' · noncommercial use only' : ''}`,
      `Retrieved: ${p.retrieved_at.slice(0, 10)}`,
      'Possible land-use clue; not evidence of a historic site or occupation date.'
    ]) {
      const row = document.createElement('p'); row.textContent = line; div.append(row);
    }
    // Construct source URL from validated numeric ID; never trust a downloaded href.
    const link = document.createElement('a');
    link.href = `https://www.inaturalist.org/observations/${feature.id}`;
    link.target = '_blank'; link.rel = 'noopener noreferrer'; link.textContent = 'Original iNaturalist observation';
    div.append(link);
    return div;
  }
  function validate(data) {
    if (data.type !== 'FeatureCollection' || !Array.isArray(data.features) ||
        data.metadata?.status !== 'success' || data.metadata?.validation?.complete !== true ||
        !/^\d{4}-\d{2}-\d{2}T/.test(data.metadata.retrieved_at) ||
        data.metadata.feature_count !== data.features.length ||
        typeof data.metadata.config?.area?.label !== 'string' ||
        !Number.isFinite(data.metadata.config?.accuracy_metres) || data.metadata.config.accuracy_metres <= 0) throw Error('Invalid dataset');
    const ids = new Set();
    for (const f of data.features) {
      const p = f.properties, c = f.geometry?.coordinates;
      if (f.type !== 'Feature' || !Number.isSafeInteger(f.id) || f.id <= 0 || ids.has(f.id) ||
          f.geometry?.type !== 'Point' || !Array.isArray(c) || c.length !== 2 ||
          !c.every(Number.isFinite) || Math.abs(c[0]) > 180 || Math.abs(c[1]) > 90 ||
          !p || !byId.has(p.group_id) || !Number.isFinite(p.accuracy_m) || p.accuracy_m < 0 ||
          p.accuracy_m > data.metadata.config.accuracy_metres ||
          !['cc0', 'cc-by', 'cc-by-nc'].includes(p.license) ||
          !['taxon_name', 'taxon_rank', 'attribution', 'retrieved_at'].every(k => typeof p[k] === 'string')) throw Error('Invalid observation');
      ids.add(f.id);
    }
    return data;
  }
  async function load() {
    if (loading || dataset) return;
    loading = true; loadError = false; render();
    const abort = new AbortController();
    const timeout = setTimeout(() => abort.abort(), 30000);
    try {
      const response = await fetch('preview/plants/observations.geojson', {signal: abort.signal});
      if (!response.ok) throw Error('Dataset unavailable');
      dataset = validate(await response.json());
      for (const f of dataset.features) {
        const t = byId.get(f.properties.group_id);
        const marker = L.circleMarker([f.geometry.coordinates[1], f.geometry.coordinates[0]], {
          renderer, radius: 4, color: t.color, fillColor: t.color, fillOpacity: 0.65, weight: 1
        });
        marker.bindPopup(() => popup(f));
        marker.bindTooltip(() => {
          const text = document.createElement('span');
          text.textContent = `${t.code} · ${f.properties.taxon_name}`; return text;
        });
        markers.set(f.id, marker);
        counts.set(t.id, counts.get(t.id) + 1);
      }
    } catch (_) {
      dataset = undefined; markers.clear(); group.clearLayers();
      counts.forEach((_, id) => counts.set(id, 0)); loadError = true;
    } finally {
      clearTimeout(timeout); loading = false; render();
    }
  }
  function render() {
    const enabled = el('plants-visible').checked;
    if (enabled && !map.hasLayer(group)) group.addTo(map);
    if (!enabled && map.hasLayer(group)) map.removeLayer(group);
    selectedMarkers = [];
    if (dataset) {
      for (const f of dataset.features) {
        const marker = markers.get(f.id);
        if (selected.has(f.properties.group_id)) {
          selectedMarkers.push(marker);
          if (enabled && !group.hasLayer(marker)) group.addLayer(marker);
        } else if (group.hasLayer(marker)) {
          group.removeLayer(marker);
        }
      }
    }
    for (const t of taxa) {
      el(`plant-${t.id}`).checked = selected.has(t.id);
      el(`plant-count-${t.id}`).textContent = dataset ? `(${counts.get(t.id)} in dataset)` : '';
    }
    el('plant-retry').hidden = !loadError;
    updateStatus();
  }
  // Panning only updates the viewport count, not filters or marker membership.
  function updateStatus() {
    const enabled = el('plants-visible').checked;
    const total = selectedMarkers.length;
    const bounds = map.getBounds();
    const visible = enabled ? selectedMarkers.filter(marker => bounds.contains(marker.getLatLng())).length : 0;
    el('plant-status').textContent = !enabled ? 'Plant layer off.' : loading ? 'Loading observations…' : loadError ?
      'Plant data could not be loaded. Other map layers remain available. Retry plants.' : !dataset ? '' :
      selected.size === 0 ? 'No taxa selected. Select a taxon or use Select all.' :
      `${total.toLocaleString()} observations selected in dataset; ${visible.toLocaleString()} in map view.${total === 0 ? ' No matching observations.' : ''}`;
  }
  el('plants-visible').addEventListener('change', () => {
    render(); if (el('plants-visible').checked) load();
  });
  el('plant-all').addEventListener('click', () => { taxa.forEach(t => selected.add(t.id)); render(); });
  el('plant-clear').addEventListener('click', () => { selected.clear(); render(); });
  el('plant-retry').addEventListener('click', load);
  el('plant-extent').addEventListener('click', () => {
    if (dataset?.features.length) map.fitBounds(L.latLngBounds(dataset.features.map(f => [f.geometry.coordinates[1], f.geometry.coordinates[0]])));
  });
  el('plant-details').addEventListener('toggle', () => map.invalidateSize({pan: false}));
  map.on('moveend', updateStatus);
  function restore(params, {initial = false} = {}) {
    if (initial) el('plants-visible').checked = false;
    if (params.get('view') !== '1') return;
    el('plants-visible').checked = !initial && params.get('plants') === '1';
    selected.clear();
    const values = params.has('plantTaxa') ? params.get('plantTaxa').split(',') : taxa.map(t => String(t.id));
    for (const value of values) if (taxa.some(t => String(t.id) === value)) selected.add(Number(value));
    render(); if (el('plants-visible').checked) load();
  }
  render();
  return {
    restore,
    serialize(params) {
      params.set('plants', el('plants-visible').checked ? '1' : '0');
      params.set('plantTaxa', taxa.filter(t => selected.has(t.id)).map(t => t.id).join(','));
    }
  };
};
