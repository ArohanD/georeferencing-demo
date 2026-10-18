"""Create local comparison evidence from public USGS basemap exports."""
from datetime import datetime, timezone
import json
from pathlib import Path
import requests
from pyproj import Transformer
from common import ROOT, sha256, reference_preview
from colonial_maps import IDS, NOTICE


def fetch(out, name, bounds, width=1400):
    image = out/f'{name}-modern.jpg'; meta = out/f'{name}-modern.json'
    if image.exists() and meta.exists(): return image, meta
    h = round(width*(bounds[3]-bounds[1])/(bounds[2]-bounds[0]))
    u = 'https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/export'
    r = requests.get(u, params=dict(f='json', bbox=','.join(map(str, bounds)), bboxSR=3857, imageSR=3857, size=f'{width},{h}', format='jpg'), timeout=120)
    r.raise_for_status(); j = r.json()
    if 'error' in j: raise RuntimeError(j['error'])
    r2 = requests.get(j['href'], timeout=120); r2.raise_for_status(); image.write_bytes(r2.content)
    meta.write_text(json.dumps(dict(request_url=r.url, response=j, sha256=sha256(image), credit='USGS The National Map', accessed=datetime.now(timezone.utc).isoformat()), indent=2)+'\n')
    return image, meta


def main():
    choices=[]; t=Transformer.from_crs(4326,3857,always_xy=True)
    for ident in IDS:
        d=ROOT/'data/historical_maps'/ident;o=ROOT/'deliverables'/ident
        m=json.loads((d/'manifest.json').read_text()); evidence=[]
        for name,bounds in [('coastal-overview',m['web']['bounds']),('new-bern',(*t.transform(-77.4,34.8),*t.transform(-76.7,35.4)))]:
            image,meta=fetch(o,name,bounds)
            evidence.append(reference_preview(ROOT/m['web']['path'],image,meta,o/f'{name}-comparison.jpg',m['title']+' / '+name))
        (d/'visual-review.json').write_text(json.dumps(dict(previews=evidence,notice=NOTICE,interpretation='Substantial coastline and town discrepancies remain. These raster comparisons are not precise crossing-location evidence.'),indent=2)+'\n')
        b=m['web']['geographic_bounds'];choices.append(dict(id=ident,title=m['title'],bounds=[[b[1],b[0]],[b[3],b[2]]],rmse=round(m['diagnostic']['check']['rmse_m']/1000,1),credit=m['source']['institution'],rights=m['source']['rights']))
    # Diagnostic viewer stays in ignored deliverables; main application is unchanged until WMS publishing succeeds.
    html='''<!doctype html><html lang="en"><meta charset="utf-8"><title>Colonial map alignment review</title>
<link rel="stylesheet" href="../app/public/preview/leaflet.css"><style>body{margin:0;font:15px system-ui}header{padding:10px}#map{height:78vh}label,button{margin-right:12px}p{margin:8px 0}</style>
<header><strong>Colonial map alignment review — local raster previews</strong><p>NOTICE</p><label>Map <select id="layers"></select></label><label>Opacity <input id="opacity" type="range" min="0" max="100" value="55"></label><button id="fit">Fit</button><label><input id="show" type="checkbox" checked> Show</label><span id="diagnostic"></span><p id="credit"></p></header><div id="map"></div>
<script src="../app/public/preview/leaflet.js"></script><script>
const maps=CONFIG;const map=L.map('map');L.tileLayer('https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}',{maxZoom:16,attribution:'USGS The National Map and contributors'}).addTo(map);
const select=document.getElementById('layers'),opacity=document.getElementById('opacity'),show=document.getElementById('show');let overlay;
for(const m of maps){const o=document.createElement('option');o.value=m.id;o.textContent=m.title;select.append(o)}
function current(){return maps.find(m=>m.id===select.value)}function load(){if(overlay)map.removeLayer(overlay);const m=current();overlay=L.imageOverlay(m.id+'/rectified-overview.png',m.bounds,{opacity:opacity.value/100});if(show.checked)overlay.addTo(map);map.fitBounds(m.bounds);document.getElementById('diagnostic').textContent=m.rmse+' km RMSE / 3 uncertain cape proxies';document.getElementById('credit').textContent=m.credit+'. '+m.rights;}
select.onchange=load;opacity.oninput=()=>overlay.setOpacity(opacity.value/100);show.onchange=()=>show.checked?overlay.addTo(map):map.removeLayer(overlay);document.getElementById('fit').onclick=()=>map.fitBounds(current().bounds);load();window.reviewMap=map;
</script></html>'''.replace('NOTICE',NOTICE).replace('CONFIG',json.dumps(choices))
    (ROOT/'deliverables/colonial-review.html').write_text(html)


if __name__=='__main__':main()
