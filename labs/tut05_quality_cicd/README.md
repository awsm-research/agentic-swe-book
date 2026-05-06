# Tutorial 5 — Code Quality and CI/CD

The `.gitlab-ci.yml` from Tutorial 5 Part B that wires `ruff`, `mypy`, and
`pytest` into a three-stage pipeline. This tutorial builds on the Tutorial 4
tax calculator — see `../tut04_unit_testing/` for `src/tax.py` and
`tests/test_tax.py`.

## Files

| File | Purpose |
|---|---|
| `.gitlab-ci.yml` | Lint → typecheck → test pipeline |

## How to run

Drop this file into the root of the Tutorial 4 project alongside `pyproject.toml`,
add `ruff` and `mypy` as dev dependencies, push to GitLab.

```bash
uv add --dev ruff mypy
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run mypy src/
uv run pytest tests/ --cov=src --cov-branch --cov-report=term-missing -q
```
