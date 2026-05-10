## 5.5 Code Quality Analysis

### 5.5.1 Linting and Formatting with Ruff

Ruff ([Astral, 2023](https://docs.astral.sh/ruff/)) is a fast Python linter and formatter written in Rust. It enforces style rules and catches common programming errors:

```bash
ruff check src/       # lint
ruff format src/      # format (replaces black)
```

Ruff subsumes the functionality of flake8, isort, and black, and runs 10–100× faster than any of them individually. A typical configuration in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP"]   # pycodestyle, pyflakes, isort, naming, pyupgrade
ignore = ["E501"]                       # handled by formatter
```

Running `ruff check --fix src/` applies safe auto-fixes — removing unused imports, reordering them, upgrading deprecated syntax — without changing behaviour.

### 5.5.2 Type Checking with mypy

Type annotations in Python (since PEP 484, [van Rossum et al., 2015](https://peps.python.org/pep-0484/)) enable static analysis. mypy verifies that annotations are consistent throughout the codebase, catching a class of bugs that tests can miss:

```bash
mypy src/ --strict
```

Common errors mypy catches:
- Passing `None` where a non-optional value is expected
- Calling a method that does not exist on a type
- Returning the wrong type from a function
- Missing return statements in non-`None` functions

Example: the following code passes all unit tests but fails mypy because `divide` can return `None` yet the caller treats the result as `float`:

```python
def divide(a: float, b: float) -> float:
    if b == 0:
        return None        # mypy: error: Incompatible return value type
    return a / b

result: float = divide(10, 0)
print(result + 1)          # AttributeError at runtime
```

Fixing the annotation to `Optional[float]` forces every caller to handle the `None` case explicitly, eliminating the runtime error before deployment.

> **Box: Incremental adoption of mypy**
>
> Adding `--strict` to an existing codebase typically produces hundreds of errors. A practical adoption path is incremental: start with `mypy src/ --ignore-missing-imports` and fix errors module by module, adding `# type: ignore` sparingly for cases that require deeper refactoring. Once the baseline is clean, tighten the flags progressively toward `--strict`.

---
