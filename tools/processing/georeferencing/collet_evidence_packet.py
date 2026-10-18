"""Generate candidate-only review crops; never add these candidates to a fit."""
import csv,hashlib,json,shutil
from pathlib import Path
from urllib.parse import urlencode
import requests
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[3]
D=R/'data/historical_maps/collet_1770/evidence'; O=R/'deliverables/collet_1770/evidence'
O.mkdir(parents=True,exist_ok=True); D.mkdir(parents=True,exist_ok=True)
Image.MAX_IMAGE_PIXELS=None
items=[
 dict(id='C01',name='Haw-Deep river junction',box=[5900,3150,7100,4050],pixel=[6640,3675],bbox=[-79.1,35.53,-78.95,35.69],decision='Candidate only: identify modern channel-center junction, then assess historical persistence. USGS places Jordan Dam 4.1 miles upstream; this junction is not the flooded Haw-New Hope junction.'),
 dict(id='C02',name='Trent-Neuse river junction',box=[9700,4350,10600,5250],pixel=[10135,4678],bbox=None,decision='Candidate only: decide whether stylized bank apex or channel-center junction is represented. Modern Trent mouth is an estuary; do not substitute the nearby USGS gauge or New Bern town proxy.'),
 dict(id='C03',name='Haw-New Hope junction',box=[6250,3000,7150,4050],pixel=[6560,3390],bbox=[-79.1,35.53,-78.95,35.69],decision='Exclude as modern shoreline control. Original confluence inundated by Jordan Lake; needs pre-impoundment topographic mapping and historical channel assessment.'),
 dict(id='C04',name='Yadkin-Uwharrie candidate junction',box=[4200,3500,5600,4400],pixel=[4870,4150],bbox=[-80.13,35.3,-80.02,35.42],decision='Exclude pending confirmation of historical tributary label and pre-impoundment geometry. Modern junction lies at Lake Tillery; reservoir shoreline is not a historical channel control.')]
im=None
for p in items:
 out=O/(p['id']+'-historical.jpg')
 if not out.exists():
  if im is None: im=Image.open(R/'data/original/collet-1770-loc-copy1.jp2')
  c=im.crop(p['box']).convert('RGB');d=ImageDraw.Draw(c);x=p['pixel'][0]-p['box'][0];y=p['pixel'][1]-p['box'][1]
  d.ellipse((x-16,y-16,x+16,y+16),outline='#cc0000',width=3);d.line((x-28,y,x+28,y),fill='#cc0000',width=2);d.line((x,y-28,x,y+28),fill='#cc0000',width=2)
  d.rectangle((0,0,c.width,30),fill='white');d.text((8,8),f"{p['id']} CANDIDATE ONLY - original image pixel {p['pixel']}",fill='black');c.save(out)
 if p['id']=='C02':
  shutil.copyfile(R/'data/reference/P06-modern.jpg',O/(p['id']+'-modern.jpg'))
  shutil.copyfile(R/'data/reference/P06-modern.json',D/(p['id']+'-modern.json'))
 elif p['id']=='C03' and (O/'C01-modern.jpg').exists():
  shutil.copyfile(O/'C01-modern.jpg',O/(p['id']+'-modern.jpg'))
  shutil.copyfile(D/'C01-modern.json',D/(p['id']+'-modern.json'))
 elif not (O/(p['id']+'-modern.jpg')).exists():
  params=dict(bbox=','.join(map(str,p['bbox'])),bboxSR=4326,imageSR=3857,size='900,900',format='jpg',f='json')
  url='https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/export?'+urlencode(params)
  j=requests.get(url,timeout=90).json()
  if 'href' not in j:raise RuntimeError(j)
  body=requests.get(j['href'],timeout=90).content
  (O/(p['id']+'-modern.jpg')).write_bytes(body)
  (D/(p['id']+'-modern.json')).write_text(json.dumps(dict(request_url=url,response=j,sha256=hashlib.sha256(body).hexdigest(),credit='USGS The National Map and contributors',purpose='Search window; no modern control coordinate accepted'),indent=2))
(D/'candidates.json').write_text(json.dumps(dict(status='candidate review only; excluded from all transformations',pixel_convention='Original-image pixel-edge coordinates: x right, y down, upper-left outer corner (0,0). Crops are native resolution; original x=crop x+left and original y=crop y+top. Crosshairs are visually selected approximate channel junctions, not accepted GCPs.',candidates=items),indent=2))
with (D/'candidates.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['point_id','feature','pixel_x','pixel_y','reference_x','reference_y','reference_crs','confidence','role','evidence','ambiguity'])
 for q in items:
  w.writerow([q['id'],q['name'],*q['pixel'],'','','','unresolved historical-modern match','excluded_candidate','evidence/README.md; '+q['id']+'-modern.json',q['decision']])
html='<html><meta charset="utf-8"><title>Collet natural-feature review</title><style>body{font:17px system-ui;max-width:1500px;margin:auto}img{width:48%;vertical-align:top}section{margin:30px 0}</style><h1>Collet: natural-feature candidates, NOT fitted controls</h1><p>Historical and modern panels are independently framed. Red historical crosshairs identify candidates. No modern coordinates have been accepted and no accuracy is claimed. Scan: Library of Congress; modern maps: USGS The National Map. Modern panels show search regions, not accepted targets.</p>'
for p in items:html+=f'<section><h2>{p["id"]}: {p["name"]}</h2><img src="{p["id"]}-historical.jpg"><img src="{p["id"]}-modern.jpg"><p>{p["decision"]}</p><p>Native source crop {p["box"]}; approximate candidate pixel {p["pixel"]}. Each crop is unscaled.</p></section>'
(O/'review.html').write_text(html+'</html>')
print(O/'review.html')
