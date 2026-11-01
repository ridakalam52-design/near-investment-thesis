"""Offline tests: rebuild from committed snapshots and check outputs are complete and consistent.

    python -m unittest discover -s tests -v
"""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r = subprocess.run([sys.executable, "build.py", "--offline"], cwd=ROOT, capture_output=True, text=True)
        cls.stdout = r.stdout + r.stderr
        assert r.returncode == 0, cls.stdout
        cls.metrics = json.loads((ROOT / "data/metrics.json").read_text())
        cls.model = json.loads((ROOT / "data/model.json").read_text())
        cls.signals = json.loads((ROOT / "data/signals.json").read_text())
        cls.thesis = (ROOT / "THESIS.md").read_text()
        cls.html = (ROOT / "docs/index.html").read_text()

    def test_outputs_exist(self):
        for p in ["docs/index.html", "docs/data.json", "THESIS.md", "data/sources_log.json"]:
            self.assertTrue((ROOT / p).exists(), p)

    def test_no_unfilled_placeholders(self):
        self.assertNotIn("{{", self.thesis)
        self.assertNotIn("%%", self.html)

    def test_every_metric_has_provenance(self):
        for k, m in self.metrics["headline"].items():
            for f in ("unit", "source", "how"):
                self.assertIn(f, m, k)
            self.assertTrue(m["source"], k)

    def test_core_metrics_present(self):
        H = self.metrics["headline"]
        for k in ["total_supply_rpc", "total_staked", "staking_ratio_pct", "max_inflation_rate_pct",
                  "txns_30d_avg", "active_accounts_30d_avg", "fees_near_30d", "intents_volume_30d",
                  "stablecoin_supply_usd", "tvl_usd"]:
            self.assertIsNotNone(H[k]["value"], k)

    def test_sanity_ranges(self):
        H = self.metrics["headline"]
        self.assertTrue(0 < H["staking_ratio_pct"]["value"] < 100)
        self.assertTrue(0 <= H["max_inflation_rate_pct"]["value"] < 10)
        self.assertTrue(H["total_supply_rpc"]["value"] > 1e9)

    def test_model_consistency(self):
        self.assertEqual(self.model["status"], "ok")
        i = self.model["inputs"]
        y0 = self.model["scenarios"]["base"]["years"][0]
        expect = i["total_supply"] * i["max_inflation_rate"] * i["issuance_realization"]
        self.assertAlmostEqual(y0["issuance_near"], expect, delta=1)
        burn = i["tx_per_day"] * 365 * i["fee_per_tx_near"] * i["burn_share"]
        self.assertAlmostEqual(y0["burn_near"], burn, delta=1)

    def test_signals_evaluated(self):
        self.assertTrue(self.signals)
        for s in self.signals:
            self.assertIn(s["status"], {"BULL", "BEAR", "UNKNOWN"})

    def test_dashboard_has_charts(self):
        self.assertGreaterEqual(self.html.count("<canvas"), 6)


if __name__ == "__main__":
    unittest.main()
