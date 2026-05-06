# Tutorial 10 — Refactor to Reduce Complexity

The four staged versions of `shipping.py` from Tutorial 10, plus the
`estimate_delivery_days` follow-up activity, plus the test suite that must
remain green at every stage.

## Files

| File | Stage | Cyclomatic complexity |
|---|---|---|
| `src/shipping_v1_initial.py` | Tutorial 10 Step 2 starting point | D (17) |
| `src/shipping_v2_guard.py` | Stage 1 — guard clauses extracted | C (~12) |
| `src/shipping_v3_lookup.py` | Stage 2 — lookup table for rates | A (~5) |
| `src/shipping_v4_extract.py` | Stage 3 — modifier helper extracted | A (1) |
| `src/estimate_delivery_initial.py` | Step 5 activity, pre-refactor | D-range |
| `tests/test_shipping.py` | Test contract — must stay green at every stage | — |

## How to run

Pick one shipping version, copy or symlink it as `src/shipping.py` (and
append the `estimate_delivery_days` definition for the Step 5 activity), then:

```bash
uv add --dev pytest radon
uv run pytest tests/ -v
uv run radon cc src/shipping.py -a -s
```
