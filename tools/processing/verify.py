"""Offline audit of provenance, numerical results, COG packaging and preview assets."""
import csv, json, hashlib, math, subprocess
from pathlib import Path
from html.parser import HTMLParser
import numpy as np
import rasterio
from pyproj import Transformer
from rio_cogeo.cogeo import cog_validate
from PIL import Image
R=Path(__file__).resolve().parents[2];O=R/'outputs'
manifest=json.loads((R/'data/metadata/input-checksums.json').read_text())
for path,expected in manifest.items():
 assert hashlib.sha256((R/path).read_bytes()).hexdigest()==expected, f'Input snapshot changed: {path}'
points=list(csv.DictReader((R/'data/points/candidates.csv').open()))
fit={p['point_id'] for p in points if p['role']=='fit'};checks={p['point_id'] for p in points if p['role']=='check'}
assert len(fit)==8 and len(checks)==4 and not fit&checks
tr=json.loads((O/'transformation.json').read_text());M=np.array(tr['coefficients_to_EPSG32119']);T=Transformer.from_crs(4269,32119,always_xy=True)
err={r['point_id']:r for r in csv.DictReader((O/'errors.csv').open())}
for p in points:
 if p['point_id'] not in fit|checks:continue
 pred=np.array([float(p['pixel_x']),float(p['pixel_y']),1])@M
 target=np.array(T.transform(float(p['longitude']),float(p['latitude'])))
 assert abs(np.linalg.norm(pred-target)-float(err[p['point_id']]['error_m']))<1e-6
for role,ids in [('fit',fit),('check',checks)]:
 rmse=math.sqrt(sum(float(err[i]['error_m'])**2 for i in ids)/len(ids))
 assert abs(rmse-tr['statistics'][role]['rmse_m'])<1e-6
valid,errors,warnings=cog_validate(str(O/'collet-1770-provisional.cog.tif'),strict=True);assert valid and not errors and not warnings
with rasterio.open(O/'collet-1770-provisional.cog.tif') as ds:
 assert ds.crs.to_epsg()==32119 and ds.res==(100,100)
 assert ds.count==4 and ds.colorinterp[3].name=='alpha' and ds.overviews(1)==[2,4,8,16]
 alpha=ds.read(4,out_shape=(200,200));assert alpha.min()==0 and alpha.max()==255
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  self.links.extend(v for k,v in attrs if k in ['src','href'])
for page in [R/'app/public/preview/index.html', R/'research/review.html']:
 parser=Links();parser.feed(page.read_text())
 for link in parser.links:
  if not link.startswith(('https:','http:','#')):assert (page.parent/link).exists(),link
d=json.loads((R/'data/points/preview.json').read_text())
for v in d['views']:
 for p in [R/'data/reference'/(v['name']+'-modern.jpg'),O/(v['name']+'-overlay.png')]:
  with Image.open(p) as im:im.verify()
 assert (O/(v['name']+'-comparison.png')).is_file()
try:subprocess.run(['node','--check',str(R/'app/public/preview/app.js')],check=True,capture_output=True)
except FileNotFoundError:print('Node unavailable: JS syntax check skipped.')
result={'input_files_checked':len(manifest),'fitting_count':8,'checking_count':4,'numeric_errors_recomputed':True,'cog_strict_validation':'passed','alpha_crs_resolution_overviews':'passed','preview_local_links_and_images':'passed','interactive_browser_test':'not run; no browser engine installed'}
(O/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
