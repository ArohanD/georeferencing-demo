"""Fetch bounded USGS exports; preserve exact requests, returned extents and hashes.
Network required on first run. Existing responses are reused. No tile crawling.
"""
import csv, json, hashlib, io, concurrent.futures
from pathlib import Path
from urllib.parse import urlencode
import requests
from PIL import Image
from pyproj import Transformer
R=Path(__file__).resolve().parents[2];D=R/'data/reference';D.mkdir(exist_ok=True)
T=Transformer.from_crs(4269,3857,always_xy=True)
jobs=json.loads((R/'outputs/views.json').read_text())
for p in csv.DictReader((R/'data/points/candidates.csv').open()):
 if p['longitude']:
  x,y=T.transform(float(p['longitude']),float(p['latitude']))
  jobs.append({'name':p['point_id'],'bbox_3857':[x-6000,y-6000,x+6000,y+6000],'width':600,'height':600})
base='https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/export'
def fetch(v):
 name=v['name'];jpg=D/(name+'-modern.jpg');meta=D/(name+'-modern.json')
 if jpg.exists() and meta.exists():return name+' cached'
 params={'bbox':','.join(map(str,v['bbox_3857'])),'bboxSR':3857,'imageSR':3857,'size':f"{v['width']},{v['height']}",'format':'jpg','transparent':'false','f':'json'}
 url=base+'?'+urlencode(params);res=requests.get(url,timeout=120);res.raise_for_status();j=res.json()
 if 'error' in j:raise RuntimeError(j)
 data=requests.get(j['href'],timeout=120);data.raise_for_status();im=Image.open(io.BytesIO(data.content));assert im.size==(v['width'],v['height'])
 # Export may adjust requested extent to image aspect ratio. Save returned extent;
 # all display/comparison code uses it, not an assumed extent.
 jpg.write_bytes(data.content);meta.write_text(json.dumps({'request_url':url,'response':j,'sha256':hashlib.sha256(data.content).hexdigest(),'credit':'USGS The National Map; full attribution in data/metadata/usgs-topo-service.json'},indent=2))
 return name+' downloaded'
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 for result in pool.map(fetch,jobs):print(result,flush=True)
