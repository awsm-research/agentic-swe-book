# Tutorial 12 — Licences, Privacy, and Responsible AI in Practice

PII detection, GDPR specification, and licence-audit pipeline scaffolding from
Tutorial 12 Parts A–E.

## Files

| File | Source |
|---|---|
| `test_presidio.py` | Part C Step 2 — first PII scan |
| `pii_guard.py` | Part C Steps 3 & 5 — `check_for_pii`, `safe_prompt`, `sanitize_prompt` |
| `test_pii_guard.py` | Part C Step 4 — guard sanity test |
| `anonymize_prompt.py` | Part C Step 5 — Presidio anonymisation wrapper |
| `endpoints/users_delete_v1.py` | Part B Step 1 — non-compliant generated endpoint |
| `endpoints/users_delete_v2_prompt.txt` | Part B Step 3 — compliant specification |
| `.github/workflows/compliance.yml` | Part E GitHub Actions licence-audit job |
| `.gitlab-ci.yml` | Part E GitLab CI licence-audit job |

## How to run

```bash
uv add --dev pip-licenses presidio-analyzer presidio-anonymizer
uv run python -m spacy download en_core_web_lg

uv run python test_presidio.py
uv run python test_pii_guard.py

uv run pip-licenses --format=table
uv run pip-licenses --fail-on="GPL;AGPL" --format=table
```
