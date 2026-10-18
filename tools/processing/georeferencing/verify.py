"""Independent packaging checks; explicitly does NOT certify historical accuracy."""
import argparse
import json
import numpy as np
import rasterio
from rasterio.transform import from_bounds
from rasterio.warp import reproject, Resampling
from scipy.ndimage import binary_erosion
from common import ROOT, inspect_raster, sha256

p=argparse.ArgumentParser();p.add_argument('maps',nargs='*',default=['collet_1770','mouzon_1775','moseley_1733']);args=p.parse_args()
reports=[]
for map_id in args.maps:
    folder=ROOT/'data/historical_maps'/map_id
    m=json.loads((folder/'manifest.json').read_text())
    paths={k:ROOT/m[k]['path'] for k in ['master','web']}
    checks={k:inspect_raster(v) for k,v in paths.items()}
    assert checks['web']['crs']=='EPSG:3857'
    for k in paths:
        if 'sha256' in m[k]:
            assert sha256(paths[k])==m[k]['sha256'],f'{map_id} {k} changed after manifest'
    # Compare master and web derivative on the same modest projected sampling grid.
    # This tests conversion fidelity, not how well either agrees with the ground.
    with rasterio.open(paths['master']) as master, rasterio.open(paths['web']) as web:
        dst_crs='EPSG:5070'
        from rasterio.warp import transform_bounds
        bounds=transform_bounds(master.crs,dst_crs,*master.bounds,densify_pts=41)
        w=1000;h=round(w*(bounds[3]-bounds[1])/(bounds[2]-bounds[0]))
        aff=from_bounds(*bounds,w,h)
        arrays=[]
        for source in [master,web]:
            a=np.zeros((4,h,w),dtype='uint8')
            reproject(rasterio.band(source,[1,2,3,4]),a,dst_crs=dst_crs,dst_transform=aff,
                      src_alpha=4,dst_alpha=4,resampling=Resampling.bilinear,num_threads=2)
            arrays.append(a)
        a,b=arrays;valid=binary_erosion((a[3]>250)&(b[3]>250),iterations=2)
        assert valid.sum()>100
        delta=np.abs(a[:3].astype(float)-b[:3].astype(float))[:,valid]
        ma=(a[3]>127);mb=(b[3]>127)
        overlap=float((ma&mb).sum()/(ma|mb).sum())
        fidelity=dict(comparison_crs=dst_crs,grid=[w,h],valid_samples=int(valid.sum()),
                      mean_absolute_rgb_difference_0_255=float(delta.mean()),p95_absolute_rgb_difference=float(np.percentile(delta,95)),
                      alpha_mask_intersection_over_union=overlap,
                      meaning='Master-versus-web reprojection fidelity only, NOT modern positional validation')
        assert overlap>.98, f'{map_id}: unexpected master/web footprint change'
        assert delta.mean()<15, f'{map_id}: inspect unexpected derivative color difference'
    r=dict(id=map_id,technical_checks_passed=True,rasters=checks,reprojection_fidelity=fidelity,
           georeferencing_status=m['status'],geographic_accuracy_certified=False,
           caution='Passing COG, bounds, alpha and reprojection checks does not validate historical positions. See point evidence and independent checkpoint results in QA.')
    (folder/'verification.json').write_text(json.dumps(r,indent=2)+'\n')
    reports.append(r)
    print(map_id, 'technical checks PASS;',m['status'],json.dumps(fidelity))
if len(reports)==3:
    (ROOT/'data/historical_maps/verification.json').write_text(json.dumps(reports,indent=2)+'\n')
