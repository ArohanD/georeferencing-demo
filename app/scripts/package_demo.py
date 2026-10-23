"""Build the minimal static application using the same rules as branch previews."""
import json
from pathlib import Path
from static_package import assemble

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'app/public'
DEST = ROOT / 'app/dist'

# Transitional declaration for the pre-JSON builder on main. Not read by this
# packager; the parity test prevents drift. Remove after the new builder ships.
FILES = ['index.html', '.nojekyll', 'preview/index.html', 'preview/app.js', 'preview/map-config.js', 'preview/terrain-layer.js', 'preview/leaflet.js', 'preview/leaflet.css', 'preview/LEAFLET-LICENSE', 'preview/plant-layer.js', 'preview/plant-layer.css', 'preview/plants/observations.geojson', 'preview/plants/manifest.json', 'preview/view-state.js']


def package(source=SOURCE, dest=DEST, manifest_path=ROOT / 'app/assets.json'):
    def read_asset(name, limit):
        path = source / name
        # Check every path component before following it.
        current = source
        if current.is_symlink():
            raise ValueError('App source directory must not be a symlink')
        for part in Path(name).parts:
            current = current / part
            if current.is_symlink():
                raise ValueError(f'Non-regular asset: {name}')
        if not path.is_file():
            raise ValueError(f'Missing asset: {name}')
        if path.stat().st_size > limit:
            raise ValueError(f'Asset exceeds 5 MiB: {name}')
        return path.read_bytes()
    return assemble(json.loads(manifest_path.read_text()), read_asset, dest)


def main():
    manifest = package()
    print(f'App package: {len(manifest)} files, {sum(item["bytes"] for item in manifest.values()) / 1024:.1f} KiB at {DEST}')


if __name__ == '__main__':
    main()
