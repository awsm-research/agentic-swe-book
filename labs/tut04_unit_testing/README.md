# Tutorial 4 — Unit Testing in Practice

The ATO tax-deduction calculator and full test suite from Tutorial 4. The
tests reach 100% branch coverage as completed in Part B Step 5.

## Files

| File | Purpose |
|---|---|
| `src/tax.py` | `calculate_deduction` with six decision points |
| `tests/test_tax.py` | Eight unit tests (six base + two added in Part B) |

## How to run

```bash
uv add --dev pytest pytest-cov
pytest tests/test_tax.py -v
pytest tests/test_tax.py --cov=src --cov-branch --cov-report=term-missing -q
```

Expected: 8 tests pass, 100% branch coverage.
