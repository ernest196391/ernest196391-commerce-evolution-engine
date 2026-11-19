import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.commerce_evolution_engine.catalog_worker import Worker, encode
from src.commerce_evolution_engine.seo_daily import tick


class DailySEOTests(unittest.TestCase):
    def test_resume_budget_and_gallery(self):
        with tempfile.TemporaryDirectory() as tmp:
            now = [86400.0]
            a,b = ['https://example.test/producto/'+s+'/' for s in ('a','b')]
            args = dict(origin='https://example.test',tenant='cv',urls=[a,b],daily_limit=3,tick_limit=1)
            calls=[]
            def fake(w, *, origin, tenant, urls, opener):
                calls.extend(urls)
                if len(calls)==1:
                    raise KeyboardInterrupt()
                report={'complete':True,'reports':[{'tenant_id':tenant,'url':urls[0],'images':['https://example.test/image.jpg'],'findings':[],'publish_allowed':False}]}
                return {**report,'report_hash':w.put(encode(report))}
            with patch('src.commerce_evolution_engine.seo_daily.run_batch',side_effect=fake):
                w=Worker(Path(tmp)); w.queue.clock=lambda:now[0]
                with self.assertRaises(KeyboardInterrupt): tick(w,**args)
                w=Worker(Path(tmp)); w.queue.clock=lambda:now[0]
                self.assertEqual(tick(w,**args)['pending_urls'],[a])
                self.assertEqual(tick(w,**args)['attempts'],2)
                now[0]+=121
                result=tick(w,**args)
                self.assertTrue(result['complete'])
                self.assertTrue(all('shared_gallery_review' in r['findings'] for r in result['reports']))
                self.assertEqual(tick(w,**args)['report_hash'],result['report_hash'])
                self.assertEqual(calls,[a,b,a])
                with self.assertRaises(ValueError): tick(w,**{**args,'daily_limit':4})
                now[0]+=86400
                self.assertEqual(tick(w,**args)['attempts'],1)

    def test_failure_exhausts_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            w=Worker(Path(tmp)); args=dict(origin='https://example.test',tenant='cv',urls=['https://example.test/producto/a/'],daily_limit=1,tick_limit=1)
            with patch('src.commerce_evolution_engine.seo_daily.run_batch',return_value={'complete':False,'report_hash':'unused'}) as run:
                self.assertFalse(tick(w,**args)['complete'])
                self.assertFalse(tick(w,**args)['complete'])
                self.assertEqual(run.call_count,1)

    def test_prioritize_not_yet_audited_next_day(self):
        with tempfile.TemporaryDirectory() as tmp:
            w=Worker(Path(tmp)); now=[86400.0]; w.queue.clock=lambda:now[0]
            urls=['https://example.test/producto/'+s+'/' for s in ('a','b')]
            args=dict(origin='https://example.test',tenant='cv',urls=urls,daily_limit=1,tick_limit=1)
            def fake(w, *, origin, tenant, urls, opener):
                report={'complete':True,'reports':[{'tenant_id':tenant,'url':urls[0],'images':[],'findings':[]}]}
                return {**report,'report_hash':w.put(encode(report))}
            with patch('src.commerce_evolution_engine.seo_daily.run_batch',side_effect=fake):
                self.assertEqual(tick(w,**args)['pending_urls'],[urls[1]])
                now[0]+=86400
                self.assertEqual(tick(w,**args)['pending_urls'],[urls[0]])
