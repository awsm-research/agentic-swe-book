# Tutorial 1: Setting Up Your Python Development Environment

This tutorial walks through setting up a Python development environment.

### Prerequisites

- Python 3.11 or later ([python.org](https://www.python.org/downloads/))
- Git ([git-scm.com](https://git-scm.com/))
- VS Code ([code.visualstudio.com](https://code.visualstudio.com/))
- A GitHub account ([github.com](https://github.com/))

### Step 1: Create a Virtual Environment

```bash
mkdir my_project
cd my_project

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

python --version                # Confirm activation
```

### Step 2: Initialise a Git Repository

```bash
git init
cat > .gitignore << 'EOF'
venv/
__pycache__/
*.pyc
.env
EOF
git add .gitignore
git commit -m "Initial commit: add .gitignore"
```

### Step 3: Install Core Development Tools

```bash
pip install pytest ruff mypy pre-commit
pip freeze > requirements.txt
```

### Step 4: Configure Ruff and Mypy

```toml
# pyproject.toml
[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]

[tool.mypy]
python_version = "3.11"
strict = true
```

### Step 5: Set Up Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

```bash
pre-commit install
```

### Step 6: Verify the Setup

```python
# src/calculator.py
import argparse


def add(a: float, b: float) -> float:
    return a + b


def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple calculator")
    parser.add_argument("operation", choices=["add", "divide"], help="Operation to perform")
    parser.add_argument("a", type=float, help="First number")
    parser.add_argument("b", type=float, help="Second number")
    args = parser.parse_args()

    if args.operation == "add":
        print(add(args.a, args.b))
    elif args.operation == "divide":
        print(divide(args.a, args.b))


if __name__ == "__main__":
    main()
```

Run it from the command line:

```bash
python src/calculator.py add 3 5       # Output: 8.0
python src/calculator.py divide 10 2   # Output: 5.0
python src/calculator.py divide 1 0    # Raises: ValueError
```

```python
# tests/test_calculator.py
import pytest
from src.calculator import add, divide

def test_add() -> None:
    assert add(2, 3) == 5
    assert add(-1, 1) == 0

def test_divide() -> None:
    assert divide(10, 2) == 5.0

def test_divide_by_zero() -> None:
    with pytest.raises(ValueError):
        divide(1, 0)
```

```bash
pytest tests/ -v
```

Expected output:
```
tests/test_calculator.py::test_add PASSED
tests/test_calculator.py::test_divide PASSED
tests/test_calculator.py::test_divide_by_zero PASSED
3 passed in 0.12s
```

This environment — version control, dependency isolation, linting, type checking, pre-commit hooks, and a test framework — is the foundation on which every subsequent chapter builds.

### Step 7: Make Your First Meaningful Commit

With a passing test suite, you are ready to make a proper commit. Good commit practice starts here.

**Stage only the files you intend to commit:**

```bash
git add src/calculator.py tests/test_calculator.py pyproject.toml .pre-commit-config.yaml requirements.txt
```

**Check what is staged before committing:**

```bash
git status
git diff --staged
```

**Write a descriptive commit message.** A good message has a short subject line (under 72 characters) and, when needed, a body explaining *why* — not just what:

```bash
git commit -m "Add calculator module with add and divide operations

- Implements add() and divide() with type hints
- divide() raises ValueError on division by zero
- CLI entry point via argparse
- Unit tests covering happy path and error cases"
```

**View your commit history:**

```bash
git log --oneline
```

Expected output:
```
a3f92c1 Add calculator module with add and divide operations
e1b4d07 Initial commit: add .gitignore
```

### Step 8: Understand What Not to Commit

Some files should never be committed. Your `.gitignore` already covers the most common cases, but it helps to understand why:

| File / Pattern | Why |
|---|---|
| `venv/` | Virtual environment — recreatable from `requirements.txt` |
| `__pycache__/`, `*.pyc` | Python bytecode — generated automatically |
| `.env` | API keys and secrets — never commit credentials |
| `*.egg-info/` | Package build artefacts |
| `.mypy_cache/`, `.ruff_cache/` | Tool caches — not part of the project |

**Verify nothing sensitive is staged:**

```bash
git status
git diff --staged --name-only
```

If you accidentally stage a secret, remove it before committing:

```bash
git restore --staged .env
```

### Step 9: Activity — Extend and Commit

Complete the following activity to practise the full edit-test-commit cycle:

1. Add a `multiply(a, b)` function to `src/calculator.py` and a `subtract(a, b)` function.
2. Add CLI support for both operations in `main()`.
3. Write at least two tests for each new function in `tests/test_calculator.py`.
4. Run the full check before committing:

```bash
ruff check src/ tests/
mypy src/
pytest tests/ -v
```

5. Stage and commit your changes with a meaningful message:

```bash
git add src/calculator.py tests/test_calculator.py
git commit -m "Add multiply and subtract operations to calculator"
```

6. Verify the commit appears in your log:

```bash
git log --oneline
```

A clean log with descriptive messages is part of professional software engineering practice — and it becomes especially important when collaborating with teammates or reviewing AI-generated changes.
