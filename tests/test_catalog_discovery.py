import io,json,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock
from src.commerce_evolution_engine.catalog_worker import Worker
from src.commerce_evolution_engine.catalog_discovery import Discovery
from src.commerce_evolution_engine.woo_reader import WooReader


class DiscoveryTests(unittest.TestCase):
    def test_resume_and_change_detection(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            opener=Mock()
            def page(pid,name='Product example'):
                response=io.BytesIO(json.dumps([dict(id=pid,sku=str(pid),name=name,description='text',short_description='short',images=[{'id':123}])]).encode())
                response.headers={'X-WP-TotalPages':'2'}
                return response
            opener.open.side_effect=[page(1),OSError('offline'),page(2),page(1),page(2,'Changed')]
            reader=WooReader('https://example.com','a',credentials=('key','secret'),opener=opener)
            self.assertEqual(Discovery(Worker(root)).scan(reader,max_pages=1)['changed'],1)
            with self.assertRaises(OSError):
                Discovery(Worker(root)).scan(reader,max_pages=1)
            result=Discovery(Worker(root)).scan(reader,max_pages=1)
            self.assertTrue(result['cycle_complete'])
            self.assertEqual(len(result['pending']),2)
            self.assertIn('page=2&',opener.open.call_args.args[0].full_url)
            result=Discovery(Worker(root)).scan(reader,max_pages=2)
            self.assertEqual(result['changed'],1)
            self.assertFalse(result['publish_allowed'])
            self.assertTrue(all(c.args[0].get_method()=='GET' and not c.args[0].has_header('Authorization') for c in opener.open.call_args_list))
            with self.assertRaises(ValueError):
                Discovery(Worker(root)).scan(WooReader('https://other.example','a',opener=opener))
