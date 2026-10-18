"""Build the app branch's minimal static site; no processing/research assets."""
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'apps/viewer/public'
DEST = ROOT / 'publish' / 'app-lidar'
FILES = ['index.html', '.nojekyll', 'preview/index.html', 'preview/app.js',
         'preview/map-config.js', 'preview/terrain-layer.js', 'preview/leaflet.js', 'preview/leaflet.css',
         'preview/LEAFLET-LICENSE']
DEST.mkdir(parents=True, exist_ok=True)
# Refuse unexpected old payloads instead of including or deleting them.
for path in DEST.rglob('*'):
    if path.is_file() and path.relative_to(DEST).as_posix() not in FILES + ['PUBLICATION-MANIFEST.json']:
        raise RuntimeError(f'Unexpected file in app package: {path.relative_to(DEST)}')
manifest = {}
for name in FILES:
    src, dst = SOURCE / name, DEST / name
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    content = dst.read_bytes()
    manifest[name] = {'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest()}
(DEST / 'PUBLICATION-MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(f'App package: {len(manifest)} files, {sum(item["bytes"] for item in manifest.values()) / 1024:.1f} KiB at {DEST}')
