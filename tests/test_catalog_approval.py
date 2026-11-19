import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.commerce_evolution_engine.catalog_worker import Worker
from src.commerce_evolution_engine.catalog_approval import ApprovalLedger
from src.commerce_evolution_engine.catalog_supervisor import HUMAN_CHECKS
from src.commerce_evolution_engine.content_studio_adapter import prepare_studio_request, BRIEF
from src.commerce_evolution_engine.studio_roundtrip import verify_roundtrip


class ApprovalTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        photos = root/'photos'
        photos.mkdir()
        self.worker = Worker(root/'state')
        product = {'tenant_id':'a','product_id':'12','name':'Example'}
        draft = {'id':'12','sku':'SKU','name':'New','description':'New text','short_description':'New short'}
        self.job = self.worker.submit(product,{},draft,photos)
        with patch('src.commerce_evolution_engine.catalog_worker.review',return_value={'status':'awaiting_human_review','tenant_id':'a','product_id':'12','blockers':[],'publish_allowed':False}):
            self.worker.run('a')
        self.ledger = ApprovalLedger(self.worker)
        self.before = {'tenant_id':'a','id':12,'sku':'SKU','name':'Old','description':'Old text','short_description':'Old short','price':'50','stock_quantity':5,'canonical':True,'source':'woo_rest_edit'}
        self.key = self.ledger.prepare('a',self.job,self.before)
        self.checks = dict.fromkeys(HUMAN_CHECKS,True)

    def approve(self):
        self.ledger.record('a',self.key,actor='test-only',decision='approved',checks=self.checks)

    def test_review_then_reverse(self):
        with self.assertRaises(ValueError):
            self.ledger.preview('a',self.key,self.before)
        self.approve()
        result = self.ledger.preview('a',self.key,self.before)
        self.assertFalse(result['publish_allowed'])
        self.assertEqual(set(result['changes']),{'name','description','short_description'})
        after = {**self.before,**result['changes']}
        reverse = self.ledger.preview('a',self.key,after,rollback=True)
        self.assertEqual({**after,**reverse['changes']},self.before)

    def test_refuse_incomplete_and_revoked(self):
        with self.assertRaises(ValueError):
            self.ledger.record('a',self.key,actor='test',decision='approved',checks={})
        self.approve()
        self.ledger.record('a',self.key,actor='test',decision='revoked')
        with self.assertRaises(ValueError):
            self.ledger.preview('a',self.key,self.before)

    def test_identity_and_concurrent_change(self):
        self.approve()
        for current in ({**self.before,'id':13},{**self.before,'name':'Another edit'},{**self.before,'tenant_id':'b'}):
            with self.assertRaises(ValueError):
                self.ledger.preview('a',self.key,current)
        with self.assertRaises(ValueError):
            self.ledger.prepare('a',self.job,{**self.before,'id':'12'})

    def test_cross_tenant_and_exact_plan(self):
        self.approve()
        new = self.ledger.prepare('a',self.job,{**self.before,'name':'New baseline'})
        with self.assertRaises(ValueError):
            self.ledger.preview('a',new,{**self.before,'name':'New baseline'})
        with self.assertRaises(ValueError):
            self.ledger.preview('b',self.key,self.before)

    def test_public_observation_cannot_prepare_reversal(self):
        with self.assertRaises(ValueError):
            self.ledger.prepare('a',self.job,{**self.before,'canonical':False,'source':'woo_store_public'})

    def studio_fixture(self):
        current = {**self.before,'status':'publish','image_ids':[34,35]}
        studio = {'id':12,'name':'Old','description':'Old text','short':'Old short',
                  'status':'publish','image_id':34,'gallery':[35], 'version':'a'*64,
                  'brief':{**dict.fromkeys(BRIEF,'existing'),'duda':'matrix'}}
        return current, studio

    def test_studio_forward_and_rollback(self):
        current, studio = self.studio_fixture()
        with self.assertRaises(ValueError):
            prepare_studio_request(self.ledger,'a',self.key,current,studio)
        self.approve()
        plan = prepare_studio_request(self.ledger,'a',self.key,current,studio)
        self.assertFalse(plan['execute_allowed'])
        self.assertTrue(plan['would_update_live'])
        self.assertEqual(set(plan['body']), {'id','version','name','description','short','brief'})
        self.assertEqual(plan['body']['brief'],dict.fromkeys(BRIEF,'existing'))
        after = {**current,**self.ledger.preview('a',self.key,current)['changes']}
        new_studio = {**studio,'name':after['name'],'description':after['description'],
                      'short':after['short_description'],'version':'b'*64}
        reverse = prepare_studio_request(self.ledger,'a',self.key,after,new_studio,rollback=True)
        self.assertEqual(reverse['body']['name'],current['name'])
        self.assertEqual(reverse['body']['description'],current['description'])
        self.assertEqual(reverse['body']['short'],current['short_description'])
        self.assertEqual(reverse['body']['version'],'b'*64)

    def test_studio_rejects_unsafe_projection(self):
        current, studio = self.studio_fixture()
        self.approve()
        for update in ({'id':13},{'version':'bad'},{'status':'draft'},{'gallery':[99]},
                       {'short':'changed'},{'brief':{}},{'brief':{**studio['brief'],'unknown':'keep'}}):
            with self.subTest(update=update), self.assertRaises(ValueError):
                prepare_studio_request(self.ledger,'a',self.key,current,{**studio,**update})
        self.ledger.record('a',self.key,actor='test',decision='revoked')
        with self.assertRaises(ValueError):
            prepare_studio_request(self.ledger,'a',self.key,current,studio)

    def test_studio_roundtrip_evidence(self):
        current, studio = self.studio_fixture()
        current.update(type='simple',regular_price='50',sale_price='',stock_status='instock',manage_stock=True)
        self.approve()
        changes = self.ledger.preview('a',self.key,current)['changes']
        before = {'woo':current,'studio':studio}
        after = {'woo':{**current,**changes},'studio':{**studio,'name':changes['name'],
                 'description':changes['description'],'short':changes['short_description'],'version':'b'*64}}
        restored = {'woo':dict(current),'studio':dict(studio)}
        result = verify_roundtrip(self.ledger,'a',self.key,before,after,restored)
        self.assertEqual(result['status'],'evidence_consistent')
        self.assertFalse(result['server_certified'])
        for change in ({'stock_quantity':0},{'price':'99'},{'name':'not restored'},{'image_ids':[34]}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                verify_roundtrip(self.ledger,'a',self.key,before,after,{**restored,'woo':{**current,**change}})
        with self.assertRaises(ValueError):
            verify_roundtrip(self.ledger,'a',self.key,before,after,{**restored,'studio':{**studio,'version':'c'*64}})
