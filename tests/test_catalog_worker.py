import tempfile
import unittest
import json
from pathlib import Path
from unittest.mock import patch

from src.commerce_evolution_engine.catalog_worker import Worker


class WorkerTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.photos = self.root / 'photos'
        self.photos.mkdir()
        self.worker = Worker(self.root / 'state')
        self.product = {'tenant_id':'a','product_id':'1','name':'Test product','source_image':'original','source_image_verified':False}
        self.research = {'tenant_id':'a','product_id':'1','identity_status':'unknown'}
        self.draft = {'id':'1','name':'Test product','description':'Details','short_description':'Summary'}

    def submit(self):
        return self.worker.submit(self.product,self.research,self.draft,self.photos)

    def test_restart_and_idempotency(self):
        first = self.submit()
        self.assertEqual(first,self.submit())
        worker = Worker(self.root / 'state')
        result = worker.run('a')
        self.assertEqual(len(result),1)
        self.assertEqual(result[0]['state'],'blocked')
        report = json.loads(worker.get(result[0]['result_hash']))
        self.assertFalse(report['publish_allowed'])
        self.assertEqual(worker.run('a'),[])

    def test_snapshot_and_changed_image(self):
        photo = self.photos / '01-hero.png'
        photo.write_bytes(b'first')
        first = self.submit()
        photo.write_bytes(b'second')
        self.assertNotEqual(first,self.submit())
        seen = []
        def inspect(product,research,draft,folder):
            seen.append((folder/'01-hero.png').read_bytes())
            return {'status':'awaiting_human_review','publish_allowed':False}
        with patch('src.commerce_evolution_engine.catalog_worker.review',side_effect=inspect):
            self.assertEqual(len(self.worker.run('a')),2)
        self.assertEqual(seen,[b'first',b'second'])

    def test_tamper_blocks(self):
        self.submit()
        key = self.worker.queue.snapshot('a')[0]['fingerprint']
        (self.worker.objects/key).write_bytes(b'tampered')
        result = self.worker.run('a')[0]
        self.assertEqual(result['state'],'blocked')
        self.assertIn('entrada_invalida_o_no_disponible',json.loads(self.worker.get(result['result_hash']))['blockers'])
