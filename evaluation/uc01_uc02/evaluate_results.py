#!/usr/bin/env python3
"""Score a Code Review Agent result file against a separately held oracle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _findings(record: Any) -> list[dict[str, Any]]:
    if isinstance(record, dict):
        value = record.get("findings", [])
        return value if isinstance(value, list) else []
    return []


def evaluate(results: dict[str, Any], oracle: dict[str, Any], tolerance: int = 3) -> dict[str, Any]:
    if results.get("dataset_id") != oracle.get("dataset_id"):
        raise ValueError("Results and oracle dataset_id do not match.")
    if tolerance < 0:
        raise ValueError("tolerance must be nonnegative")

    totals: dict[str, dict[str, Any]] = {}
    category_totals: dict[str, dict[str, int]] = {}
    case_rows: list[dict[str, Any]] = []
    for case_id, expected_case in oracle.get("cases", {}).items():
        uc = "UC01" if case_id.startswith("U1-") else "UC02"
        bucket = totals.setdefault(uc, {
            "tp": 0, "fp": 0, "fn": 0, "expected": 0, "suggestions_expected": 0,
            "suggestions_present": 0, "locations_within_tolerance": 0,
            "severity_matches": 0,
            "uc02_expected_citations": 0, "uc02_valid_citations": 0,
            "exact_line_matches": 0, "retrieval_relevant": 0, "retrieval_hits_at_5": 0,
        })
        expected = expected_case.get("findings", [])
        result_case = results.get("cases", {}).get(case_id)
        actual = _findings(result_case)
        bucket["expected"] += len(expected)
        matched_actual: set[int] = set()
        matched_expected: set[int] = set()
        for expected_index, wanted in enumerate(expected):
            category_bucket = category_totals.setdefault(wanted.get("category", "other"), {"tp": 0, "fp": 0, "fn": 0})
            if wanted.get("suggestion_required"):
                bucket["suggestions_expected"] += 1
            if wanted.get("rule_id"):
                bucket["uc02_expected_citations"] += 1
                if uc == "UC02":
                    bucket["retrieval_relevant"] += 1
                    retrieved = result_case.get("retrieved_rule_ids", []) if isinstance(result_case, dict) else []
                    if wanted["rule_id"] in retrieved[:5]:
                        bucket["retrieval_hits_at_5"] += 1
            match_index = None
            for actual_index, got in enumerate(actual):
                if actual_index in matched_actual or not isinstance(got, dict):
                    continue
                if got.get("file") != wanted.get("file"):
                    continue
                if got.get("side", "RIGHT") != wanted.get("side", "RIGHT"):
                    continue
                if got.get("category") != wanted.get("category"):
                    continue
                try:
                    line_ok = abs(int(got.get("line", -10**9)) - int(wanted["line"])) <= tolerance
                except (TypeError, ValueError):
                    line_ok = False
                if not line_ok:
                    continue
                rule_id = wanted.get("rule_id")
                if rule_id and rule_id not in (got.get("rule_ids") or []):
                    continue
                match_index = actual_index
                break
            if match_index is None:
                bucket["fn"] += 1
                category_bucket["fn"] += 1
                continue
            matched_actual.add(match_index)
            matched_expected.add(expected_index)
            bucket["tp"] += 1
            category_bucket["tp"] += 1
            bucket["locations_within_tolerance"] += 1
            got = actual[match_index]
            if int(got.get("line", -1)) == int(wanted["line"]):
                bucket["exact_line_matches"] += 1
            if got.get("severity") == wanted.get("severity"):
                bucket["severity_matches"] += 1
            if wanted.get("suggestion_required") and got.get("suggestion"):
                bucket["suggestions_present"] += 1
            if wanted.get("rule_id") and wanted["rule_id"] in (got.get("rule_ids") or []):
                bucket["uc02_valid_citations"] += 1

        extra = len(actual) - len(matched_actual)
        bucket["fp"] += extra
        for actual_index, got in enumerate(actual):
            if actual_index not in matched_actual and isinstance(got, dict):
                category = got.get("category", "unclassified")
                category_totals.setdefault(category, {"tp": 0, "fp": 0, "fn": 0})["fp"] += 1
        case_rows.append({
            "case_id": case_id,
            "use_case": uc,
            "kind": expected_case.get("kind", "unknown"),
            "expected_findings": len(expected),
            "actual_findings": len(actual),
            "tp": len(matched_expected),
            "fp": extra,
            "fn": len(expected) - len(matched_expected),
        })

    summary: dict[str, Any] = {}
    for uc, item in totals.items():
        tp, fp, fn = item["tp"], item["fp"], item["fn"]
        precision = tp / (tp + fp) if tp + fp else (1.0 if tp + fn == 0 else 0.0)
        recall = tp / (tp + fn) if tp + fn else 1.0
        summary[uc] = {
            **item,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(2 * precision * recall / (precision + recall), 4) if precision + recall else 0.0,
            "location_accuracy_within_tolerance": round(item["locations_within_tolerance"] / tp, 4) if tp else 0.0,
            "severity_accuracy": round(item["severity_matches"] / tp, 4) if tp else 0.0,
            "exact_line_rate": round(item["exact_line_matches"] / tp, 4) if tp else 0.0,
            "suggestion_presence_rate": round(item["suggestions_present"] / item["suggestions_expected"], 4) if item["suggestions_expected"] else None,
            "rule_citation_rate": round(item["uc02_valid_citations"] / item["uc02_expected_citations"], 4) if item["uc02_expected_citations"] else None,
            "rule_recall_at_5": round(item["retrieval_hits_at_5"] / item["retrieval_relevant"], 4) if item["retrieval_relevant"] else None,
        }
    category_metrics = {}
    for category, item in category_totals.items():
        tp, fp, fn = item["tp"], item["fp"], item["fn"]
        precision = tp / (tp + fp) if tp + fp else (1.0 if tp + fn == 0 else 0.0)
        recall = tp / (tp + fn) if tp + fn else 1.0
        category_metrics[category] = {
            **item,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(2 * precision * recall / (precision + recall), 4) if precision + recall else 0.0,
        }
    return {
        "schema_version": "1.0",
        "dataset_id": results["dataset_id"],
        "tolerance_lines": tolerance,
        "metrics": summary,
        "categories": category_metrics,
        "cases": case_rows,
        "limitations": [
            "Suggestion presence is measured; patch applicability and syntax are not executed by this scorer.",
            "This scorer measures only supplied oracle cases and does not establish live GitHub publication acceptance.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path, help="Agent output JSON; see RESULTS_FORMAT.md")
    parser.add_argument("--oracle", type=Path, required=True, help="Private ground_truth.json")
    parser.add_argument("--output", type=Path, help="Write metrics JSON to this path")
    parser.add_argument("--tolerance", type=int, default=3)
    args = parser.parse_args()
    result = evaluate(json.loads(args.results.read_text(encoding="utf-8")),
                      json.loads(args.oracle.read_text(encoding="utf-8")), args.tolerance)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
