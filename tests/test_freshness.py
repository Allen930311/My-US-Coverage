import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import event_census
import freshness


class FreshnessTests(unittest.TestCase):
    def test_parse_master_index(self):
        text = """Description
CIK|Company Name|Form Type|Date Filed|Filename
0000320193|APPLE INC|10-Q|2026-08-01|edgar/data/320193/example.txt
0001018724|AMAZON COM INC|8-K|2026-08-02|edgar/data/1018724/example.txt
"""
        rows = event_census.parse_master_index(text)
        self.assertEqual(rows[0]["cik"], "320193")
        self.assertEqual(rows[0]["form"], "10-Q")
        self.assertEqual(rows[1]["company"], "AMAZON COM INC")

    def test_form_actions(self):
        self.assertIn("refresh_financials", event_census.actions_for_form("10-K"))
        self.assertIn("check_material_event", event_census.actions_for_form("8-K"))

    def test_daily_index_url(self):
        template = "https://x/{year}/QTR{quarter}/master.{yyyymmdd}.idx"
        self.assertEqual(
            event_census.daily_index_url(template, __import__("datetime").date(2026, 10, 7)),
            "https://x/2026/QTR4/master.20261007.idx",
        )

    def test_timestamp_classification(self):
        rule = {"max_age_days": 2}
        now = datetime(2026, 10, 7, 12, tzinfo=timezone.utc)
        self.assertEqual(freshness.classify_timestamp("2026-10-06", rule, now), "FRESH")
        self.assertEqual(freshness.classify_timestamp("2026-10-01", rule, now), "STALE")

    def test_publication_gate_fail_closed(self):
        contract = {
            "publication_gate": {
                "always_required": ["listing_universe", "material_events"],
                "claim_scoped": {},
                "allowed_statuses": ["FRESH"],
            }
        }
        gate = freshness.publication_gate({"listing_universe": "FRESH"}, contract, [])
        self.assertFalse(gate["ready"])
        self.assertEqual(gate["blockers"]["material_events"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
