# UC01/UC02 Acceptance Test Set

This benchmark contains **45 synthetic Python PR cases**, with 34 expected findings and 13 no-finding cases. It includes multi-file and multi-hunk examples, left-side/deletion comments, rename/context cases, clean changes, performance/security/test findings, policy scoping and exceptions, two prompt-injection cases, one policy-update case, and duplicate-finding pressure.

## Files

- `cases.json`: public, unlabelled PR inputs. It contains no expected finding labels.
- `team_rules.md`: trusted policy corpus supplied to the UC02 agent.
- `evaluate_results.py`: deterministic post-run scorer.
- `RESULTS_FORMAT.md`: expected result schema.

The private oracle is distributed separately as `ground_truth.json`. Keep it outside the reviewed repository, the agent process, prompts, context and retrieval index; use it only after a run. A separate local folder alone is not an access-control boundary.

## Run

```powershell
py -3 -m unittest discover -s tests -v
py -3 evaluation/uc01_uc02/evaluate_results.py .\agent-results.json --oracle 'PATH_TO_PRIVATE_ORACLE\ground_truth.json' --output .\evaluation-report.json
```

The scorer reports per-UC and per-category precision/recall/F1, exact and ±3-line location, severity accuracy, suggestion presence, citation rate and Recall@5 (if ranked `retrieved_rule_ids` are included). It does not apply suggestions, parse patched source, make live provider calls, or prove GitHub publication. Human review of the oracle is still required before treating it as instructor-approved ground truth.
