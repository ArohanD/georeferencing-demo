"""Build the integration manifest and a local static review index, no app edits."""
import html
import json
import shutil
from common import ROOT

ids=['collet_1770','mouzon_1775','moseley_1733']
maps=[]; sections=[]
for map_id in ids:
    path=ROOT/'data/historical_maps'/map_id/'manifest.json'
    m=json.loads(path.read_text())
    m['status']=m.get('status',m.get('georeferencing_status'))
    assert m['status'] in ['provisional usable','approximate only','blocked']
    m['workspace']='pending';m['publication_status']='pending';m['service_url']=None
    m.setdefault('output_raster_path',m['web']['path'])
    m.setdefault('bounds',m['web']['geographic_bounds']);m.setdefault('bounds_crs','EPSG:4326')
    m['bounds_meaning']='Actual raster envelope, including transparent edges; not surveyed historical extent'
    m['qa_path']=f'data/historical_maps/{map_id}/QA.md'
    maps.append(m)
    folder=ROOT/'deliverables'/map_id
    # Preserve small reference provenance in versionable storage; images stay ignored.
    refdir=ROOT/'data/historical_maps'/map_id/'reference_exports'
    refdir.mkdir(exist_ok=True)
    for pattern in ['*modern.json','reference-*.json']:
        for p in folder.glob(pattern):
            shutil.copyfile(p,refdir/p.name)
    previews=sorted(set(folder.glob('*comparison*'))|set(folder.glob('preview-*.jpg')))
    rows=[]
    for p in previews:
        rel=p.relative_to(ROOT/'deliverables').as_posix()
        rows.append(f'<details><summary>{html.escape(p.stem)}</summary><a href="{rel}"><img loading="lazy" src="{rel}" alt="{html.escape(p.stem)} modern versus historical comparison"></a></details>')
    links=[]
    for p in sorted(folder.rglob('*review*.html')):
        rel=p.relative_to(ROOT/'deliverables').as_posix()
        links.append(f'<li><a href="{rel}">Annotated evidence: {html.escape(p.name)}</a></li>')
    evidence=sorted(set(folder.glob('*annotated.png'))|set(folder.glob('M??-historical.jpg'))|set(folder.glob('M??-modern.jpg'))|set(folder.glob('graticule-review.png')))
    if evidence:
        figures=[]
        for p in evidence:
            rel=p.relative_to(ROOT/'deliverables').as_posix()
            figures.append(f'<figure><figcaption>{html.escape(p.name)}</figcaption><a href="{rel}"><img loading="lazy" src="{rel}" alt="{html.escape(p.stem)}"></a></figure>')
        rows.append('<details><summary>Annotated control and candidate evidence — read QA for ambiguities</summary>'+''.join(figures)+'</details>')
    for key in ['master','web']:
        rel=(ROOT/m[key]['path']).relative_to(ROOT/'deliverables').as_posix()
        links.append(f'<li><a href="{rel}">{key} raster ({m[key]["crs"]})</a></li>')
    sections.append(f'<section><h2>{html.escape(m["title"])} ({m["date"]})</h2><p><strong>{m["status"].upper()}</strong> — {html.escape(m["accuracy_disclaimer"])}</p><p><a href="../data/historical_maps/{map_id}/QA.md">QA and interpretation limits</a> · <a href="../data/historical_maps/{map_id}/manifest.json">Manifest</a></p><ul>{"".join(links)}</ul>{"".join(rows)}</section>')
manifest=dict(schema_version=1,project='NC State MGIST Listening Machine',
              geoserver_base_url='https://vclvm176-164.vclgis.cnr.ncsu.edu/geoserver',
              workspace='pending',publication_status='pending',service_url=None,
              application=dict(library='Leaflet 1.9.4',framework='plain HTML/JavaScript',current_config='data/points/preview.json',current_layer_code='apps/viewer/public/preview/app.js',changed=False),
              accuracy_disclaimer='Rectification does not establish accuracy of historical routes or locations. Read individual status and checkpoint evidence.',maps=maps)
(ROOT/'data/historical_maps/integration-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Listening Machine — georeferencing review</title><style>body{max-width:1250px;margin:2rem auto;padding:0 1rem;font:17px/1.5 system-ui;color:#172a36;background:#f4f3ed}section{padding:1rem;background:white;border:1px solid #bbc5c9;margin:2rem 0}img{max-width:100%;height:auto}summary{cursor:pointer;padding:.6rem;background:#edf1f2;margin:.3rem 0}a{color:#064d7c}strong{color:#9a3316}</style><h1>Listening Machine: historical-map review</h1><p>Three actual raster datasets for review. Publication and workspace remain pending. No GeoServer or application configuration has been changed.</p><p><strong>All current results are approximate only.</strong> Technical verification checks the files and reprojection. Geographic evidence remains insufficient for validated historical registration. The Eno–Haw area is a provisional inspection area, not a selected research corridor.</p><p><a href="../data/historical_maps/README.md">Reproduction and integration notes</a> · <a href="../data/historical_maps/integration-manifest.json">Integration manifest</a></p>'''+''.join(sections)+'</html>'
(ROOT/'deliverables/index.html').write_text(page)
print('Wrote data/historical_maps/integration-manifest.json and deliverables/index.html')
