import json
import tempfile
import unittest
from pathlib import Path
from src.commerce_evolution_engine.catalog_worker import Worker
from src.commerce_evolution_engine.daily_catalog import run_daily


class DailyTests(unittest.TestCase):
    def test_batch_restart_budget_and_bad_entry(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            rows=[]
            for pid in ('1','2'):
                folder=root/pid
                folder.mkdir()
                for k,data in {'product':{'tenant_id':'a','product_id':pid,'name':'Example'},
                               'research':{},'draft':{'id':pid,'name':'Example'}}.items():
                    (folder/(k+'.json')).write_text(json.dumps(data))
                rows.append({**{k:f'{pid}/{k}.json' for k in ('product','research','draft')},'photos':pid})
            manifest=root/'batch.json'
            manifest.write_text(json.dumps(rows+[{'product':'../outside.json'}]))
            first=run_daily(Worker(root/'state'),'a',manifest,daily_limit=1)
            self.assertEqual(len(first['completed_this_run']),1)
            self.assertEqual(first['queue_totals'],{'blocked':1,'queued':1})
            self.assertEqual(len(first['invalid_rows']),1)
            restarted=Worker(root/'state')
            second=run_daily(restarted,'a',manifest,daily_limit=1)
            self.assertEqual(second['submitted_job_ids'],first['submitted_job_ids'])
            self.assertEqual(second['completed_this_run'],[])
            next_day=restarted.queue.clock()+86400
            restarted.queue.clock=lambda: next_day
            third=run_daily(restarted,'a',manifest,daily_limit=1)
            self.assertEqual(len(third['completed_this_run']),1)
            self.assertEqual(third['queue_totals'],{'blocked':2})
            self.assertFalse(third['publish_allowed'])
