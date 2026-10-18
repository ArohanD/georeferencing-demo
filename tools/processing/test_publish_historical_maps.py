"""Safety/metadata tests for the scoped publisher; no network or credentials."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

spec = importlib.util.spec_from_file_location('publisher', Path(__file__).with_name('publish_historical_maps.py'))
pub = importlib.util.module_from_spec(spec); spec.loader.exec_module(pub)


class Response:
    def __init__(self, code, content=b''):
        self.status_code, self.content = code, content


class Session:
    def __init__(self, responses): self.responses, self.calls = list(responses), []
    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        return self.responses.pop(0)


class PublisherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = json.loads((pub.ROOT/'data/historical_maps/bowen_1747/manifest.json').read_text())

    def test_metadata_preserves_full_provenance_and_warning(self):
        xml = ET.fromstring(pub.coverage_xml(self.m))
        stored = json.loads(xml.find("./metadata/entry[@key='historicalMapMetadata']").text)
        self.assertEqual(stored['points'], self.m['points'])
        self.assertEqual(stored['transformation'], self.m['transformation'])
        self.assertIn(self.m['accuracy_notice'], xml.find('abstract').text)
        self.assertIn('cape-proxy', xml.find('abstract').text)
        self.assertEqual(len(xml.findall('./metadataLinks/metadataLink')), 3)

    def test_authentication_error_stops(self):
        s = Session([Response(401)])
        with self.assertRaisesRegex(RuntimeError, 'Authentication'): pub.request(s, 'GET', pub.BASE+'/rest/workspaces/history.json')
        self.assertEqual(len(s.calls), 1)

    def test_redirect_is_not_followed(self):
        s = Session([Response(302)])
        with self.assertRaisesRegex(RuntimeError, 'Redirects'): pub.request(s, 'PUT', pub.BASE+'/rest/x')
        self.assertFalse(s.calls[0][2]['allow_redirects'])
        self.assertNotIn('verify', s.calls[0][2])  # Never disables requests' TLS verification.

    def test_existing_store_never_overwritten_without_receipt(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(pub, 'ROOT', Path(tmp)):
            s = Session([Response(200)])
            with self.assertRaisesRegex(RuntimeError, 'Refusing overwrite'): pub.publish(s, pub.BASE, self.m, Path(tmp)/'raster.tif', resume=True)
            self.assertTrue(all(c[0] == 'GET' for c in s.calls))

    def test_existing_layer_in_other_store_refused(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(pub, 'ROOT', Path(tmp)):
            s = Session([Response(404), Response(200)])
            with self.assertRaisesRegex(RuntimeError, 'collision'): pub.publish(s, pub.BASE, self.m, Path(tmp)/'raster.tif')
            self.assertTrue(all(c[0] == 'GET' for c in s.calls))

    def test_upload_metadata_and_receipt(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(pub, 'ROOT', Path(tmp)), patch.object(pub, 'verify_wms', return_value=[{'test': True}]):
            raster = Path(tmp)/'raster.tif'; raster.write_bytes(b'test fixture')
            s = Session([Response(404), Response(404), Response(201), Response(200), Response(200), Response(200, pub.coverage_xml(self.m))])
            pub.publish(s, pub.BASE, self.m, raster)
            receipt = json.loads((Path(tmp)/'deliverables'/self.m['id']/'publication-receipt.json').read_text())
            self.assertTrue(receipt['metadata_uploaded'] and receipt['wms_verified'])
            self.assertEqual(s.calls[2][2]['params']['coverageName'], self.m['id'])
            self.assertEqual([c[0] for c in s.calls], ['GET','GET','PUT','PUT','PUT','GET'])

    def test_failed_upload_has_no_success_receipt(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(pub, 'ROOT', Path(tmp)):
            raster = Path(tmp)/'raster.tif'; raster.write_bytes(b'test fixture')
            s = Session([Response(404), Response(404), Response(413)])
            with self.assertRaisesRegex(RuntimeError, 'IIS'): pub.publish(s, pub.BASE, self.m, raster)
            self.assertFalse((Path(tmp)/'deliverables'/self.m['id']/'publication-receipt.json').exists())

    def test_resume_never_resends_raster(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(pub, 'ROOT', Path(tmp)), patch.object(pub, 'verify_wms', return_value=[]):
            path = Path(tmp)/'deliverables'/self.m['id']/'publication-receipt.json'
            pub.save_receipt(path, dict(base=pub.BASE, layer=self.m['layer_name'], sha256=self.m['web']['sha256'], raster_uploaded=True))
            s = Session([Response(200), Response(200), Response(200), Response(200, pub.coverage_xml(self.m))])
            pub.publish(s, pub.BASE, self.m, Path(tmp)/'unused.tif', resume=True)
            self.assertFalse(any('file.geotiff' in c[1] for c in s.calls))


if __name__ == '__main__': unittest.main()
