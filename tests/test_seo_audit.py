import unittest
from src.commerce_evolution_engine.seo_audit import audit, audit_batch


def page(slug='a', tenant='cv', stock='in_stock', price='26.00', availability='InStock'):
    url='https://example.test/product/'+slug
    return {'tenant_id':tenant,'url':url,'canonical':url,'h1':'Product',
            'visible_price':price,'visible_currency':'USD','visible_stock':stock,
            'product':{'@type':'Product','name':'Product','sku':'x',
                       'image':['https://example.test/photo.png'],
                       'offers':{'@type':'Offer','price':'26','priceCurrency':'USD',
                                 'availability':'https://schema.org/'+availability}}}


class SEOTests(unittest.TestCase):
    def test_consistent_and_mismatch(self):
        self.assertEqual(audit(page())['findings'],[])
        out=audit(page(price='27',stock='out_of_stock'))
        self.assertEqual(out['findings'],['availability_mismatch','price_or_currency_mismatch'])
        self.assertFalse(out['publish_allowed'])

    def test_on_request_and_unknown(self):
        self.assertIn('on_request_semantics_review',audit(page(stock='on_request',availability='OutOfStock'))['findings'])
        self.assertIn('availability_unverified',audit(page(stock=None))['findings'])
        self.assertIn('price_unverified',audit(page(price='NaN'))['findings'])

    def test_gallery_tenant_isolation(self):
        a,b,c=audit_batch([page('24'),page('28'),page('28',tenant='other')])
        self.assertIn('shared_gallery_review',a['findings'])
        self.assertIn('shared_gallery_review',b['findings'])
        self.assertNotIn('shared_gallery_review',c['findings'])
        self.assertNotIn('shared_gallery_review',audit_batch([page(),page()])[0]['findings'])

    def test_ambiguous_offer_and_expiration(self):
        x=page(); x['product']['offers']=[x['product']['offers']]*2
        self.assertIn('offer_missing_or_ambiguous',audit(x)['findings'])
        x=page();x['product']['offers']['priceValidUntil']='2027-12-31'
        self.assertIn('price_expiration_source_review',audit(x)['findings'])
        x['product']['sku']=123
        self.assertIn('numeric_sku_review',audit(x)['findings'])
