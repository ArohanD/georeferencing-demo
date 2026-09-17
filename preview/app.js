'use strict';
fetch('data.json').then(r=>{if(!r.ok)throw Error('Cannot load local data');return r.json()}).then(d=>{
 const map=L.map('map',{minZoom:5,maxZoom:12});L.control.scale({imperial:false}).addTo(map);
 const layers=L.layerGroup().addTo(map);let base,overlay;
 const selector=document.getElementById('view');
 d.views.forEach(v=>{const o=document.createElement('option');o.value=v.name;o.textContent=v.name;selector.append(o)});
 const color={fit:'#1761a0',check:'#b44112',excluded:'#666'};
 d.points.filter(p=>p.role!=='excluded'&&p.latlng).forEach(p=>{
   const text=`${p.point_id} ${p.feature_name} (${p.role})<br>GNIS ${p.gnis_id}, NAD83 town proxy.<br>${p.matching_rationale}<br>${p.ambiguity}`;
   const marker=p.role==='check'?L.rectangle([[p.latlng[0]-.008,p.latlng[1]-.01],[p.latlng[0]+.008,p.latlng[1]+.01]],{color:color[p.role],fillOpacity:.85,weight:2}):L.circleMarker(p.latlng,{radius:6,color:color[p.role],fillOpacity:.85});
   marker.bindTooltip(`${p.point_id} ${p.feature_name}`).bindPopup(text).addTo(layers);
   L.circleMarker(p.predicted_latlng,{radius:5,color:color[p.role],fillOpacity:0,weight:2}).bindPopup(`${p.point_id}: transformed historical symbol`).addTo(layers);
   L.polyline([p.latlng,p.predicted_latlng],{color:color[p.role],weight:2}).addTo(layers);
 });
 L.polyline(d.hull,{color:'#333',weight:1.5,dashArray:'6 6'}).bindTooltip('Fitting-point convex hull; outside is extrapolation').addTo(layers);
 function show(){const v=d.views.find(v=>v.name===selector.value);if(base)map.removeLayer(base);if(overlay)map.removeLayer(overlay);base=L.imageOverlay(`../data/reference/${v.name}-modern.jpg`,v.leaflet_bounds,{attribution:'USGS The National Map'}).addTo(map);overlay=L.imageOverlay(`../outputs/${v.name}-overlay.png`,v.leaflet_bounds,{opacity:document.getElementById('opacity').value/100,attribution:'Library of Congress, Geography and Map Division'}).addTo(map);map.fitBounds(v.leaflet_bounds);}
 selector.addEventListener('change',show);document.getElementById('opacity').addEventListener('input',e=>{overlay.setOpacity(e.target.value/100);document.getElementById('percent').textContent=e.target.value+'%'});
 document.getElementById('points').addEventListener('change',e=>e.target.checked?map.addLayer(layers):map.removeLayer(layers));show();
}).catch(e=>{document.getElementById('error').textContent=e.message+' — serve the project with the README localhost command.'});
