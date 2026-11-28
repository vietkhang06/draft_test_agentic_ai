from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "evaluation" / "uc01_uc02"
sys.path.insert(0, str(PUBLIC))
from evaluate_results import evaluate  # noqa: E402


class EvaluationHarnessTests(unittest.TestCase):
    def setUp(self):
        self.oracle = {
            "dataset_id": "harness-unit-fixture",
            "cases": {
                "U1-01": {"kind": "bug", "findings": [{
                    "file": "a.py", "line": 10, "side": "RIGHT", "category": "logic",
                    "severity": "major", "suggestion_required": True,
                }]},
                "U1-08": {"kind": "clean", "findings": []},
                "U1-11": {"kind": "bug", "findings": [{
                    "file": "b.py", "line": 20, "side": "LEFT", "category": "security",
                    "severity": "critical", "suggestion_required": False,
                }]},
                "U2-01": {"kind": "bug", "findings": [{
                    "file": "rules.py", "line": 30, "side": "RIGHT", "category": "convention",
                    "severity": "minor", "rule_id": "PY-NAME-01", "suggestion_required": True,
                }]},
            },
        }

    def test_dataset_has_expected_breadth_and_clean_cases(self):
        public = json.loads((PUBLIC / "cases.json").read_text(encoding="utf-8"))
        self.assertEqual(public["case_count"], 45)
        self.assertEqual(len(public["cases"]), 45)
        self.assertEqual(len({c["case_id"] for c in public["cases"]}), 45)
        self.assertTrue(any(c["case_id"] == "U1-23" and len(c["files"]) > 1 for c in public["cases"]))
        self.assertTrue(any(c["case_id"] == "U2-19" and len(c["files"][0]["hunks"]) > 1 for c in public["cases"]))

    def test_public_inputs_do_not_contain_oracle_fields(self):
        raw = (PUBLIC / "cases.json").read_text(encoding="utf-8")
        for forbidden in ("suggestion_required", "ground_truth", '"expected"', '"kind"'):
            self.assertNotIn(forbidden, raw)

    def test_matching_uses_file_category_side_and_line_tolerance(self):
        results = {
            "dataset_id": self.oracle["dataset_id"],
            "cases": {
                "U1-01": {"findings": [{
                    "file": "a.py", "line": 12, "side": "RIGHT",
                    "category": "logic", "severity": "major", "suggestion": "return PRODUCTS[sku]",
                }]},
                "U1-08": {"findings": [{
                    "file": "a.py", "line": 24, "side": "RIGHT",
                    "category": "logic", "severity": "minor", "suggestion": None,
                }]},
                "U1-11": {"findings": [{
                    "file": "b.py", "line": 20, "side": "RIGHT",
                    "category": "security", "severity": "critical", "suggestion": None,
                }]},
                "U2-01": {"findings": [{
                    "file": "rules.py", "line": 30, "side": "RIGHT",
                    "category": "convention", "severity": "minor", "rule_ids": ["PY-NAME-01"],
                    "suggestion": "def calculate_total(lines):",
                }]},
            },
        }
        report = evaluate(results, self.oracle)
        u1 = report["metrics"]["UC01"]
        u2 = report["metrics"]["UC02"]
        self.assertEqual(u1["tp"], 1)
        self.assertEqual(u1["fp"], 2)
        self.assertEqual(u1["fn"], 1)
        self.assertEqual(u2["tp"], 1)
        self.assertEqual(u2["rule_citation_rate"], 1.0)

    def test_wrong_rule_citation_is_not_a_match(self):
        results = {
            "dataset_id": self.oracle["dataset_id"],
            "cases": {"U2-01": {"findings": [{
                "file": "src/orders/service.py", "line": 12, "side": "RIGHT",
                "category": "convention", "rule_ids": ["PY-LOG-02"],
            }]}},
        }
        metrics = evaluate(results, self.oracle)["metrics"]["UC02"]
        self.assertEqual(metrics["tp"], 0)
        self.assertEqual(metrics["fp"], 1)
        self.assertEqual(metrics["fn"], 1)
        self.assertEqual(metrics["rule_citation_rate"], 0.0)

    def test_dataset_mismatch_and_invalid_tolerance_are_rejected(self):
        with self.assertRaises(ValueError):
            evaluate({"dataset_id": "other", "cases": {}}, self.oracle)
        with self.assertRaises(ValueError):
            evaluate({"dataset_id": self.oracle["dataset_id"], "cases": {}}, self.oracle, -1)


if __name__ == "__main__":
    unittest.main()
