# Chapter 4 — Testing

Calculator module and pytest/unittest test examples extracted from Chapter 4
(Section 4.6 Unit Testing in Python).

## Files

| File | Purpose |
|---|---|
| `src/calculator.py` | The `add`/`subtract`/`multiply`/`divide` calculator |
| `tests/test_calculator.py` | AAA-pattern unit tests, including `assertRaises` examples |

## How to run

```bash
pytest tests/ -v
pytest --cov=src --cov-report=term-missing
pytest --cov=src --cov-branch --cov-report=term-missing
```
