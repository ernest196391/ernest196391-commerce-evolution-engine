import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.commerce_evolution_engine.catalog_worker import Worker
from src.commerce_evolution_engine.catalog_approval import ApprovalLedger
from src.commerce_evolution_engine.catalog_supervisor import HUMAN_CHECKS


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
        self.before = {'tenant_id':'a','id':12,'sku':'SKU','name':'Old','description':'Old text','short_description':'Old short','price':'50','stock_quantity':5}
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
