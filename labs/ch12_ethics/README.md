# Chapter 12 — Responsible AI

Examples extracted from Chapter 12 (GDPR right-to-erasure, PII in AI prompts,
licence compliance).

## Files

| File | Demonstrates |
|---|---|
| `delete_user_v1_noncompliant.py` | Typical AI-generated DELETE endpoint that fails GDPR Article 17 |
| `pii_guard.py` | Block AI requests when Presidio detects PII |

## How to run

```bash
pip install presidio-analyzer presidio-anonymizer anthropic
python -m spacy download en_core_web_lg
python pii_guard.py
```

For licence auditing commands and the responsible AI checklist see Tutorial 12.
