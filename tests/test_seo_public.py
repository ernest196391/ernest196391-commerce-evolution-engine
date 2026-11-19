import tempfile
import unittest
from pathlib import Path
from src.commerce_evolution_engine.seo_public import extract,run_batch
from src.commerce_evolution_engine.catalog_worker import Worker
from src.commerce_evolution_engine.seo_audit import audit

try:
    import lxml.html
    HAS_LXML=True
except ImportError:
    HAS_LXML=False


@unittest.skipUnless(HAS_LXML,'lxml optional')
class PublicSEOTests(unittest.TestCase):
    def test_extract_only_summary(self):
        url='https://example.test/producto/fan/'
        page=f'''<html><head><link rel="canonical" href="{url}"></head><body>
        <h1>Fan</h1><div class="summary"><p class="price">US$85.00</p><p class="stock">Encargo 24 h</p></div>
        <p class="price">US$4.00</p><script type="application/ld+json">{{"@type":"Product","name":"Fan","image":"https://example.test/photo.png","offers":{{"@type":"Offer","price":"85.00","priceCurrency":"USD","availability":"https://schema.org/OutOfStock"}}}}</script></body></html>'''
        row=extract(page,url,'cv')
        self.assertEqual(audit(row)['findings'],['on_request_semantics_review'])
        self.assertEqual(row['visible_price'],'85.00')

    def test_scope_before_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            w=Worker(Path(tmp))
            for url in ('https://evil.test/producto/fan/','https://example.test/wp-admin/', 'https://example.test/producto/fan/?x=1'):
                with self.assertRaises(ValueError):
                    run_batch(w,origin='https://example.test',tenant='cv',urls=[url],opener=object())
