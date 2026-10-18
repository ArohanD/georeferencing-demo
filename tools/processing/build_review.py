"""Offline static comparisons, annotated point crops, review page, viewer bounds."""
import csv, json, html, os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parents[2]/'.cache/matplotlib'))
os.environ.setdefault('XDG_CACHE_HOME',str(Path(__file__).resolve().parents[2]/'.cache'))
import numpy as np
from PIL import Image, ImageDraw
import rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_bounds
from pyproj import Transformer
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[2];O=R/'outputs';D=R/'data/reference';Q=O/'review';Q.mkdir(exist_ok=True)
Image.MAX_IMAGE_PIXELS=None
data=json.loads((R/'data/points/preview.json').read_text());points=data['points']
web=Transformer.from_crs(4269,3857,always_xy=True);ll=Transformer.from_crs(3857,4326,always_xy=True)
colors={'fit':'#1761a0','check':'#b44112','excluded':'#666666'}
with rasterio.open(O/'collet-1770-provisional.cog.tif') as src:
 for v in data['views']:
  j=json.loads((D/(v['name']+'-modern.json')).read_text())['response'];e=j['extent'];bounds=[e[k] for k in ['xmin','ymin','xmax','ymax']]
  west,south=ll.transform(*bounds[:2]);east,north=ll.transform(*bounds[2:]);v['leaflet_bounds']=[[south,west],[north,east]]
  modern=Image.open(D/(v['name']+'-modern.jpg')).convert('RGBA');w,h=modern.size
  arr=np.zeros((4,h,w),dtype='uint8')
  reproject(rasterio.band(src,[1,2,3,4]),arr,src_transform=src.transform,src_crs=src.crs,dst_transform=from_bounds(*bounds,w,h),dst_crs='EPSG:3857',src_alpha=4,dst_alpha=4,resampling=Resampling.bilinear)
  overlay=Image.fromarray(np.moveaxis(arr,0,2));overlay.save(O/(v['name']+'-overlay.png'))
  trans=overlay.copy();trans.putalpha(trans.getchannel('A').point(lambda x:round(x*.5)));blend=Image.alpha_composite(modern,trans)
  fig,axes=plt.subplots(1,3,figsize=(18,7),layout='constrained')
  for ax,img,title in zip(axes,[modern,overlay,blend],['Modern USGS reference','Provisional Collet affine','50% overlay + displacement']):
   ax.set_facecolor('#dddddd');ax.imshow(img);ax.set_title(title);ax.axis('off')
  def pos(latlon):
   y,x=latlon;xx,yy=web.transform(x,y);return ((xx-bounds[0])/(bounds[2]-bounds[0])*w,(bounds[3]-yy)/(bounds[3]-bounds[1])*h)
  for p in points:
   if p['role']=='excluded' or 'latlng' not in p:continue
   x,y=pos(p['latlng']);px,py=pos(p['predicted_latlng'])
   if 0<x<w and 0<y<h:
    for ax in [axes[0],axes[2]]:
     ax.plot(x,y,'o' if p['role']=='fit' else '^',color=colors[p['role']],ms=6);ax.annotate(p['point_id'],(x,y),xytext=(4,4),textcoords='offset points',fontsize=8)
    axes[2].plot([x,px],[y,py],color=colors[p['role']],lw=1.2);axes[2].plot(px,py,'x',color=colors[p['role']])
  fig.suptitle(f"The Listening Machine — {v['name']} — PROVISIONAL, check RMSE 8.0 km\nBlue circles: fit / orange triangles: check / crosses: transformed symbols",fontsize=12)
  fig.supxlabel('Historical scan: Library of Congress, Geography and Map Division. Modern: USGS The National Map. No settlement-level accuracy claimed.',fontsize=8)
  fig.savefig(O/(v['name']+'-comparison.png'),dpi=160);plt.close(fig)
(R/'data/points/preview.json').write_text(json.dumps(data,indent=2))
im=Image.open(R/'data/original/collet-1770-loc-copy1.jp2')
thumb=im.copy();thumb.thumbnail((2400,2400));thumb.save(O/'source-overview.jpg')
for name,box in {'northwest':(2700,1400,7300,4000),'northeast':(8500,1400,12300,3900),'central':(6000,3900,11000,6600),'south':(7600,5600,10800,8300),'legend':(600,570,2600,830)}.items():
 crop=im.crop(box);crop.thumbnail((2100,1500));crop.save(O/('crop-'+name+'.jpg'))
cards=[]
for p in points:
 pid=p['point_id'];name=p['feature_name'];imgs=''
 if p['pixel_x']:
  x,y=float(p['pixel_x']),float(p['pixel_y']);box=(round(x)-350,round(y)-350,round(x)+350,round(y)+350)
  c=im.crop(box).convert('RGB');dr=ImageDraw.Draw(c);dr.ellipse((340,340,360,360),outline='#0066ff',width=3);dr.line((325,350,375,350),fill='#0066ff',width=2);dr.line((350,325,350,375),fill='#0066ff',width=2)
  dr.rectangle((0,0,700,30),fill='white');dr.text((8,8),f'{pid} {name}: source pixel ({x:g}, {y:g})',fill='black');c.save(Q/(pid+'-historical.jpg'))
  imgs+=f'<img alt="Annotated historical {html.escape(name)} symbol" src="../outputs/review/{pid}-historical.jpg">'
 if p['longitude']:
  c=Image.open(D/(pid+'-modern.jpg')).convert('RGB');j=json.loads((D/(pid+'-modern.json')).read_text())['response']['extent'];x,y=web.transform(float(p['longitude']),float(p['latitude']));cx=(x-j['xmin'])/(j['xmax']-j['xmin'])*c.width;cy=(j['ymax']-y)/(j['ymax']-j['ymin'])*c.height
  dr=ImageDraw.Draw(c);dr.ellipse((cx-8,cy-8,cx+8,cy+8),outline='#c04000',width=3);dr.line((cx-20,cy,cx+20,cy),fill='#c04000',width=2);dr.line((cx,cy-20,cx,cy+20),fill='#c04000',width=2)
  c.save(Q/(pid+'-modern.jpg'));imgs+=f'<img alt="USGS modern view centered at GNIS {html.escape(name)} proxy" src="../outputs/review/{pid}-modern.jpg">'
 decision='Accept or revise the town-symbol center and the GNIS town proxy for REGIONAL use. If revising, supply an independently sourced colonial-core coordinate, its CRS and citation. Do not move a point just to improve residuals.'
 if pid=='P13':decision='Does the Nixonton symbol refer to the same colonial core as the GNIS point? Supply independent historic evidence before admitting it.'
 if pid=='P14':decision='Locate the Brunswick Town archaeological footprint (not modern Brunswick), and determine whether a town-center or church anchor is defensible. Supply sourced coordinates and CRS.'
 if pid=='P15':decision='Resolve Cross Creek versus Campbellton using a documented colonial plan; identify the represented town core and supply its coordinates and CRS.'
 if pid=='P16':decision='Identify the Haw–Deep junction on the original image and a sourced modern channel junction; assess channel change or impoundment. Leave blank if uncertain.'
 cards.append(f'<article><h2>{pid} {html.escape(name)} — {p["role"]}</h2><div class="images">{imgs}</div><p>Pixel: {p["pixel_x"] or "unresolved"}, {p["pixel_y"] or "unresolved"}. Reference longitude, latitude: {p["longitude"] or "unresolved"}, {p["latitude"] or "unresolved"} ({p["reference_crs"] or "no CRS assigned"}); GNIS ID {p["gnis_id"] or "none"}.</p><p>{html.escape(p["matching_rationale"])} {html.escape(p["ambiguity"])}</p><p><b>Decision requested:</b> {decision}</p></article>')
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Collet point review</title><style>body{font:17px system-ui;max-width:1100px;margin:30px auto;padding:0 20px;background:#f8f5ee;color:#242424}article{border-top:2px solid #ccc;padding:20px 0}.images{display:flex;gap:12px}.images img{width:48%;object-fit:contain;align-self:start}h2{font-size:21px}a{color:#13598c}</style><h1>Collet 1770: one consolidated review request</h1><p>The processing attempt is complete. Review is optional for this provisional regional demonstration, but needed before stronger historical claims. Blue crosshairs are selected historical symbols; orange crosshairs are USGS GNIS town proxies on modern USGS maps. Views are independently centered, not evidence of alignment.</p><p>Edit <a href="../data/points/review.csv" download>review.csv</a>: accept, reject or revise; preserve IDs and include a source and CRS for any correction. Original columns remain the baseline. Highest priorities: Bath and New Bern, followed by excluded Brunswick Town and Cross Creek. All 16 candidates are below. Do not infer the right correction from this experiment’s residuals.</p><p>These checks have now been inspected. Any revised model needs newly reserved independent checks; the old four become diagnostic data. <a href="../apps/viewer/public/">Return to map</a>. <a href="reports/reference-research.md">Historical evidence and source links</a>.</p>'''+''.join(cards)+'<p>Scan: Library of Congress, Geography and Map Division. Modern: USGS The National Map (full attribution in source metadata). GNIS coordinates: NAD83, EPSG:4269. No modern coordinate supplied for unresolved candidates.</p></html>'
(R/'research/review.html').write_text(page)
print('Saved five static comparisons, 15 historical crops, 13 modern crops and one consolidated review page.')
