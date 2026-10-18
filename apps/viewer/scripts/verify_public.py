"""Verify the public GitHub Pages payload against the local publication manifest."""
import concurrent.futures, hashlib, json
from pathlib import Path
import requests
R=Path(__file__).resolve().parents[3]
base='https://arohand.github.io/georeferencing-demo/'
local=json.loads((R/'apps/viewer/dist/PUBLICATION-MANIFEST.json').read_text())
response=requests.get(base+'PUBLICATION-MANIFEST.json',timeout=45);response.raise_for_status()
assert response.json()==local,'Published manifest differs from audited package'
def check(item):
 path,info=item
 if path.startswith('.'):return path+' omitted by Pages (repository control file)'
 r=requests.get(base+path,timeout=45);r.raise_for_status()
 assert hashlib.sha256(r.content).hexdigest()==info['sha256'],path
 return path
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 verified=list(pool.map(check,local.items()))
result={'url':base,'repository':'https://github.com/ArohanD/georeferencing-demo','manifest_matches':True,'public_files_hash_verified':sum(not p.startswith('.') for p in local),'note':'HTTP content verification; not interactive browser automation','excluded_from_publication':['credentials','Python environments','source scan','COG and scratch TIFFs','local machine metadata'],'package_bytes':sum(x['bytes'] for x in local.values())}
out = R/'apps/viewer/artifacts'
out.mkdir(exist_ok=True)
(out/'publication-verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
