import tempfile
import unittest
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from src.commerce_evolution_engine.catalog_queue import CatalogQueue


class CatalogQueueTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / 'queue.sqlite'
        self.now = 100000
        self.q = CatalogQueue(self.path, clock=lambda: self.now)

    def test_idempotency_and_tenant(self):
        job = self.q.enqueue('a','sku','v1')
        self.assertEqual(job,self.q.enqueue('a','sku','v1'))
        self.assertNotEqual(job,self.q.enqueue('a','sku','v2'))
        self.assertNotEqual(job,self.q.enqueue('b','sku','v1'))
        self.assertEqual(len(self.q.snapshot('a')),2)

    def test_priority_and_budget(self):
        self.q.enqueue('a','low','v1',1)
        high = self.q.enqueue('a','high','v1',9)
        self.assertEqual(self.q.claim('a',daily_limit=1)['id'],high)
        self.assertIsNone(self.q.claim('a',daily_limit=1))
        self.now += 86400
        self.assertIsNotNone(self.q.claim('a',daily_limit=1))

    def test_recovery_and_stale_worker(self):
        job = self.q.enqueue('a','sku','v1')
        first = self.q.claim('a',lease_seconds=5)
        self.now += 6
        reopened = CatalogQueue(self.path,clock=lambda: self.now)
        second = reopened.claim('a')
        self.assertEqual(second['id'],job)
        self.assertNotEqual(first['token'],second['token'])
        self.assertFalse(reopened.finish('a',job,first['token'],state='awaiting_review',result_hash='old'))
        self.assertFalse(reopened.finish('b',job,second['token'],state='awaiting_review',result_hash='wrong'))
        self.assertTrue(reopened.finish('a',job,second['token'],state='awaiting_review',result_hash='new'))
        self.assertEqual(reopened.snapshot('a')[0]['result_hash'],'new')
        self.assertIsNone(reopened.claim('a'))

    def test_exhausted_attempts_block(self):
        self.q.enqueue('a','sku','v1')
        self.q.claim('a',lease_seconds=1,max_attempts=1)
        self.now += 2
        self.assertIsNone(self.q.claim('a',max_attempts=1))
        self.assertEqual(self.q.snapshot('a')[0]['state'],'blocked')

    def test_concurrent_workers_only_one_claim(self):
        self.q.enqueue('a','sku','v1')
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(lambda _: self.q.claim('a'),range(4)))
        self.assertEqual(sum(x is not None for x in results),1)

    def test_publish_not_supported(self):
        job = self.q.enqueue('a','sku','v1')
        claim = self.q.claim('a')
        with self.assertRaises(ValueError):
            self.q.finish('a',job,claim['token'],state='published',result_hash='x')
