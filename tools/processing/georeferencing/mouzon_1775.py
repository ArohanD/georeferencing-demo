"""Reproduce explicitly APPROXIMATE Mouzon graticule placement. No modern fit.
Run with .venv313/bin/python tools/processing/georeferencing/mouzon_1775.py [--fetch].
Outputs reused, never overwritten. Inputs original pixels (upper-left corner 0,0;
x right, y down). Graticule ticks are single-coordinate constraints, NOT GCPs.
"""
import argparse,csv,json,math,sys
from pathlib import Path
import numpy as np
import requests,rasterio
from rasterio import Affine
from rasterio.enums import ColorInterp
from rasterio.features import geometry_mask
from rasterio.shutil import copy as rio_copy
from pyproj import Transformer
from PIL import Image,ImageDraw
from common import ROOT,sha256,inspect_raster,web_cog,reference_preview
D=ROOT/'deliverables/mouzon_1775'; M=ROOT/'data/historical_maps/mouzon_1775'
URL='https://tile.loc.gov/storage-services/service/gmd/gmd390/g3900/g3900/ar139400.jp2'
D.mkdir(parents=True,exist_ok=True);M.mkdir(parents=True,exist_ok=True)
args=argparse.ArgumentParser();args.add_argument('--fetch',action='store_true');opt=args.parse_args()
def fetch(url,path):
 if not path.exists():
  r=requests.get(url,timeout=180);r.raise_for_status();path.write_bytes(r.content)
 if path.stat().st_size==0:raise ValueError(path)
if opt.fetch:
 fetch('https://www.loc.gov/item/74692510/?fo=json',M/'loc-item.json');fetch(URL,D/'original.jp2')
assert sha256(D/'original.jp2') == '5d24c388552b938ea0c208630dd37acce9924c634752a533eae5b0a6bd3d1fce', 'Source checksum changed; do not reuse points'
# Manually read from original-resolution crops scaled by 0.5. Approx. +/-10 px.
# London zero is provisionally equated with Greenwich, NOT established historically.
ticks=[('L01',2047,336,'longitude',-83),('L02',4079,321,'longitude',-82),('L03',14300,299,'longitude',-77),('L04',16330,300,'longitude',-76),('L05',2167,12138,'longitude',-83),('L06',4185,12120,'longitude',-82),('L07',14334,12068,'longitude',-77),('L08',16350,12054,'longitude',-76),('B01',250,644,'latitude',36.5),('B02',16780,565,'latitude',36.5),('B03',365,11886,'latitude',32),('B04',16790,11789,'latitude',32)]
with (M/'graticule_ticks.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['point_id','pixel','line','coordinate_axis','printed_degrees','status','evidence','confidence']);w.writerows([(*t,'initial_placement_only','Original LOC image border tick, visually inspected crops; London zero assumed Greenwich','high tick identification; low geodetic interpretation') for t in ticks])
for name in ['control_points','checkpoints']:
 p=M/(name+'.csv')
 if not p.exists():p.write_text('point_id,pixel,line,reference_x,reference_y,reference_crs,feature_description,evidence,confidence,status\n')
coef=[];residuals=[]
for axis in ['longitude','latitude']:
 rows=[t for t in ticks if t[3]==axis]; A=np.array([[t[1],t[2],1] for t in rows]);b=np.array([t[4] for t in rows]);c=np.linalg.lstsq(A,b,rcond=None)[0];coef.append(c)
 # EQC local metric component residuals, not 2-D modern positional errors.
 scale=111319.49079327358*(math.cos(math.radians(34)) if axis=='longitude' else 1)
 residuals += [{'point_id':t[0],'axis':axis,'residual_degrees':float(r),'component_residual_m_local_eqc':float(r*scale)} for t,r in zip(rows,A@c-b)]
cx,cy=coef;aff=Affine(cx[0],cx[1],cx[2],cy[0],cy[1],cy[2])
(M/'placement.json').write_text(json.dumps({'method':'affine graticule placement only; not modern georeferencing','transform':list(aff)[:6],'source_crs_assumption':'EPSG:4326, printed London longitude provisionally equated to Greenwich; plate-carree assumption','metric_residual_crs':'+proj=eqc +lat_ts=34 +lon_0=-80 +datum=WGS84 +units=m','residuals':residuals,'independent_checkpoint_count':0,'independent_rmse_m':None,'pixel_convention':'upper-left corner (0,0); columns right and lines down; original 17109 x 12467 scan','tick_selection_precision_pixels':10,'main_map_polygon_pixels':[[270,365],[16770,310],[16790,12040],[370,12140]],'excluded_inset_rectangle_pixels':[11350,8700,16800,12100]},indent=2))
source=D/'original.jp2'; master=D/'mouzon_1775-approximate-master.tif'
if not master.exists():
 temp=D/'mouzon-master.working.tif'
 with rasterio.Env(GDAL_CACHEMAX=128),rasterio.open(source) as s:
  p=dict(driver='GTiff',height=s.height,width=s.width,count=4,dtype='uint8',crs='EPSG:4326',transform=aff,tiled=True,blockxsize=512,blockysize=512,compress='deflate',BIGTIFF='IF_SAFER')
  with rasterio.open(temp,'w',**p) as d:
   for b in [1,2,3]:d.write(s.read(b),b)
   poly={'type':'Polygon','coordinates':[[[270,365],[16770,310],[16790,12040],[370,12140],[270,365]]]}
   for _,win in d.block_windows(4):
    mask=geometry_mask([poly],(int(win.height),int(win.width)),Affine.translation(win.col_off,win.row_off),invert=True)
    yy,xx=np.ogrid[int(win.row_off):int(win.row_off+win.height),int(win.col_off):int(win.col_off+win.width)]
    mask &= ~((xx>=11350)&(xx<=16800)&(yy>=8700)&(yy<=12100))
    d.write(mask.astype('uint8')*255,4,window=win)
   d.colorinterp=(ColorInterp.red,ColorInterp.green,ColorInterp.blue,ColorInterp.alpha)
   d.update_tags(status='approximate only',method='Affine printed graticule, London/Greenwich assumed',accuracy='Unvalidated. No modern control points or independent checkpoints. Not for route location.')
 rio_copy(temp,master,driver='COG',compress='DEFLATE',blocksize=512,overview_resampling='AVERAGE');temp.unlink()
print('Master',master,flush=True)
web=D/'mouzon_1775-approximate-3857.tif';web_meta=web_cog(master,web,100)
master_meta=inspect_raster(master)
# Pin modern maps only for visual review, never use them to tune this placement.
views=[('full_extent',web_meta['geographic_bounds']),('eno_haw_hillsborough',[-79.7,35.45,-78.6,36.35]),('cape_fear',[-78.35,33.7,-77.55,34.5]),('albemarle',[-77.0,35.7,-75.5,36.5]),('neuse_trent_review',[-77.13,35.02,-76.95,35.16])]
T=Transformer.from_crs(4326,3857,always_xy=True);previews=[]
for name,bbox in views:
 img=D/(name+'-modern.jpg');meta=D/(name+'-modern.json')
 if opt.fetch and not meta.exists():
  xmin,ymin=T.transform(*bbox[:2]);xmax,ymax=T.transform(*bbox[2:]);p={'bbox':f'{xmin},{ymin},{xmax},{ymax}','bboxSR':3857,'imageSR':3857,'size':'900,700','format':'jpg','f':'json'}
  r=requests.get('https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/export',params=p,timeout=180);r.raise_for_status();j=r.json()
  if 'error' in j:raise RuntimeError(j)
  fetch(j['href'],img);meta.write_text(json.dumps({'request_url':r.url,'response':j,'sha256':sha256(img),'credit':'USGS The National Map'},indent=2))
 if meta.exists():previews.append(reference_preview(web,img,meta,D/(name+'-comparison.png'),'Mouzon 1775 APPROXIMATE ONLY - '+name))
manifest={'id':'mouzon_1775','title':'An Accurate Map of North and South Carolina','date':1775,'attribution':'Library of Congress, Geography and Map Division','source_url':'https://www.loc.gov/item/74692510/','status':'approximate only','georeferencing_status':'approximate only','accuracy_disclaimer':'Unvalidated graticule placement with assumed London/Greenwich equivalence and affine plate-carree geometry. Zero modern fitting controls. One coarse independent shoreline check available in validation/review; insufficient spatial validation. Rectification does not establish accuracy of historical routes or locations.','geoserver_base_url':'https://vclvm176-164.vclgis.cnr.ncsu.edu/geoserver','suggested_layer_name':'mouzon_1775','workspace':'pending','publication_status':'pending','master':master_meta,'web':web_meta,'output_raster_path':str(web.relative_to(ROOT)),'bounds':web_meta['geographic_bounds'],'bounds_crs':'EPSG:4326','previews':previews,'validation':{'modern_fit_points':0,'independent_checkpoints':0,'fit_rmse_m':None,'checkpoint_rmse_m':None}}
(M/'manifest.json').write_text(json.dumps(manifest,indent=2))
j=json.loads((M/'loc-item.json').read_text());(M/'source.json').write_text(json.dumps({'catalog_url':'https://www.loc.gov/item/74692510/','download_url':URL,'institution':'Library of Congress','attribution':manifest['attribution'],'rights_statement':j['item']['rights'],'dimensions':[17109,12467],'file_bytes':source.stat().st_size,'sha256':sha256(source),'source_path':str(source.relative_to(ROOT)),'original_map_date':'1775-05-30 visibly printed; catalog 1775','reproduction_date':None,'digital_derivative':'LOC full-pixel-resolution JP2; 17109x12467; TIFF dimensions not separately verified. JPEG2000 may be lossy; output compression is lossless. TIFF master advertised 639920700 bytes, JP2 chosen to avoid redundant bulky acquisition.','visual_inspection':'Title and printed May 30 1775 verified. North and South Carolina with Georgia, western Indian frontiers. Two inset maps (Port Royal and Charlestown) excluded from alpha. Multiple cloth-mounted section seams and fold damage preserved.'},indent=2))
# Annotated source packet, explicitly graticule only, with transform of preview coords.
with rasterio.open(source) as s:
 a=s.read(out_shape=(3,1458,2000));im=Image.fromarray(a.transpose(1,2,0));draw=ImageDraw.Draw(im)
 for pid,x,y,axis,value in ticks:
  u=x*2000/s.width;v=y*1458/s.height;draw.ellipse((u-5,v-5,u+5,v+5),outline='red',width=2);draw.text((max(0,min(1900,u+6)),max(0,min(1430,v+6))),f'{pid} {value}',fill='red')
 im.save(D/'graticule-review.png')
print(json.dumps({'manifest':str(M/'manifest.json'),'web':str(web),'previews':len(previews)},indent=2),flush=True)

if (D/'neuse_trent_review-modern.json').exists():
 import runpy
 runpy.run_path(str(ROOT/'tools/processing/georeferencing/mouzon_review.py'))
