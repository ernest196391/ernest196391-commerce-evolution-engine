import tempfile,unittest
from pathlib import Path
from unittest.mock import Mock
from src.commerce_evolution_engine.catalog_worker import Worker
from src.commerce_evolution_engine.research_pipeline import ResearchPipeline


class ResearchPipelineTests(unittest.TestCase):
    def test_revision_and_evidence_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            worker=Worker(root/'state')
            pipeline=ResearchPipeline(worker)
            reader=Mock(tenant='a',origin='https://example.com')
            row=dict(id=12,sku='SKU',name='Example model',description='text',short_description='short',image_ids=[1],tenant_id='a',canonical=False)
            reader.public_page.return_value=([row],True)
            pipeline.discovery.scan(reader)
            brief=pipeline.prepare('a')[0]
            key=brief['observation_hash']
            self.assertFalse(brief['publish_allowed'])
            self.assertEqual(ResearchPipeline(Worker(root/'state')).prepare('a'),[])
            self.assertEqual(ResearchPipeline(Worker(root/'state')).pending('a'),[brief])
            product=dict(tenant_id='a',product_id='12',name='Example model',source_image='original.png',source_image_verified=True)
            research=dict(tenant_id='a',product_id='12',identity_status='exact_verified',sources=[dict(id='manual',type='manual',reference='example')],claims=[dict(name='Model',value='Example',status='verified',source_ids=['manual'])])
            draft=dict(id='12',sku='SKU',name='Example model',description='Text',short_description='Short')
            with self.assertRaises(ValueError):
                pipeline.submit('a',12,key,product,{**research,'claims':[]},draft,root)
            job=pipeline.submit('a',12,key,product,research,draft,root)
            self.assertEqual(pipeline.pending('a'),[])
            self.assertEqual(pipeline.submit('a',12,key,product,research,draft,root),job)
            reader.public_page.return_value=([{**row,'name':'Changed'}],True)
            pipeline.discovery.scan(reader)
            self.assertEqual(len(pipeline.prepare('a')),1)
            with self.assertRaises(ValueError):
                pipeline.submit('a',12,key,product,research,draft,root)
