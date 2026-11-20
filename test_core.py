"""Small standard-library smoke tests for the sample PM dashboard's business rules.
Run from the repository root: python -m unittest discover -s tests -v
"""
import copy
import unittest
from datetime import date

from core import (client_update, extract_requirements, missing_questions,
                  next_id, pm_brief, project_health, seed_data, validate_import)


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.workspace = seed_data()
        self.program = self.workspace["projects"][0]
        self.asof = date(2026, 12, 10)

    def test_seed_portfolio_and_core_dimensions(self):
        self.assertEqual(len(self.workspace["projects"]), 3)
        self.assertEqual(self.program["participants"], 100)
        self.assertEqual(self.program["cohorts"], 4)
        self.assertEqual(self.program["budget"], 800000)

    def test_task_completion_updates_project_health(self):
        previous = project_health(self.program, self.asof)
        changed = next(t for t in self.program["tasks"] if t["status"] != "Done")
        changed["status"], changed["progress"] = "Done", 100
        current = project_health(self.program, self.asof)
        self.assertEqual(current["completed_tasks"], previous["completed_tasks"] + 1)
        self.assertGreater(current["completion"], previous["completion"])

    def test_blocked_approvals_and_risks_are_flagged(self):
        health = project_health(self.program, self.asof)
        self.assertTrue(health["blocked"])
        self.assertTrue(health["pending"])
        self.assertTrue(health["high_risks"])
        self.assertEqual(health["status"], "Needs attention")

    def test_requirement_extraction_stays_draft(self):
        drafts = extract_requirements(self.program["notes"])
        self.assertGreaterEqual(len(drafts), 4)
        self.assertTrue(all(d["status"] == "Needs validation" for d in drafts))
        self.assertTrue(any("100" in d["text"] for d in drafts))

    def test_client_discovery_gap_questions(self):
        self.assertTrue(any("facilitator" in q.lower() for q in missing_questions(self.program["notes"])))

    def test_traceability_and_ids(self):
        req_ids = {r["id"] for r in self.program["requirements"]}
        self.assertTrue(all(set(t["requirements"]).issubset(req_ids) for t in self.program["tasks"]))
        self.assertEqual(next_id(self.program["requirements"], "REQ-"), "REQ-008")

    def test_reports_use_current_records(self):
        brief = pm_brief(self.program, self.asof)
        update = client_update(self.program, self.asof)
        self.assertIn("T-002", brief)
        self.assertIn("2026-12-10", update)
        self.assertIn("800,000", brief)

    def test_export_shape_validation(self):
        self.assertTrue(validate_import(copy.deepcopy(self.workspace)))
        self.assertFalse(validate_import({"projects": [{}]}))


if __name__ == "__main__":
    unittest.main()
