# Tutorial 7 — Well-Tested App

Sample pytest test suite for the `AssignJobService` from Tutorial 6/7.

## Files

| File | Purpose |
|---|---|
| `tests/test_job_service.py` | Sample-answer test suite from Activity 1 |

## How to use

This file imports `src.service.job_service` and `src.domain.repair_job` —
both produced by the AI-driven implementation in Tutorial 6 Activity 3. Drop
this file into the Tutorial 6 project structure once those modules exist.

```bash
uv add --dev pytest pytest-cov
pytest tests/test_job_service.py -v --cov=src/service --cov-report=term-missing
```
