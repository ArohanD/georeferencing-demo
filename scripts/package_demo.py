"""Build an explicitly allowlisted static GitHub Pages demo; never copy credentials."""
import hashlib, html, json, re, shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R/'publish'/'geoserver-demo';P.mkdir(parents=True,exist_ok=True)
files=set()
def add(pattern):files.update(p for p in R.glob(pattern) if p.is_file())
for pattern in ['preview/*.html','preview/*.js','preview/*.css','preview/data.json','preview/LEAFLET-LICENSE','outputs/*-overlay.png','outputs/*-comparison.png','outputs/review/*.jpg','data/reference/*-modern.jpg','data/points/*.csv','data/points/selection.json','data/points/mask.json','reports/*.md']:
 add(pattern)
for name in ['data/metadata/usgs-topo-service.json','data/metadata/source.json','outputs/errors.csv','outputs/cog-validation.json','outputs/transformation.json']:
 files.add(R/name)
for src in sorted(files):
 dst=P/src.relative_to(R);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
# Omit machine-specific metadata from public processing settings.
f=P/'outputs/transformation.json';j=json.loads(f.read_text());j.pop('runtime',None);f.write_text(json.dumps(j,indent=2)+'\n')
# Render read-only reports without adding a framework or a build dependency.
def inline(text):
 s=html.escape(text)
 s=re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',r'<a href="\2">\1</a>',s)
 s=re.sub(r'`([^`]+)`',r'<code>\1</code>',s)
 return re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',s)
def render(md):
 parts=[];paragraph=[];table=False;listing=False
 def flush():
  if paragraph:parts.append('<p>'+inline(' '.join(paragraph))+'</p>');paragraph.clear()
 for line in md.splitlines()+['']:
  if not line.startswith('|') and table:parts.append('</tbody></table></div>');table=False
  if not line.startswith('- ') and listing:parts.append('</ul>');listing=False
  if line.startswith('|'):
   flush()
   if re.match(r'^\|[\s:|\-]+$',line):continue
   if not table:parts.append('<div class="table"><table><tbody>');table=True
   parts.append('<tr>'+''.join('<td>'+inline(x.strip())+'</td>' for x in line.strip('|').split('|'))+'</tr>')
  elif line.startswith('#'):
   flush();n=min(len(line)-len(line.lstrip('#')),6);parts.append(f'<h{n}>'+inline(line[n:].strip())+f'</h{n}>')
  elif line.startswith('- '):
   flush()
   if not listing:parts.append('<ul>');listing=True
   parts.append('<li>'+inline(line[2:])+'</li>')
  elif line.strip():paragraph.append(line)
  else:flush()
 return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>The Listening Machine — report</title><style>body{font:17px/1.6 system-ui;max-width:960px;margin:30px auto;padding:0 20px;background:#f8f5ee;color:#242424}a{color:#14598a}code{overflow-wrap:anywhere}.table{overflow-x:auto}td{border-bottom:1px solid #ccc;padding:8px;vertical-align:top}h1{line-height:1.2}</style><a href="../preview/">Return to demo</a>'+''.join(parts)+'</html>'
for md in (P/'reports').glob('*.md'):md.with_suffix('.html').write_text(render(md.read_text()))
for name in ['index.html','review.html']:
 f=P/'preview'/name;s=f.read_text().replace('../reports/feasibility.md','../reports/feasibility.html').replace('../reports/reference-research.md','../reports/reference-research.html')
 f.write_text(s)
(P/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><meta http-equiv="refresh" content="0; url=preview/"><title>The Listening Machine</title><p><a href="preview/">Open the Collet 1770 demo</a></p></html>\n')
(P/'.nojekyll').touch()
(P/'.gitignore').write_text('.DS_Store\nThumbs.db\n')
(P/'README.md').write_text('''# The Listening Machine — historical-map demo

Public historical-map georeferencing proof of concept for an NC State MGIST capstone.

**Provisional regional overlay:** four held-out town proxies give an 8.02 km RMSE, with a maximum error of 13.08 km. This is not a source of precise historical settlement, road or parcel locations. Eight town proxies fit one affine model; four were reserved before fitting. The demo includes an opacity slider, modern reference maps, point discrepancies, static comparisons, a feasibility report and review materials.

For local use, run `python -m http.server 8000 --bind 127.0.0.1` from this folder and open http://localhost:8000/preview/ . Live Collet imagery streams from the NC State VCL GeoServer over HTTPS, above OpenStreetMap. Local Collet overlays, USGS reference images and Leaflet remain bundled for offline comparison. No API keys, database connections or analytics are used.

Approximate historical-map alignment. For visual comparison only; not suitable for locating routes or sites precisely. These uncertain historical correspondences are not survey-grade accuracy estimates.

Public endpoints, layer names, bounds and publication flags are centralized in `preview/map-config.js`; there are no environment variables. On 2026-10-12 Collet was verified; Moseley was absent from capabilities and is disabled. After publishing and verifying Moseley, set its `available` flag to true and update its label. It has approximately 20.5 km RMSE across two held-out coastal proxies.

This directory is a prepared static deployment artifact, not confirmation of deployment. Serve its contents at the hosting root (or a project subpath); relative links are preserved. Live services must remain reachable over trusted HTTPS. The ordinary image tile requests do not require a CORS-enabled fetch or browser credentials.

## Included material

- `preview/`: viewer and annotated point-review page.
- `outputs/`: display overlays, comparisons, crops and selected method/error records.
- `reports/`: feasibility and source research, with browser-readable HTML copies.
- `data/`: selected reference images, control-point tables and source credits.

This repository is a display package. It deliberately excludes the source scan, full COG, processing scratch files, Python environment and machine-specific metadata. It is not the complete reproducibility archive. Public corrections should not contain personal or confidential information; the current review CSV is a blank response template with baseline candidates.

## Attribution and reuse

Historical scan: Library of Congress, Geography and Map Division, [John Collet, A compleat map of North-Carolina from an actual survey, London: S. Hooper, 1770, Copy 1](https://www.loc.gov/resource/g3900.ar150000/). See `data/metadata/source.json` for provenance and stated reuse terms.

Modern maps: USGS The National Map and its credited contributors; full attribution is preserved in `data/metadata/usgs-topo-service.json`. Reference town coordinates: USGS GNIS, NAD83. Leaflet 1.9.4 is provided under its BSD license in `preview/LEAFLET-LICENSE`. The map’s historical content reflects its time; inclusion is not endorsement.

No additional blanket license is asserted over third-party material or the project’s original writing/code. Retain source credits and the provisional-accuracy notice when sharing the demo.
''')
# Audit the exact publication payload, including any unexpected preexisting files.
allowed={p.relative_to(R).as_posix() for p in files}|{'outputs/transformation.json','index.html','.nojekyll','.gitignore','README.md'}|{f'reports/{p.stem}.html' for p in (P/'reports').glob('*.md')}
secret=re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bgh[pousr]_[A-Za-z0-9]{20,}|\bgithub_pat_[A-Za-z0-9_]{20,}|\bAKIA[0-9A-Z]{16}\b')
manifest={}
for f in P.rglob('*'):
 if not f.is_file() or '.git' in f.relative_to(P).parts:continue
 rel=f.relative_to(P).as_posix()
 if rel=='PUBLICATION-MANIFEST.json':continue
 assert rel in allowed, f'Unexpected file in public payload: {rel}'
 if f.suffix in {'.md','.html','.js','.css','.json','.csv'}:
  s=f.read_text();assert not secret.search(s),f'Credential pattern: {rel}'
  assert '/home/arohan' not in s and '.local-auth' not in s and 'localhost:8000' not in s.replace('http://localhost:8000',''), f'Local metadata: {rel}'
 manifest[rel]={'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
(P/'PUBLICATION-MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(f'Allowlist passed: {len(manifest)} files; {sum(x["bytes"] for x in manifest.values())/1048576:.2f} MiB; largest {max(x["bytes"] for x in manifest.values())/1048576:.2f} MiB.')
