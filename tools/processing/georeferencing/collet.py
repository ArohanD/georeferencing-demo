"""Package the frozen Collet town-proxy experiment as APPROXIMATE ONLY.

Run from any directory with the repository .venv313 Python. Existing deliverables
are reused; source hashes and the frozen split are checked. No app files changed.
"""
import csv
import json
import math
import shutil
import numpy as np
import rasterio
from rasterio.transform import Affine, from_origin
from rasterio.warp import reproject, Resampling
from rasterio.enums import ColorInterp
from rasterio.shutil import copy as rio_copy
from pyproj import Transformer
from PIL import Image, ImageDraw
from common import ROOT, sha256, inspect_raster, web_cog, reference_preview, fetch_reference

O = ROOT/'deliverables/collet_1770'
D = ROOT/'data/historical_maps/collet_1770'
O.mkdir(parents=True, exist_ok=True); D.mkdir(parents=True, exist_ok=True)
source = ROOT/'data/original/collet-1770-loc-copy1.jp2'
metadata = json.loads((ROOT/'data/metadata/source.json').read_text())
assert sha256(source) == metadata['sha256']
metadata.update(local_path=str(source.relative_to(ROOT)), verification_date='2026-10-07',
                verification='Checksum matches preserved institutional download. Full overview re-inspected; title, main map, central sheet seam and cartouche confirmed.')
(D/'source.json').write_text(json.dumps(metadata, indent=2)+'\n')
lock = json.loads((ROOT/'data/points/selection.json').read_text())
points = []
for role, filename, hashkey in [('fit', 'fitting.csv', 'fit_sha256'), ('check', 'checks.csv', 'checks_sha256')]:
    f = ROOT/'data/points'/filename
    assert sha256(f) == lock[hashkey]
    rows = list(csv.DictReader(f.open())); points.extend(rows)
    shutil.copyfile(f, D/('control_points.csv' if role == 'fit' else 'checkpoints.csv'))
shutil.copyfile(ROOT/'data/points/candidates.csv', D/'legacy_candidates.csv')
(D/'point_conventions.json').write_text(json.dumps(lock | {
    'current_status':'approximate only',
    'acceptance':'Legacy proxies retained for reproduction, NOT accepted exact historical geographic controls. GNIS populated-place centers are not verified colonial settlement locations.'}, indent=2)+'\n')
t = Transformer.from_crs(4269, 32119, always_xy=True)
fit = [p for p in points if p['role'] == 'fit']
A = np.array([[float(p['pixel_x']),float(p['pixel_y']),1] for p in fit])
B = np.array([t.transform(float(p['longitude']),float(p['latitude'])) for p in fit])
center=A[:,:2].mean(0); scale=A[:,:2].std(0)
C=np.linalg.lstsq(np.column_stack(((A[:,:2]-center)/scale,np.ones(len(A)))),B,rcond=None)[0]
M=np.vstack((C[:2]/scale[:,None],C[2]-(center/scale)@C[:2]))
aff=Affine(M[0,0],M[1,0],M[2,0],M[0,1],M[1,1],M[2,1])
errors=[]
for p in points:
    target=np.array(t.transform(float(p['longitude']),float(p['latitude'])))
    pred=np.array([float(p['pixel_x']),float(p['pixel_y']),1])@M
    errors.append(dict(point_id=p['point_id'],role=p['role'],feature=p['feature_name'],error_m=float(np.linalg.norm(pred-target))))
with (D/'errors.csv').open('w', newline='') as f:
    writer=csv.DictWriter(f,fieldnames=errors[0]); writer.writeheader(); writer.writerows(errors)
stats={}
for role in ['fit','check']:
    e=np.array([v['error_m'] for v in errors if v['role']==role])
    stats[role]=dict(n=len(e),rmse_m=float(np.sqrt(np.mean(e**2))),min_m=float(e.min()),max_m=float(e.max()))
master=O/'collet_1770_approximate_master_32119.tif'
if not master.exists():
    # Rebuild from the immutable source and frozen proxy points, without touching pilot outputs.
    Image.MAX_IMAGE_PIXELS=None
    src=Image.open(source).convert('RGB'); W,H=src.size
    src.thumbnail((6975,4762),Image.Resampling.LANCZOS); sw,sh=src.size
    rgba=np.zeros((4,sh,sw),dtype='uint8');rgba[:3]=np.moveaxis(np.asarray(src),2,0)
    poly=json.loads((ROOT/'data/points/mask.json').read_text())['main_map_polygon']
    mask=Image.new('L',(sw,sh));ImageDraw.Draw(mask).polygon([(x*sw/W,y*sh/H) for x,y in poly],fill=255)
    rgba[3]=np.asarray(mask)
    corners=np.array([[0,0,1],[W,0,1],[W,H,1],[0,H,1]])@M
    res=100.;left=math.floor(corners[:,0].min()/res)*res;right=math.ceil(corners[:,0].max()/res)*res
    bottom=math.floor(corners[:,1].min()/res)*res;top=math.ceil(corners[:,1].max()/res)*res
    w=int((right-left)/res);h=int((top-bottom)/res); da=from_origin(left,top,res,res)
    arr=np.zeros((4,h,w),dtype='uint8')
    reproject(rgba,arr,src_transform=aff*Affine.scale(W/sw,H/sh),src_crs='EPSG:32119',dst_transform=da,dst_crs='EPSG:32119',src_alpha=4,dst_alpha=4,resampling=Resampling.bilinear,num_threads=2)
    tmp=O/'collet_master.working.tif'
    with rasterio.open(tmp,'w',driver='GTiff',width=w,height=h,count=4,dtype='uint8',crs='EPSG:32119',transform=da,tiled=True,compress='deflate',blockxsize=512,blockysize=512) as ds:
        ds.write(arr);ds.colorinterp=(ColorInterp.red,ColorInterp.green,ColorInterp.blue,ColorInterp.alpha)
        ds.update_tags(status='APPROXIMATE ONLY: legacy town proxies, no verified historical feature fit',source=metadata['resource_url'])
    rio_copy(tmp,master,driver='COG',compress='DEFLATE',blocksize=512,overview_resampling='AVERAGE');tmp.unlink()
master_info=inspect_raster(master)
web=O/'collet_1770_approximate_web_3857.tif'
web_info=web_cog(master,web,125)
previews=[]
fetch_reference(O,'full-extent',web_info['bounds'],1600)
Tweb=Transformer.from_crs(4326,3857,always_xy=True)
fetch_reference(O,'eno-haw',(*Tweb.transform(-79.4,35.65),*Tweb.transform(-78.7,36.25)),1100)
for name in ['full-extent','overview','salem','bath','cape-fear','eno-haw']:
    folder=O if name in ['eno-haw','full-extent'] else ROOT/'data/reference'
    jpg=folder/(name+'-modern.jpg'); meta=folder/(name+'-modern.json')
    if jpg.exists() and meta.exists():
        previews.append(reference_preview(web,jpg,meta,O/(name+'-comparison.jpg'),f'Collet 1770 / {name} / APPROXIMATE ONLY'))
qgis=['mapX,mapY,sourceX,sourceY,enable,dX,dY,residual']
for p in points:
    x,y=t.transform(float(p['longitude']),float(p['latitude']))
    qgis.append(f"{x},{y},{p['pixel_x']},{-float(p['pixel_y'])},{1 if p['role']=='fit' else 0},0,0,0")
(D/'collet_1770.points').write_text('\n'.join(qgis)+'\n')
manifest=dict(id='collet_1770',title=metadata['title'],date=1770,attribution=metadata['institution'],source_url=metadata['resource_url'],
              status='approximate only',accuracy_disclaimer='Town-symbol/GNIS proxies only; no defensible exact historical control fit established. Rectification does not establish accuracy of historical routes or locations.',
              master=master_info,web=web_info,output_raster_path=web_info['path'],bounds=web_info['geographic_bounds'],bounds_crs='EPSG:4326',
              suggested_layer_name='collet_1770',geoserver_base_url='https://vclvm176-164.vclgis.cnr.ncsu.edu/geoserver',workspace='pending',publication_status='pending',
              legacy_proxy_discrepancies=stats,independent_geographic_validation=None,previews=previews)
(D/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(D/'transformation.json').write_text(json.dumps(dict(coefficients_to_EPSG32119=M.tolist(),statistics=stats,method='legacy unweighted affine; frozen proxy split; no tuning',master_resolution_m=100,web_resolution_map_units=125,source_reduction='13949x9524 to 6975x4762 Lanczos; bilinear warp; average overviews',mask='data/points/mask.json',pixel_size_is_not_accuracy=True),indent=2)+'\n')
print(json.dumps(dict(deliverable=str(web),status=manifest['status'],legacy_proxy_discrepancies=stats),indent=2))
