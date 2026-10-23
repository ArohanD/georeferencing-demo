"""Shared static package validation/writing; readers supply bytes, never execute assets."""
import hashlib
import json
import posixpath
import re
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


def validate_files(files):
    if not isinstance(files, list) or not files or len(files) > 256:
        raise ValueError('FILES must list 1–256 assets')
    for name in files:
        if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z0-9_./-]+', name):
            raise ValueError('Invalid asset path in FILES')
        parts = name.split('/')
        if (name != '.nojekyll' and any(part.startswith('.') or not part for part in parts)):
            raise ValueError(f'Unsafe asset path: {name}')
        if (parts[0] == 'branches' or name in ('PUBLICATION-MANIFEST.json', 'DEPLOYMENT-MANIFEST.json')):
            raise ValueError(f'Reserved asset path: {name}')
        if name != '.nojekyll' and Path(name).suffix.lower() not in (
                '.html', '.js', '.css', '.json', '.geojson', '.png', '.jpg', '.jpeg',
                '.svg', '.webp', '.ico', '.woff', '.woff2', '.txt') and name != 'preview/LEAFLET-LICENSE':
            raise ValueError(f'Unsupported app asset type: {name}')
    if len(set(files)) != len(files) or 'index.html' not in files:
        raise ValueError('FILES needs a unique index.html and no duplicates')
    return files


class AssetReferences(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ('script', 'img', 'source', 'audio', 'video') and attrs.get('src'):
            self.urls.append(attrs['src'])
        if tag == 'link' and set(attrs.get('rel', '').split()) & {'stylesheet', 'icon', 'preload', 'modulepreload'}:
            if attrs.get('href'):
                self.urls.append(attrs['href'])


def validate_html_assets(assets):
    for name, content in assets.items():
        if not name.endswith('.html'):
            continue
        parser = AssetReferences()
        parser.feed(content.decode('utf-8'))
        for url in parser.urls:
            parsed = urlsplit(url)
            if parsed.scheme or parsed.netloc:
                continue
            path = posixpath.normpath(posixpath.join(posixpath.dirname(name), unquote(parsed.path)))
            if path not in assets:
                raise ValueError(f'HTML asset not packaged: {name} -> {url}')



def assemble(files, read_asset, dest):
    files = validate_files(files)
    assets = {}
    total_size = 0
    for name in files:
        content = read_asset(name, 5 * 1024 * 1024)
        if len(content) > 5 * 1024 * 1024:
            raise ValueError(f'Asset exceeds 5 MiB: {name}')
        total_size += len(content)
        if total_size > 50 * 1024 * 1024:
            raise ValueError('App package exceeds 50 MiB')
        if name.endswith('.js'):
            checked = subprocess.run(['node', '--check', '-'], input=content,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            if checked.returncode:
                raise ValueError(f'JavaScript syntax check failed: {name}')
        assets[name] = content
    validate_html_assets(assets)
    if dest.is_symlink():
        raise ValueError('Package directory must not be a symlink')
    # Refuse stale or symlinked output rather than deleting local work or writing
    # through links. All inputs are validated before touching the output.
    output_files = set(files) | {'PUBLICATION-MANIFEST.json'}
    for path in dest.rglob('*'):
        name = path.relative_to(dest).as_posix()
        if (path.is_symlink() or
                (name in output_files and not path.is_file()) or
                (name not in output_files and not path.is_dir())):
            raise ValueError(f'Unexpected file in app package: {path.relative_to(dest)}')
    dest.mkdir(parents=True, exist_ok=True)
    for name, content in assets.items():
        target = dest / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    manifest = {name: {'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest()}
                for name, content in assets.items()}
    (dest / 'PUBLICATION-MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest
