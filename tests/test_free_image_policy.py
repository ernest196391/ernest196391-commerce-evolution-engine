import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timezone, timedelta
from src.commerce_evolution_engine.free_image_policy import reserve

class FreeImagePolicyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / "ledger.sqlite"
        self.now = datetime(2026, 11, 19, 12, tzinfo=timezone.utc)
        self.args = dict(job_id="fixture-1", account_key="fixture", certified_account_key="fixture",
                         plan="Workers Free", checked_at=self.now, neurons_used=0,
                         approved=True, now=self.now)

    def call(self, **changes):
        return reserve(self.db, **(self.args | changes))

    def test_reserves_before_transport_and_blocks_duplicate(self):
        result = self.call()
        self.assertEqual(result["max_additional_usd"], 0)
        self.assertEqual(result["estimated_neurons"], 110)
        self.assertFalse(result["paid_fallback"])
        with self.assertRaises(ValueError):
            self.call(job_id="second")
        later = self.now + timedelta(days=1)
        with self.assertRaises(ValueError):
            self.call(now=later, checked_at=later)
        self.assertEqual(self.call(now=later, checked_at=later, job_id="second")["day_utc"], "2026-11-20")

    def test_rejects_unsafe_inputs(self):
        for changes in (dict(plan="Workers Paid"), dict(certified_account_key="other"),
                        dict(approved=False), dict(neurons_used=9800), dict(neurons_used=None),
                        dict(checked_at=self.now-timedelta(hours=2)),
                        dict(output_size=(2048,2048)), dict(input_size=(1024,1024))):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.call(**changes)

if __name__ == "__main__":
    unittest.main()
