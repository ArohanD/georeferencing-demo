"""Reproduce conservative coastal affine placement; no validated accuracy claim.
Run .venv313/bin/python tools/processing/georeferencing/moseley_1733.py [--fetch].
Frozen manually inspected points are in points.csv; checks never select the model.
"""
from pathlib import Path
import argparse,csv,json,hashlib,sys,html
import numpy as np
import requests,rasterio
from PIL import Image,ImageDraw
from pyproj import Transformer
from rasterio.control import GroundControlPoint
from rasterio.transform import from_gcps,from_bounds
from rasterio.warp import reproject,calculate_default_transform
from rasterio.enums import Resampling,ColorInterp
from rasterio.shutil import copy as rio_copy
from common import ROOT,sha256,inspect_raster,web_cog,fetch_reference,reference_preview
Image.MAX_IMAGE_PIXELS=None
D=ROOT/'deliverables/moseley_1733';M=ROOT/'data/historical_maps/moseley_1733'
URL='https://iiif.lib.ecu.edu/cantaloupe/iiif/2/00062315_0001.jp2/full/10000,/0/default.jpg'
SOURCE=D/'original-ecu-62315-10000.jpg'
def fetch():
 D.mkdir(parents=True,exist_ok=True)
 if not SOURCE.exists():
  r=requests.get(URL,timeout=180);r.raise_for_status();SOURCE.write_bytes(r.content)
 for name,bbox in [('overview',[-81,32.8,-75,36.8]),('fear',[-78.2,33.7,-77.7,34.2]),('middle',[-77.2,34.5,-76.4,35.3]),('northeast',[-76.5,35.1,-75.4,36.2]),('winyah',[-79.4,33,-78.8,33.6]),('eno-haw',[-79.5,35.5,-78.5,36.5])]:
  if (D/f'reference-{name}.jpg').exists():continue
  params=dict(bbox=','.join(map(str,bbox)),bboxSR=4326,imageSR=4326,size='1800,1200' if name=='overview' else '1200,1200',format='jpg',f='json')
  r=requests.get('https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/export',params=params,timeout=120);r.raise_for_status();j=r.json()
  (D/f'reference-{name}.json').write_text(json.dumps(dict(request_url=r.url,response=j),indent=2))
  r=requests.get(j['href'],timeout=120);r.raise_for_status();(D/f'reference-{name}.jpg').write_bytes(r.content)
def preview(name,raster):
 meta=json.loads((D/f'reference-{name}.json').read_text());e=meta['response']['extent'];im=Image.open(D/f'reference-{name}.jpg').convert('RGBA');w,h=im.size
 arr=np.zeros((4,h,w),np.uint8)
 with rasterio.open(raster) as s:reproject(rasterio.band(s,[1,2,3,4]),arr,dst_transform=from_bounds(e['xmin'],e['ymin'],e['xmax'],e['ymax'],w,h),dst_crs='EPSG:4326',src_alpha=4,dst_alpha=4,resampling=Resampling.bilinear)
 arr[3]=(arr[3]*.55).astype(np.uint8);blend=Image.alpha_composite(im,Image.fromarray(arr.transpose(1,2,0)))
 out=Image.new('RGB',(w*2,h+65),'white');out.paste(im,(0,65));out.paste(blend,(w,65));draw=ImageDraw.Draw(out)
 draw.text((12,8),f'Moseley 1733 | {name} | APPROXIMATE ONLY - coastal affine placement',fill='black');draw.text((12,28),'USGS The National Map (left); 55% historical overlay (right). Coastal change and interior distortion uncorrected.',fill='black');draw.text((12,46),'Rectification does not establish accuracy of historical routes or locations.',fill='black');out.save(D/f'preview-{name}.jpg',quality=93)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--fetch',action='store_true');args=ap.parse_args()
 if args.fetch:fetch()
 for rel,expected in json.loads((M/'input-checksums.json').read_text()).items():
  assert sha256(ROOT/rel)==expected, f'Changed frozen input {rel}; create a separately reviewed version'
 pts=list(csv.DictReader((M/'points.csv').open()));tr=Transformer.from_crs(4326,32119,always_xy=True)
 for p in pts:
  p['x'],p['y']=tr.transform(float(p['longitude']),float(p['latitude']))
 fit=[p for p in pts if p['status']=='fit'];gcps=[GroundControlPoint(row=float(p['line']),col=float(p['pixel']),x=p['x'],y=p['y']) for p in fit];aff=from_gcps(gcps)
 errs=[]
 for p in pts:
  x,y=aff*(float(p['pixel']),float(p['line']));errs.append(dict(point_id=p['point_id'],status=p['status'],dx_m=x-p['x'],dy_m=y-p['y'],error_m=float(np.hypot(x-p['x'],y-p['y']))))
 stats={k:dict(n=sum(e['status']==k for e in errs),rmse_m=float(np.sqrt(np.mean([e['error_m']**2 for e in errs if e['status']==k]))),max_m=max(e['error_m'] for e in errs if e['status']==k)) for k in ['fit','check']}
 (M/'errors.json').write_text(json.dumps(dict(method='affine',master_crs='EPSG:32119',affine=list(aff),errors=errs,statistics=stats,warning='Checks are independent but weak coastal morphology proxies; these are diagnostic discrepancies, not certified positional accuracy.'),indent=2))
 master=D/'moseley_1733-approximate-master.cog.tif'
 if not master.exists():
  im=Image.open(SOURCE).convert('RGB');w,h=im.size;mask=Image.new('L',(w,h),0);dr=ImageDraw.Draw(mask)
  # Conservative main-map crop excludes bottom inset strip and neatline margins.
  dr.rectangle((380,230,9720,6500),fill=255)
  # Retain southwest main geography left of inset without title cartouche.
  dr.polygon([(1700,6500),(2720,6500),(2720,7670),(1700,7670)],fill=255)
  src=np.empty((4,h,w),dtype=np.uint8);src[:3]=np.asarray(im).transpose(2,0,1);src[3]=np.asarray(mask)
  corners=[aff*(x,y) for x,y in [(0,0),(w,0),(0,h),(w,h)]];xs,ys=zip(*corners);res=100;ow=int(np.ceil((max(xs)-min(xs))/res));oh=int(np.ceil((max(ys)-min(ys))/res));outaff=from_bounds(min(xs),max(ys)-oh*res,min(xs)+ow*res,max(ys),ow,oh)
  temp=D/'moseley-working.tif'
  with rasterio.Env(GDAL_CACHEMAX=128),rasterio.open(temp,'w',driver='GTiff',width=ow,height=oh,count=4,dtype='uint8',crs='EPSG:32119',transform=outaff,tiled=True,blockxsize=512,blockysize=512,compress='deflate') as dst:
   reproject(src,rasterio.band(dst,[1,2,3,4]),src_transform=aff,src_crs='EPSG:32119',src_alpha=4,dst_alpha=4,resampling=Resampling.bilinear,num_threads=2,warp_mem_limit=128)
   dst.colorinterp=(ColorInterp.red,ColorInterp.green,ColorInterp.blue,ColorInterp.alpha);dst.update_tags(status='approximate only',method='four coastal proxies affine; insufficient interior control',accuracy='Not validated; 100m pixel size is not positional accuracy')
  del src,im,mask
  rio_copy(temp,master,driver='COG',compress='DEFLATE',blocksize=512,overview_resampling='AVERAGE');temp.unlink()
 masterinfo=inspect_raster(master);webinfo=web_cog(master,D/'moseley_1733-approximate-web.cog.tif',125)
 if args.fetch or (D/'full-modern.jpg').exists():
  ref,meta=fetch_reference(D,'full',webinfo['bounds'],1200)
  reference_preview(master,ref,meta,D/'preview-full-extent.jpg','Moseley 1733 | APPROXIMATE ONLY | full raster extent')
 for n in ['overview','fear','middle','northeast','winyah','eno-haw']:preview(n,master)
 # Full actual raster footprint PNG, including transparent outside-footprint areas.
 with rasterio.open(master) as s:
  arr=s.read(out_shape=(4,round(s.height*1800/s.width),1800));Image.fromarray(arr.transpose(1,2,0)).save(D/'full-extent.png')
 manifest=dict(id='moseley_1733',title='A New and Correct Map of the Province of North Carolina',date=1733,attribution='East Carolina University, J. Y. Joyner Library, East Carolina Manuscript Collection MC0017',source_url='https://digital.lib.ecu.edu/62315',source_scan=dict(path=str(SOURCE.relative_to(ROOT)),download_url=URL,dimensions=[10000,7918],bytes=SOURCE.stat().st_size,sha256=sha256(SOURCE)),status='approximate only',accuracy_disclaimer='Sparse coastal feature proxies and independent coastal diagnostic checks do not validate interior placement or historical routes. No independent interior accuracy estimate.',suggested_layer_name='moseley_1733',geoserver_base_url='https://vclvm176-164.vclgis.cnr.ncsu.edu/geoserver',workspace='pending',publication_status='pending',service_url=None,master=masterinfo,web=webinfo,validation=stats)
 manifest.update(output_raster_path=webinfo['path'],bounds=webinfo['geographic_bounds'],bounds_crs='EPSG:4326')
 (M/'manifest.json').write_text(json.dumps(manifest,indent=2))
 im=Image.open(SOURCE)
 im.crop((8400,6600,9700,7550)).save(D/'edition-1733-cartouche.jpg',quality=95)
 with (M/'qgis.points').open('w') as f:
  f.write('#CRS: EPSG:4326\nmapX,mapY,pixelX,pixelY,enable,dX,dY,residual\n')
  for p in pts:f.write(f"{p['longitude']},{p['latitude']},{p['pixel']},{-float(p['line'])},{int(p['status']=='fit')},0,0,0\n")
 for p in pts:
  x,y=float(p['pixel']),float(p['line']);box=(int(x)-400,int(y)-400,int(x)+400,int(y)+400);crop=im.crop(box);d=ImageDraw.Draw(crop);cx=x-box[0];cy=y-box[1];d.ellipse((cx-15,cy-15,cx+15,cy+15),outline='red',width=4);d.text((15,15),p['point_id']+' '+p['feature']+' | '+p['status'],fill='red');crop.save(D/(p['point_id']+'-historical.jpg'),quality=95)
  ref=Image.open(D/('reference-'+p['reference_name']+'.jpg'));x,y=float(p['reference_pixel']),float(p['reference_line']);d=ImageDraw.Draw(ref);d.ellipse((x-12,y-12,x+12,y+12),outline='red',width=4);d.text((15,15),p['point_id']+' '+p['feature'],fill='red');ref.save(D/(p['point_id']+'-modern.jpg'),quality=95)
 packet=['<!doctype html><html lang="en"><meta charset="utf-8"><title>Moseley 1733 review packet</title><style>body{font:17px sans-serif;margin:2em;max-width:1500px}img{width:48%;vertical-align:top}section{border-top:1px solid #bbb;margin-top:2em}</style><h1>Moseley 1733 — approximate only</h1><p>Historical original-resolution crops (left); USGS modern references (right). Red circles mark the observed proxy positions. These are not monuments. Four points fit the affine; two were held out. Diagnostic check RMSE 20.45 km. Review coastal morphology before accepting any proxy; interior Eno–Haw placement has no independent control.</p><p>Exact ambiguity: do the historic cape/island tips and inlet mouth denote comparable geography after shoreline migration? M06 Winyah is especially doubtful because modern jetties and barrier geometry differ. Any improved fit needs independently evidenced interior correspondences and new held-out checks.</p>']
 for p in pts:
  pid=p['point_id'];packet.append(f'<section><h2>{pid}: {html.escape(p["feature"])}</h2><p>{p["status"]}; {html.escape(p["confidence"])}</p><img src="{pid}-historical.jpg" alt="Annotated historical crop"><img src="{pid}-modern.jpg" alt="Annotated USGS modern reference"></section>')
 packet.append('<p>Rectification does not establish accuracy of historical routes or locations.</p></html>');(D/'review.html').write_text('\n'.join(packet))
 print(json.dumps(stats,indent=2));print(master)
if __name__=='__main__':main()
