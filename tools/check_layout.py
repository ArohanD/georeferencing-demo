"""Check monorepo links, Python entry-point roots, and the built viewer without network."""
import ast
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'apps/viewer/public'
PACKAGE = ROOT / 'publish/app-lidar'


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        self.links.extend(value for key, value in attrs if key in ('src', 'href') and value)


def check_link(page, link):
    url = urlsplit(link)
    if url.scheme or url.netloc or not url.path:
        return
    target = (page.parent / unquote(url.path)).resolve()
    assert target.is_relative_to(ROOT), f'Link escapes repository: {page}: {link}'
    assert target.exists(), f'Broken local link: {page.relative_to(ROOT)}: {link}'


def main():
    pages = [*PUBLIC.rglob('*.html'), ROOT / 'research/review.html', *PACKAGE.rglob('*.html')]
    for page in pages:
        parser = Links()
        parser.feed(page.read_text())
        for link in parser.links:
            check_link(page, link)
    markdown = [ROOT/'README.md', *ROOT.joinpath('apps').rglob('*.md'),
                *ROOT.joinpath('tools').rglob('*.md'), *ROOT.joinpath('research').rglob('*.md'),
                *ROOT.joinpath('docs').rglob('*.md'), *ROOT.joinpath('data').rglob('*.md')]
    for page in markdown:
        for link in re.findall(r'\]\(([^\s)]+)\)', page.read_text()):
            check_link(page, link)
    # Check static root assignments without importing scripts that process or publish data.
    roots = 0
    for parent in (ROOT/'apps', ROOT/'tools'):
        for script in parent.rglob('*.py'):
            tree = ast.parse(script.read_text(), filename=str(script))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Assign):
                    continue
                if not any(isinstance(t, ast.Name) and t.id in ('ROOT', 'R', 'root') for t in node.targets):
                    continue
                source = ast.get_source_segment(script.read_text(), node.value)
                if re.fullmatch(r'Path\(__file__\)\.resolve\(\)\.parents\[\d+\]', source or ''):
                    resolved = script.resolve().parents[node.value.slice.value]
                    assert resolved == ROOT, f'Wrong repository root: {script}'
                    roots += 1
    expected = {p.relative_to(PUBLIC).as_posix() for p in PUBLIC.rglob('*') if p.is_file()}
    manifest = json.loads((PACKAGE/'PUBLICATION-MANIFEST.json').read_text())
    assert set(manifest) == expected, 'Package must contain exactly the public app assets'
    actual = {p.relative_to(PACKAGE).as_posix() for p in PACKAGE.rglob('*') if p.is_file()}
    assert actual == expected | {'PUBLICATION-MANIFEST.json'}, 'Unexpected package content'
    for name, info in manifest.items():
        content = (PACKAGE/name).read_bytes()
        assert content == (PUBLIC/name).read_bytes(), f'Stale packaged asset: {name}'
        assert len(content) == info['bytes']
        assert hashlib.sha256(content).hexdigest() == info['sha256']
    print(f'Passed: {len(pages)} HTML pages, {len(markdown)} Markdown files, '
          f'{roots} script roots, and {len(manifest)} packaged assets.')


if __name__ == '__main__':
    main()
