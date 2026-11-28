# Agent result format

Save the agent's output separately from the input cases and submit it to `evaluate_results.py` after the review. Do not pass the private oracle to the agent or include it in the prompt/context.

```json
{
  "dataset_id": "se373-uc01-uc02-acceptance-v1",
  "cases": {
    "U1-01": {
      "findings": [
        {
          "file": "review_lab/catalog.py",
          "line": 26,
          "side": "RIGHT",
          "severity": "major",
          "category": "logic",
          "rule_ids": [],
          "suggestion": "return PRODUCTS[sku]"
        }
      ]
    },
    "U2-01": {"findings": [], "retrieved_rule_ids": ["PY-NAME-01", "PY-LOG-02"]}
  }
}
```

`line` must be the line number in the PR head version; `side` must be `RIGHT` or `LEFT`. UC02 convention findings must include the cited `rule_ids`. Missing case entries are scored as no findings. Unknown case IDs are ignored; only cases in the oracle are scored.

The scorer reports overall and per-category precision/recall/F1, exact and ±3-line location rates, severity match rate, suggestion presence, UC02 citation rate, and Recall@5 from `retrieved_rule_ids`. Include only rule IDs actually returned by the retriever, in rank order. It does **not** run suggested patches, parse the resulting code, test live GitHub publication, or decide whether a finding is semantically correct beyond the curated oracle match.
