"""Reproduce two approximate colonial map derivatives from frozen town proxies.

Run .venv313/bin/python tools/processing/georeferencing/colonial_maps.py.
Downloads must already exist at source.json paths; no publishing side effects.
"""
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
from common import ROOT, sha256, inspect_raster, web_cog

IDS = ('wimble_1738', 'bowen_1747')
NOTICE = 'Approximate historical-map alignment. For visual comparison only; not suitable for locating routes or sites precisely.'


def build(ident):
    d = ROOT/'data/historical_maps'/ident
    o = ROOT/'deliverables'/ident
    meta = json.loads((d/'source.json').read_text())
    source = ROOT/meta['source_path']
    assert sha256(source) == meta['source_sha256'], 'Source checksum changed'
    assert sha256(d/'points.json') == meta['points_sha256'], 'Frozen points changed'
    points = json.loads((d/'points.json').read_text())
    t = Transformer.from_crs(4269, 32119, always_xy=True)
    fit = [p for p in points if p['role'] == 'fit']
    a = np.array([[p['pixel_x'], p['pixel_y'], 1] for p in fit])
    b = np.array([t.transform(p['longitude'], p['latitude']) for p in fit])
    center, scale = a[:, :2].mean(0), a[:, :2].std(0)
    c = np.linalg.lstsq(np.column_stack(((a[:, :2]-center)/scale, np.ones(len(a)))), b, rcond=None)[0]
    m = np.vstack((c[:2]/scale[:, None], c[2]-(center/scale)@c[:2]))
    aff = Affine(m[0, 0], m[1, 0], m[2, 0], m[0, 1], m[1, 1], m[2, 1])
    errors = []
    for p in points:
        pred = np.array([p['pixel_x'], p['pixel_y'], 1])@m
        target = np.array(t.transform(p['longitude'], p['latitude']))
        errors.append(dict(id=p['id'], name=p['name'], role=p['role'], dx_m=float(pred[0]-target[0]), dy_m=float(pred[1]-target[1]), error_m=float(np.linalg.norm(pred-target))))
    stats = {}
    for role in ('fit', 'check'):
        e = np.array([v['error_m'] for v in errors if v['role'] == role])
        stats[role] = dict(n=len(e), rmse_m=float(np.sqrt(np.mean(e**2))), max_m=float(e.max()))
    transform = dict(method=meta['method'], coefficients_to_EPSG32119=m.tolist(), statistics=stats, residuals=errors, master_pixel_size_m=meta['resolution'], web_pixel_size_map_units=meta['resolution'], pixel_size_is_not_accuracy=True, point_selection_uncertainty_pixels=[p['selection_uncertainty_pixels'] for p in points])
    (d/'transformation.json').write_text(json.dumps(transform, indent=2)+'\n')
    # Rebuild deterministically; never silently reuse derivatives of different points.
    master = o/f'{ident}_approximate_master_32119.tif'
    web = o/f'{ident}_approximate_web_3857.tif'
    im = Image.open(source).convert('RGB')
    poly = meta['mask_polygon']
    x0, y0 = min(p[0] for p in poly), min(p[1] for p in poly)
    x1, y1 = max(p[0] for p in poly), max(p[1] for p in poly)
    im = im.crop((x0, y0, x1, y1)); w, h = im.size
    cropped_aff = aff * Affine.translation(x0, y0)
    rgba = np.zeros((4, h, w), dtype='uint8')
    rgba[:3] = np.moveaxis(np.asarray(im), 2, 0)
    mask = Image.new('L', (w, h))
    ImageDraw.Draw(mask).polygon([(x-x0, y-y0) for x, y in poly], fill=255)
    rgba[3] = np.asarray(mask)
    corners = np.array([[x0, y0, 1], [x1, y0, 1], [x1, y1, 1], [x0, y1, 1]])@m
    res = meta['resolution']
    left = math.floor(corners[:, 0].min()/res)*res
    top = math.ceil(corners[:, 1].max()/res)*res
    width = math.ceil((corners[:, 0].max()-left)/res)
    height = math.ceil((top-corners[:, 1].min())/res)
    da = from_origin(left, top, res, res)
    arr = np.zeros((4, height, width), dtype='uint8')
    reproject(rgba, arr, src_transform=cropped_aff, src_crs='EPSG:32119', dst_transform=da, dst_crs='EPSG:32119', src_alpha=4, dst_alpha=4, resampling=Resampling.bilinear, num_threads=2, warp_mem_limit=256)
    tmp = o/'master.working.tif'
    with rasterio.open(tmp, 'w', driver='GTiff', width=width, height=height, count=4, dtype='uint8', crs='EPSG:32119', transform=da, tiled=True, compress='deflate', blockxsize=512, blockysize=512) as ds:
        ds.write(arr)
        ds.colorinterp = (ColorInterp.red, ColorInterp.green, ColorInterp.blue, ColorInterp.alpha)
        ds.update_tags(TITLE=meta['title'], COPYRIGHT=meta['institution'], SOURCE=meta['item_url'], YEAR=str(meta['year']), WARNING=NOTICE, PROVENANCE_JSON=json.dumps(meta), TRANSFORMATION_JSON=json.dumps(transform), CONTROL_POINTS_JSON=json.dumps(points))
    rio_copy(tmp, master, driver='COG', compress='DEFLATE', blocksize=512, overview_resampling='AVERAGE')
    tmp.unlink()
    if web.exists(): web.unlink()
    master_info = inspect_raster(master)
    web_info = web_cog(master, web, meta['resolution'])
    manifest = dict(id=ident, title=meta['short_title']+' — approximate preview', date=meta['year'], source=meta, status='approximate preview', accuracy_notice=NOTICE, diagnostic=stats, independent_geographic_validation=None, points=points, transformation=transform, master=master_info, web=web_info, workspace='history', layer_name='history:'+ident, publication_status='not uploaded; authenticated REST access required')
    (d/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    for name in ('source.json', 'points.json', 'transformation.json', 'manifest.json', 'iiif-manifest.json'):
        shutil.copyfile(d/name, o/name)
    with rasterio.open(web) as ds:
        a = ds.read(out_shape=(4, round(ds.height*1800/ds.width), 1800))
        Image.fromarray(np.moveaxis(a, 0, 2)).save(o/'rectified-overview.png')
    print(json.dumps(dict(id=ident, stats=stats, web_bytes=web_info['bytes'], cog_valid=web_info['cog_valid']), indent=2), flush=True)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--download', action='store_true', help='Download missing public source JPEGs; frozen checksums must match')
    args = parser.parse_args()
    for ident in IDS:
        if args.download:
            import requests
            meta = json.loads((ROOT/'data/historical_maps'/ident/'source.json').read_text())
            path = ROOT/meta['source_path']
            if not path.exists():
                response = requests.get(meta['download_url'], timeout=180)
                response.raise_for_status()
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(response.content)
        build(ident)
