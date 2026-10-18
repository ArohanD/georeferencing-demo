"""Fit the frozen affine experiment, warp a masked raster, validate COG, build assets."""
import csv, json, hashlib, math, sys, platform
from pathlib import Path
import numpy as np
import rasterio
from rasterio.transform import Affine, from_origin, from_bounds
from rasterio.warp import reproject, Resampling, transform_bounds
from rasterio.enums import ColorInterp
from rasterio.shutil import copy as rio_copy
from pyproj import Transformer, __version__ as projversion
from scipy.spatial import ConvexHull
from PIL import Image, ImageDraw
from rio_cogeo.cogeo import cog_validate

R=Path(__file__).resolve().parents[2]; O=R/'outputs'; O.mkdir(exist_ok=True)
assert hashlib.sha256((R/'data/original/collet-1770-loc-copy1.jp2').read_bytes()).hexdigest()=='ddda5ee92d091ed5aca1ee8d63d43b6f349264770073041ea4be60a523705591', 'Original scan differs from the inspected source.'
Image.MAX_IMAGE_PIXELS=None
points=list(csv.DictReader((R/'data/points/candidates.csv').open()))
lock=json.loads((R/'data/points/selection.json').read_text())
for n in ['fit','checks']:
 f=R/'data/points'/('fitting.csv' if n=='fit' else 'checks.csv')
 assert hashlib.sha256(f.read_bytes()).hexdigest()==lock[n+'_sha256'], 'Selection changed: explicitly version a new experiment.'
fit=[p for p in points if p['role']=='fit']; checks=[p for p in points if p['role']=='check']
for role,filename in [('fit','fitting.csv'),('check','checks.csv')]:
 assert [p for p in points if p['role']==role]==list(csv.DictReader((R/'data/points'/filename).open()))
t=Transformer.from_crs(4269,32119,always_xy=True)
def xy(p):return t.transform(float(p['longitude']),float(p['latitude']))
def pix(p):return [float(p['pixel_x']),float(p['pixel_y']),1.]
A=np.array([pix(p) for p in fit]); B=np.array([xy(p) for p in fit])
# Center/scale predictors for numerical stability; solve a full 6-parameter affine.
center=A[:,:2].mean(axis=0); scale=A[:,:2].std(axis=0)
Z=np.column_stack(((A[:,:2]-center)/scale,np.ones(len(A))))
coef=np.linalg.lstsq(Z,B,rcond=None)[0]
M=np.vstack((coef[:2]/scale[:,None],coef[2]-(center/scale)@coef[:2]))
aff=Affine(M[0,0],M[1,0],M[2,0],M[0,1],M[1,1],M[2,1])
errors=[]
for p in fit+checks:
 pred=np.array(pix(p))@M; target=np.array(xy(p)); delta=pred-target
 errors.append({'point_id':p['point_id'],'feature_name':p['feature_name'],'role':p['role'],'error_m':float(np.linalg.norm(delta)),'east_error_m':float(delta[0]),'north_error_m':float(delta[1]),'predicted_easting':float(pred[0]),'predicted_northing':float(pred[1]),'reference_easting':float(target[0]),'reference_northing':float(target[1])})
with (O/'errors.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=errors[0]);w.writeheader();w.writerows(errors)
stats={}
for role in ['fit','check']:
 e=np.array([r['error_m'] for r in errors if r['role']==role]);stats[role]={'n':len(e),'rmse_m':float(np.sqrt(np.mean(e**2))),'median_m':float(np.median(e)),'max_m':float(e.max())}
W,H=13949,9524
# Main map neatline; no inset observed. Conservative polygon excises cartouche,
# scale bar and border. Polygon is a visibility mask, never a geographic control.
mask_poly=[(700,700),(13350,700),(13350,5230),(12350,5230),(12050,6000),(11150,6500),(10550,6770),(9630,7020),(9060,7480),(9090,8400),(8580,8650),(650,8650)]
(R/'data/points/mask.json').write_text(json.dumps({'coordinate_system':'original image pixel-edge coordinates','main_map_polygon':mask_poly,'purpose':'Conservative decorative cartouche, border and scale-bar exclusion; no inset detected'},indent=2))
corners=np.array([[0,0,1],[W,0,1],[W,H,1],[0,H,1]])@M
res=100.; left=math.floor(corners[:,0].min()/res)*res; right=math.ceil(corners[:,0].max()/res)*res
bottom=math.floor(corners[:,1].min()/res)*res; top=math.ceil(corners[:,1].max()/res)*res
width=int(round((right-left)/res));height=int(round((top-bottom)/res)); dstaff=from_origin(left,top,res,res)
print('Affine fitted; errors (metres):',stats,flush=True)
src=Image.open(R/'data/original/collet-1770-loc-copy1.jp2').convert('RGB')
src.thumbnail((6975,4762),Image.Resampling.LANCZOS); sw,sh=src.size
rgba=np.zeros((4,sh,sw),dtype='uint8');rgba[:3]=np.moveaxis(np.asarray(src),2,0)
mask=Image.new('L',(sw,sh));ImageDraw.Draw(mask).polygon([(x*sw/W,y*sh/H) for x,y in mask_poly],fill=255);rgba[3]=np.asarray(mask)
source_aff=aff*Affine.scale(W/sw,H/sh)
dest=np.zeros((4,height,width),dtype='uint8')
reproject(rgba,dest,src_transform=source_aff,src_crs='EPSG:32119',dst_transform=dstaff,dst_crs='EPSG:32119',src_alpha=4,dst_alpha=4,resampling=Resampling.bilinear,num_threads=2)
tmp=O/'collet-intermediate.tif'
with rasterio.open(tmp,'w',driver='GTiff',width=width,height=height,count=4,dtype='uint8',crs='EPSG:32119',transform=dstaff,tiled=True,compress='deflate',blockxsize=512,blockysize=512) as ds:
 ds.write(dest);ds.colorinterp=(ColorInterp.red,ColorInterp.green,ColorInterp.blue,ColorInterp.alpha)
 ds.update_tags(status='PROVISIONAL town-proxy affine; not settlement reconstruction',source='Library of Congress g3900.ar150000',fit_rmse_m=stats['fit']['rmse_m'],check_rmse_m=stats['check']['rmse_m'])
cog=O/'collet-1770-provisional.cog.tif'
rio_copy(tmp,cog,driver='COG',compress='DEFLATE',blocksize=512,overview_resampling='AVERAGE',BIGTIFF='IF_SAFER')
valid,errs,warns=cog_validate(str(cog),strict=True)
with rasterio.open(cog) as ds:
 validation={'valid':valid,'errors':errs,'warnings':warns,'crs':str(ds.crs),'size':[ds.width,ds.height],'bands':ds.count,'color_interpretations':[c.name for c in ds.colorinterp],'overviews':ds.overviews(1),'image_structure':ds.tags(ns='IMAGE_STRUCTURE'),'bounds':list(ds.bounds),'resolution':list(ds.res),'alpha_nonzero_fraction':float(np.mean(ds.read(4,out_shape=(256,256))>0))}
 assert ds.crs.to_epsg()==32119 and ds.count==4 and ds.overviews(1) and 0<validation['alpha_nonzero_fraction']<1
assert valid,validation
(O/'cog-validation.json').write_text(json.dumps(validation,indent=2))
to_ll=Transformer.from_crs(32119,4326,always_xy=True)
to_web=Transformer.from_crs(4326,3857,always_xy=True)
markers=[]
for p in points:
 q=dict(p)
 if p['longitude']:
  q['latlng']=[float(p['latitude']),float(p['longitude'])]
 if p['pixel_x']:
  pred=np.array(pix(p))@M;lng,lat=to_ll.transform(*pred);q['predicted_latlng']=[lat,lng]
 markers.append(q)
hull=ConvexHull(A[:,:2]); hull_ll=[]
for i in list(hull.vertices)+[hull.vertices[0]]:
 lng,lat=to_ll.transform(*(A[i]@M));hull_ll.append([lat,lng])
# Fixed display bounds independent of fit/check errors. Detail views illustrate
# checking locations and the southeastern edge; these do not feed back into fit.
views=[{'name':'overview','bbox_ll':[-82.5,33.5,-75.2,36.9],'width':1800},
 {'name':'salem','bbox_ll':[-80.65,35.88,-79.98,36.35],'width':1000},
 {'name':'bath','bbox_ll':[-77.13,35.23,-76.48,35.72],'width':1000},
 {'name':'hertford','bbox_ll':[-76.8,35.96,-76.14,36.43],'width':1000},
 {'name':'cape-fear','bbox_ll':[-78.3,33.72,-77.62,34.38],'width':1000}]
for v in views:
 west,south,east,north=v['bbox_ll'];l,b=to_web.transform(west,south);rr,tt=to_web.transform(east,north)
 v['bbox_3857']=[l,b,rr,tt];v['height']=round(v['width']*(tt-b)/(rr-l));v['leaflet_bounds']=[[south,west],[north,east]]
 arr=np.zeros((4,v['height'],v['width']),dtype='uint8')
 reproject(dest,arr,src_transform=dstaff,src_crs='EPSG:32119',dst_transform=from_bounds(l,b,rr,tt,v['width'],v['height']),dst_crs='EPSG:3857',src_alpha=4,dst_alpha=4,resampling=Resampling.bilinear)
 Image.fromarray(np.moveaxis(arr,0,2)).save(O/(v['name']+'-overlay.png'))
singular=np.linalg.svd(M[:2],compute_uv=False)
report={'status':'PROVISIONAL: regional town-proxy experiment, not verified historical feature registration','model':'unweighted least-squares affine; 8 towns fit, 4 frozen checks','coefficient_rows':['pixel_x','pixel_y','constant'],'coefficients_to_EPSG32119':M.tolist(),'statistics':stats,'output_crs':'EPSG:32119 NAD83 / North Carolina, metres','resolution_m':res,'resampling':'Lanczos source reduction to approximately half dimensions, then bilinear affine warp; average overviews','source_dimensions':[W,H],'reduced_source_dimensions':[sw,sh],'mask':'data/points/mask.json; alpha band, transparent outside mask; no RGB nodata value','pixel_scale_singular_values_m':singular.tolist(),'anisotropy_ratio':float(singular.max()/singular.min()),'jacobian_determinant':float(np.linalg.det(M[:2])),'note':'Negative determinant expected because image y points down; affine has constant Jacobian and no local folding. Outside fit hull is extrapolation. Check errors include GNIS and symbol ambiguity. No polynomial/TPS fitted: insufficient exact controls, uneven coverage, no independent southern/western edge checks.','runtime':{'python':sys.version,'platform':platform.platform(),'rasterio':rasterio.__version__,'GDAL_bundled':rasterio.__gdal_version__,'PROJ_pyproj':projversion}}
(O/'transformation.json').write_text(json.dumps(report,indent=2))
(O/'views.json').write_text(json.dumps(views,indent=2))
(R/'data/points/preview.json').write_text(json.dumps({'points':markers,'views':views,'hull':hull_ll,'statistics':stats},indent=2))
print('COG validation:',validation,flush=True)
