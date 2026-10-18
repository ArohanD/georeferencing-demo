#!/usr/bin/env python3
"""Publish only the two prepared historical maps; dry-run unless --publish.

Credentials are prompted, never persisted. HTTPS verification is mandatory.
"""
import argparse
import getpass
import hashlib
import io
import json
import os
from pathlib import Path, PureWindowsPath
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET
import requests
from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parents[2]
IDS = ('wimble_1738', 'bowen_1747')
BASE = 'https://vclvm176-164.vclgis.cnr.ncsu.edu/geoserver'


def checksum(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8*1024*1024), b''): h.update(chunk)
    return h.hexdigest()


def request(session, method, url, expected=(200,), **kwargs):
    r = session.request(method, url, timeout=(20, 600), allow_redirects=False, **kwargs)
    if r.status_code not in expected:
        hints = {401: 'Authentication required or credentials rejected.', 403: 'Account lacks publishing access.', 413: 'Upload exceeds IIS request size; use documented server-local file registration.', 404: 'Resource not found; check endpoint/workspace.'}
        hint = hints.get(r.status_code, 'Check the GeoServer/IIS logs. Redirects are not followed.')
        # Do not echo arbitrary responses, which might contain sensitive server details.
        raise RuntimeError(f'{method} {urlsplit(url).path}: HTTP {r.status_code}. {hint}')
    return r


def coverage_xml(m):
    c = ET.Element('coverage')
    for key, value in {'name': m['id'], 'title': m['title'], 'srs': 'EPSG:3857', 'enabled': 'true'}.items():
        ET.SubElement(c, key).text = value
    s, check = m['source'], m['diagnostic']['check']
    abstract = (f"{s['title']} ({m['date']}). {s['publication']}. "
                f"{m['accuracy_notice']} Held-out cape-proxy RMSE: {check['rmse_m']/1000:.2f} km across {check['n']} checks; uncertain correspondences, not survey-grade accuracy. "
                f"{s['institution']}. Source: {s['item_url']}. Method: {s['method']} "
                f"Rights: {s['rights']} Full provenance, points and transformation are in historicalMapMetadata and embedded GeoTIFF tags.")
    ET.SubElement(c, 'abstract').text = abstract
    keywords = ET.SubElement(c, 'keywords')
    for word in ('North Carolina', 'historical map', str(m['date']), 'approximate alignment', 'visual comparison', *s['creators']):
        ET.SubElement(keywords, 'string').text = word
    links = ET.SubElement(c, 'metadataLinks')
    for url in (s['item_url'], s['resource_url'], s['rights_url']):
        link = ET.SubElement(links, 'metadataLink')
        for k, v in {'type': 'text/html', 'metadataType': 'other', 'content': url}.items(): ET.SubElement(link, k).text = v
    metadata = ET.SubElement(c, 'metadata')
    # This is intentionally a string, allowing complete provenance to survive REST round trips.
    published = dict(m, publication_status='Raster and metadata submitted; consult local publication receipt for WMS verification')
    ET.SubElement(metadata, 'entry', key='historicalMapMetadata').text = json.dumps(published, ensure_ascii=False)
    ET.SubElement(metadata, 'entry', key='historicalMapSHA256').text = m['web']['sha256']
    return ET.tostring(c, encoding='utf-8', xml_declaration=True)


def layer_xml(m):
    layer = ET.Element('layer')
    ET.SubElement(layer, 'enabled').text = 'true'
    style = ET.SubElement(layer, 'defaultStyle'); ET.SubElement(style, 'name').text = 'raster'
    att = ET.SubElement(layer, 'attribution')
    ET.SubElement(att, 'title').text = m['source']['institution']
    ET.SubElement(att, 'href').text = m['source']['item_url']
    return ET.tostring(layer, encoding='utf-8', xml_declaration=True)


def load(ident):
    m = json.loads((ROOT/'data/historical_maps'/ident/'manifest.json').read_text())
    p = (ROOT/m['web']['path']).resolve()
    if not p.is_relative_to(ROOT/'deliverables') or m['id'] != ident:
        raise RuntimeError('Unexpected raster path or ID')
    if checksum(p) != m['web']['sha256'] or not m['web']['cog_valid']:
        raise RuntimeError(f'{ident}: raster checksum/validation mismatch; rebuild before publishing')
    return m, p


def save_receipt(path, receipt):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(receipt, indent=2)+'\n')
    temp.replace(path)


def verify_wms(base, m, out):
    # Deliberately anonymous: the public app must work without publishing credentials.
    session = requests.Session()
    session.trust_env = False  # Prevent implicit .netrc credentials.
    caps = request(session, 'GET', base+'/history/wms', params=dict(service='WMS', version='1.1.1', request='GetCapabilities'))
    root = ET.fromstring(caps.content)
    names = {e.text for e in root.findall('.//Layer/Name')}
    if m['id'] not in names and m['layer_name'] not in names:
        raise RuntimeError('Published layer missing from anonymous WMS capabilities')
    bounds = m['web']['bounds']
    results = []
    for name, box in [('overview', bounds), ('center-detail', [(bounds[0]+bounds[2])/2-45000, (bounds[1]+bounds[3])/2-30000, (bounds[0]+bounds[2])/2+45000, (bounds[1]+bounds[3])/2+30000])]:
        h = max(100, round(1200*(box[3]-box[1])/(box[2]-box[0])))
        r = request(session, 'GET', base+'/history/wms', params=dict(service='WMS', version='1.1.1', request='GetMap', layers=m['layer_name'], styles='', srs='EPSG:3857', bbox=','.join(map(str, box)), width=1200, height=h, format='image/png', transparent='true'))
        if not r.headers.get('Content-Type', '').lower().startswith('image/png'):
            raise RuntimeError('WMS did not return PNG imagery')
        im = Image.open(io.BytesIO(r.content)).convert('RGBA'); im.load()
        if im.size != (1200, h) or im.getchannel('A').getextrema()[1] == 0 or max(ImageStat.Stat(im.convert('RGB')).stddev) < 2:
            raise RuntimeError('WMS returned blank or unexpected imagery')
        path = out/f'published-{name}.png'; path.write_bytes(r.content)
        results.append(dict(image=str(path.relative_to(ROOT)), bbox=box, dimensions=list(im.size)))
    return results


def publish(session, base, m, raster, resume=False, server_dir=None):
    ident = m['id']; out = ROOT/'deliverables'/ident
    receipt_path = out/'publication-receipt.json'
    key = dict(base=base, layer=m['layer_name'], sha256=m['web']['sha256'])
    store = base+'/rest/workspaces/history/coveragestores/'+ident
    exists = request(session, 'GET', store+'.json', expected=(200, 404)).status_code == 200
    receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else {}
    if exists:
        if not resume or any(receipt.get(k) != v for k, v in key.items()) or not receipt.get('raster_uploaded'):
            raise RuntimeError(f'{ident}: store exists. Refusing overwrite; --resume requires this uploader’s matching local receipt.')
    else:
        # Also protect a same-named layer originating in another store.
        layer = request(session, 'GET', base+'/rest/layers/history:'+ident+'.json', expected=(200, 404))
        if layer.status_code == 200: raise RuntimeError(f'{ident}: layer already exists; refusing collision')
        params = dict(configure='first', coverageName=ident)
        if server_dir:
            uri = (PureWindowsPath(server_dir)/raster.name).as_uri()
            request(session, 'PUT', store+'/external.geotiff', expected=(200, 201, 202), params=params, data=uri, headers={'Content-Type': 'text/plain'})
        else:
            with raster.open('rb') as f:
                request(session, 'PUT', store+'/file.geotiff', expected=(200, 201, 202), params=params, data=f, headers={'Content-Type': 'image/tiff'})
        receipt = dict(key, raster_uploaded=True, metadata_uploaded=False, wms_verified=False)
        save_receipt(receipt_path, receipt)
    request(session, 'PUT', store+'/coverages/'+ident+'.xml', data=coverage_xml(m), headers={'Content-Type': 'application/xml'})
    request(session, 'PUT', base+'/rest/layers/history:'+ident+'.xml', data=layer_xml(m), headers={'Content-Type': 'application/xml'})
    # Check that complete metadata survived serialization, not only HTTP 200.
    xml = request(session, 'GET', store+'/coverages/'+ident+'.xml')
    cov = ET.fromstring(xml.content)
    stored = cov.find("./metadata/entry[@key='historicalMapMetadata']")
    if stored is None or not stored.text or json.loads(stored.text)['web']['sha256'] != key['sha256']:
        raise RuntimeError('Full provenance did not round-trip; inspect coverage metadata before proceeding')
    receipt['metadata_uploaded'] = True; save_receipt(receipt_path, receipt)
    receipt['wms_images'] = verify_wms(base, m, out)
    receipt['wms_verified'] = True; save_receipt(receipt_path, receipt)
    print(f"Verified {m['layer_name']}: metadata plus two anonymous WMS images", flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--publish', action='store_true', help='Perform authenticated GeoServer writes')
    p.add_argument('--verify-only', action='store_true', help='Check anonymous published WMS without credentials')
    p.add_argument('--resume', action='store_true', help='Finish only uploads owned by matching local receipts')
    p.add_argument('--layer', choices=IDS, action='append', help='Default: both prepared maps')
    p.add_argument('--base-url', default=BASE)
    p.add_argument('--server-dir', help='Windows directory already containing identical TIFFs; register via external.geotiff')
    a = p.parse_args(); base = a.base_url.rstrip('/')
    parsed = urlsplit(base)
    if parsed.scheme != 'https' or not parsed.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment:
        p.error('Use an HTTPS GeoServer base URL without credentials, query or fragment')
    if a.publish and a.verify_only: p.error('Choose --publish or --verify-only')
    maps = [load(i) for i in (a.layer or IDS)]
    for m, raster in maps:
        print(f"{m['layer_name']}: {raster.name} ({raster.stat().st_size/1e6:.1f} MB), SHA256 {m['web']['sha256']}")
        (ROOT/'deliverables'/m['id']/'coverage.xml').write_bytes(coverage_xml(m))
        (ROOT/'deliverables'/m['id']/'layer.xml').write_bytes(layer_xml(m))
    if a.verify_only:
        for m, _ in maps: print(json.dumps(verify_wms(base, m, ROOT/'deliverables'/m['id']), indent=2))
        return
    if not a.publish:
        print('Dry-run: prepared metadata payloads; no network requests or server changes. Add --publish to upload.')
        return
    session = requests.Session(); session.trust_env = False
    username = os.environ.get('GEOSERVER_USERNAME') or input('GeoServer username: ')
    password = getpass.getpass('GeoServer password (not stored): ')
    session.auth = (username, password)
    request(session, 'GET', base+'/rest/workspaces/history.json')
    for m, raster in maps: publish(session, base, m, raster, a.resume, a.server_dir)


if __name__ == '__main__':
    try: main()
    except (RuntimeError, requests.RequestException, ValueError, OSError, ET.ParseError) as e:
        raise SystemExit(str(e))
