# Tutorial 1 — Python + GitLab Setup

Final state of the Python project scaffolded in Tutorial 1 Steps 1–5.

## Files

| File | Purpose |
|---|---|
| `pyproject.toml` | Initial uv-generated project metadata |
| `.gitignore` | Excludes `.venv/`, caches, and `.env` |
| `.pre-commit-config.yaml` | Pre-commit hooks: whitespace, EOF, YAML, large-files |
| `src/calculator.py` | `add`/`divide` calculator with argparse CLI |

## How to run

```bash
uv venv
source .venv/bin/activate
uv add --dev pre-commit
uv run pre-commit install

python src/calculator.py add 3 5       # 8.0
python src/calculator.py divide 10 2   # 5.0
```
