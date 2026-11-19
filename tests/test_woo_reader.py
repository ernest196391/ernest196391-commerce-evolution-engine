import io
import json
import unittest
from unittest.mock import Mock
from src.commerce_evolution_engine.woo_reader import WooReader


class ReaderTests(unittest.TestCase):
    def setUp(self):
        self.opener = Mock()
        self.data = {'id':12,'sku':'x','name':'Original','description':'<p>raw</p>',
                     'short_description':'Short','images':[{'id':34}], 'date_modified_gmt':'2026-11-19T12:00:00'}
        self.opener.open.side_effect=lambda *a,**k: io.BytesIO(json.dumps(self.data).encode())
        self.reader = WooReader('https://example.com','tenant',credentials=('key','secret'),opener=self.opener)

    def test_public_no_auth(self):
        result = self.reader.read(12,expected_sku='x')
        request = self.opener.open.call_args.args[0]
        self.assertEqual(request.get_method(),'GET')
        self.assertIsNone(request.get_header('Authorization'))
        self.assertFalse(result['canonical'])
        self.assertEqual(result['image_ids'],[34])

    def test_canonical_raw(self):
        result = self.reader.read(12,expected_sku='x',canonical=True)
        req = self.opener.open.call_args.args[0]
        self.assertIn('/wc/v3/products/12?context=edit',req.full_url)
        self.assertTrue(req.has_header('Authorization'))
        self.assertTrue(result['canonical'])
        self.assertEqual(result['description'],'<p>raw</p>')

    def test_no_creds_or_identity_mismatch(self):
        with self.assertRaises(ValueError):
            WooReader('https://example.com','a',opener=self.opener).read(12,expected_sku='x',canonical=True)
        with self.assertRaises(ValueError):
            self.reader.read(12,expected_sku='wrong')
        with self.assertRaises(ValueError):
            WooReader('http://example.com','a')
