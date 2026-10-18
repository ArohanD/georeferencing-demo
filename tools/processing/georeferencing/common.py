"""Shared raster packaging and review helpers; no publication side effects."""
from pathlib import Path
import hashlib
import json
import numpy as np
import rasterio
from rasterio.enums import ColorInterp, Resampling
from rasterio.shutil import copy as rio_copy
from rasterio.warp import calculate_default_transform, reproject, transform_bounds
from rasterio.transform import from_bounds
from PIL import Image, ImageDraw
from rio_cogeo.cogeo import cog_validate

ROOT = Path(__file__).resolve().parents[3]

def fetch_reference(output_dir, name, bounds_3857, width=1400):
    """Cache one documented USGS export; requires network only when missing."""
    import requests
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    jpg=output_dir/(name+'-modern.jpg'); meta=output_dir/(name+'-modern.json')
    if jpg.exists() and meta.exists():
        return jpg, meta
    l,b,r,t=bounds_3857
    height=round(width*(t-b)/(r-l))
    params=dict(bbox=','.join(map(str,bounds_3857)),bboxSR=3857,imageSR=3857,
                size=f'{width},{height}',format='jpg',f='json')
    u='https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/export'
    response=requests.get(u,params=params,timeout=120); response.raise_for_status()
    data=response.json()
    if 'error' in data:
        raise RuntimeError(data['error'])
    img=requests.get(data['href'],timeout=120); img.raise_for_status()
    jpg.write_bytes(img.content)
    with Image.open(jpg) as im:
        assert im.size==(width,height)
    meta.write_text(json.dumps(dict(request_url=response.url,response=data,sha256=sha256(jpg),
                                   credit='USGS The National Map',access_date='2026-10-07'),indent=2)+'\n')
    return jpg,meta

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def inspect_raster(path):
    valid, errors, warnings = cog_validate(str(path), strict=True)
    with rasterio.open(path) as s:
        sample = s.read(out_shape=(s.count, 128, 128))
        result = dict(path=str(Path(path).relative_to(ROOT)), bytes=Path(path).stat().st_size,
                      sha256=sha256(path), crs=str(s.crs), dimensions=[s.width, s.height],
                      bounds=list(s.bounds), geographic_bounds=transform_bounds(s.crs, 'EPSG:4326', *s.bounds, densify_pts=41),
                      resolution=list(s.res), overviews=s.overviews(1), bands=s.count,
                      color_interpretation=[v.name for v in s.colorinterp],
                      compression=str(s.compression), cog_valid=valid, errors=errors, warnings=warnings,
                      sampled_rgb_range=[int(sample[:3].min()), int(sample[:3].max())])
        if s.count == 4:
            result['sampled_alpha_nonzero_fraction'] = float(np.mean(sample[3] > 0))
        assert valid and s.crs and s.overviews(1) and np.ptp(sample[:3]) > 0, result
    return result

def web_cog(master, output, resolution=125):
    output = Path(output)
    if output.exists():
        return inspect_raster(output)
    tmp = output.with_suffix('.working.tif')
    with rasterio.Env(GDAL_CACHEMAX=256), rasterio.open(master) as s:
        aff, w, h = calculate_default_transform(s.crs, 'EPSG:3857', s.width, s.height, *s.bounds, resolution=resolution)
        profile = s.profile.copy()
        profile.update(driver='GTiff', crs='EPSG:3857', transform=aff, width=w, height=h,
                       tiled=True, blockxsize=512, blockysize=512, compress='deflate', BIGTIFF='IF_SAFER')
        with rasterio.open(tmp, 'w', **profile) as d:
            reproject(source=rasterio.band(s, list(range(1, s.count+1))),
                      destination=rasterio.band(d, list(range(1, s.count+1))),
                      src_alpha=4 if s.count == 4 else 0, dst_alpha=4 if s.count == 4 else 0,
                      resampling=Resampling.bilinear, num_threads=2, warp_mem_limit=256)
            d.colorinterp = s.colorinterp
            d.update_tags(**s.tags(), derivative='Web Mercator serving grid; pixel size is not positional accuracy')
    rio_copy(tmp, output, driver='COG', compress='DEFLATE', blocksize=512, overview_resampling='AVERAGE')
    tmp.unlink()
    return inspect_raster(output)

def reference_preview(raster, reference_image, reference_json, output, title):
    """Use actual returned USGS export extent, never assumed request extent."""
    meta = json.loads(Path(reference_json).read_text())
    e = meta['response']['extent']
    base = Image.open(reference_image).convert('RGBA')
    w, h = base.size
    arr = np.zeros((4, h, w), dtype='uint8')
    with rasterio.open(raster) as s:
        reproject(rasterio.band(s, [1,2,3,4]), arr,
                  dst_transform=from_bounds(e['xmin'], e['ymin'], e['xmax'], e['ymax'], w, h),
                  dst_crs='EPSG:3857', src_alpha=4, dst_alpha=4, resampling=Resampling.bilinear)
    overlay = Image.fromarray(np.moveaxis(arr, 0, 2))
    overlay.save(Path(output).with_name(Path(output).stem + '-overlay.png'))
    arr[3] = (arr[3].astype(float) * .55).astype('uint8')
    blend = Image.alpha_composite(base, Image.fromarray(np.moveaxis(arr, 0, 2)))
    canvas = Image.new('RGB', (w * 2, h + 70), 'white')
    canvas.paste(base.convert('RGB'), (0, 70)); canvas.paste(blend.convert('RGB'), (w, 70))
    draw = ImageDraw.Draw(canvas)
    draw.text((15, 8), title, fill='black')
    draw.text((15, 28), 'USGS The National Map reference (left); historical overlay at 55% (right)', fill='black')
    draw.text((15, 48), 'PROVISIONAL INSPECTION ONLY. Rectification does not validate historical routes or locations.', fill='black')
    canvas.save(output)
    return dict(preview=str(Path(output).relative_to(ROOT)), reference_extent=e, opacity=.55)
