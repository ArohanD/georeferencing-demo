"""Frozen-placement independent coarse check and annotated human review packet.
Run after mouzon_1775.py --fetch. This script NEVER changes transformation.
"""
import json,csv
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
from pyproj import Transformer
import rasterio
from rasterio.windows import Window
from common import ROOT
D=ROOT/'deliverables/mouzon_1775';M=ROOT/'data/historical_maps/mouzon_1775'
# Selected visually after affine coefficients were frozen in placement.json.
# New Bern north-bank Trent/Neuse junction: coarse shoreline point, not town centroid.
historical=(12000+906*2300/1600,2600+762*2300/1600)
modern_pixel=(445,320)
j=json.loads((D/'neuse_trent_review-modern.json').read_text());e=j['response']['extent']
x=e['xmin']+(modern_pixel[0]+.5)/900*(e['xmax']-e['xmin']);y=e['ymax']-(modern_pixel[1]+.5)/700*(e['ymax']-e['ymin'])
lon,lat=Transformer.from_crs(3857,4326,always_xy=True).transform(x,y)
p=json.loads((M/'placement.json').read_text());a,b,c,d,f,g=p['transform'];hlon=a*historical[0]+b*historical[1]+c;hlat=d*historical[0]+f*historical[1]+g
T=Transformer.from_crs(4326,5070,always_xy=True);mx,my=T.transform(lon,lat);hx,hy=T.transform(hlon,hlat);err=float(np.hypot(mx-hx,my-hy))
row=dict(point_id='C01',pixel=historical[0],line=historical[1],reference_x=lon,reference_y=lat,reference_crs='EPSG:4326',feature_description='North-bank cusp at Trent/Neuse junction at New Bern; coarse estuarine shoreline correspondence, not a town centroid',evidence='Historical crop [12000,2600,2200,2300], resized to 1530x1600; selected display (906,762). USGS neuse_trent_review-modern.jpg selected display (445,320), center-of-pixel; returned extent in paired JSON',confidence='medium-low: shore modification and broad estuarine junction; allow ~1 km correspondence uncertainty',status='independent_coarse_check_not_used_for_fit',error_m_epsg5070=err)
with (M/'checkpoints.csv').open('w') as out:
 w=csv.DictWriter(out,fieldnames=list(row));w.writeheader();w.writerow(row)
review={'checkpoint':row,'historical_predicted_longitude':hlon,'historical_predicted_latitude':hlat,'reference_pixel':modern_pixel,'independent_error_m':err,'interpretation':'One coarse shoreline check only; not spatially distributed validation. No correction or tuning used. Unknown correspondence uncertainty; approximate 1 km visual tolerance is an assessment, not measured uncertainty.','rejected_candidates':[{'id':'R01','feature':'Eno/Little/Flat junction east of Hillsborough','reason':'Modern USGS shows Falls Lake reservoir at the network; historical branches ambiguous and pre-impoundment authoritative reference needed.'},{'id':'R02','feature':'New River and Bogue inlets','reason':'Dynamic barrier inlets; modern shoreline correspondence not defensible without change-history evidence.'},{'id':'R03','feature':'Hillsborough town symbol','reason':'Historical symbol/court-house identity requires site evidence; modern town centroid not used.'}]}
(M/'review.json').write_text(json.dumps(review,indent=2))
with rasterio.open(D/'original.jp2') as s:
 for name,w,box,label in [('neuse-trent-candidate',(12000,2600,2200,2300),(13180,3570,13430,3830),'C01: Trent / Neuse north-bank cusp. Coarse check only.'),('eno-haw-candidate',(8500,300,3300,2200),(9980,1380,10350,1750),'R01: Eno/Little/Flat junction. Modern reservoir obscures correspondence.'),('coastal-inlets-candidate',(11800,4000,2400,2200),(12500,5200,13200,5700),'R02: Bogue/New River inlets. Dynamic shoreline; rejected.')]:
  arr=s.read(window=Window(*w));im=Image.fromarray(arr.transpose(1,2,0));im.thumbnail((1600,1600));sx=im.width/w[2];sy=im.height/w[3];dr=ImageDraw.Draw(im);dr.rectangle([(box[0]-w[0])*sx,(box[1]-w[1])*sy,(box[2]-w[0])*sx,(box[3]-w[1])*sy],outline='red',width=4);dr.rectangle((0,0,im.width,25),fill='white');dr.text((5,5),label,fill='black');im.save(D/(name+'-annotated.png'))
ref=Image.open(D/'neuse_trent_review-modern.jpg').convert('RGB');dr=ImageDraw.Draw(ref);u,v=modern_pixel;dr.ellipse((u-8,v-8,u+8,v+8),outline='red',width=3);dr.text((u+12,v),'C01 coarse shoreline check',fill='red');ref.save(D/'neuse-trent-modern-annotated.png')
manifest_path=M/'manifest.json'
if manifest_path.exists():
 m=json.loads(manifest_path.read_text());m['validation'].update(independent_checkpoints=1,checkpoint_rmse_m=err,checkpoint_scope='One coarse estuarine shoreline check only, roughly 1 km correspondence uncertainty; not spatial validation');manifest_path.write_text(json.dumps(m,indent=2))
print(json.dumps(review,indent=2))
