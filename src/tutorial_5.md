# Tutorial 5: Code Quality and CI/CD

This tutorial builds directly on the tax deduction calculator from Tutorial 4. You will run static analysis, linting, and type-checking tools against the existing codebase on your local machine, then wire those same checks into a GitLab CI pipeline so every push is automatically validated.

**Concepts covered:** linting, auto-formatting, static type checking, CI/CD pipelines, GitLab CI

**Format:** Individual or pairs | **Duration:** ~1.5 hours | **Tool:** Python, ruff, mypy, GitLab CI

---

## Outline

- [Starting Point](#starting-point)
- [Part A: Running Code Quality Tools Locally](#part-a-running-code-quality-tools-locally-40-min)
- [Part B: Setting Up a GitLab CI Pipeline](#part-b-setting-up-a-gitlab-ci-pipeline-30-min)
- [Part C: Breaking and Fixing the Pipeline](#part-c-breaking-and-fixing-the-pipeline-20-min)
- [References](#references)

---

## Learning Objectives

By the end of this tutorial, you will be able to:

1. Run `ruff` to detect and auto-fix linting and formatting violations in a Python codebase.
2. Run `mypy` to verify that type annotations are consistent across a module.
3. Write a `.gitlab-ci.yml` file that runs lint, type-check, and test jobs on every push.
4. Interpret CI pipeline results and trace a failure back to the job and line that caused it.

---

## Starting Point

This tutorial builds on the tax deduction calculator and test suite from Tutorial 4. Before continuing, confirm your project contains these files:

```
my_project/
├── src/
│   └── tax.py          # production code from Tutorial 4
├── tests/
│   └── test_tax.py     # test suite with 100% branch coverage from Tutorial 4
├── pyproject.toml
└── uv.lock
```

If either `tax.py` or `test_tax.py` is missing, return to Tutorial 4 and complete it first. `uv.lock` must also be committed — it locks every dependency to an exact version so CI can reproduce your environment faithfully.

---

## Part A: Running Code Quality Tools Locally *(~40 min)*

Code review catches logic problems; code quality tools catch everything else — unused imports, inconsistent formatting, missing or incorrect type annotations. Running them locally before pushing means CI is confirming what you already know, not surprising you.

### Step 1: Install ruff and mypy

`ruff` is a fast Python linter and formatter that replaces `flake8`, `black`, and `isort` in a single tool. `mypy` is the standard Python static type checker.

```bash
uv add --dev ruff mypy
git add pyproject.toml uv.lock
git commit -m "chore: add ruff and mypy as dev dependencies"
```

---

### Step 2: Lint the Codebase with ruff

`ruff check` analyses source files for style and correctness violations without modifying anything.

```bash
uv run ruff check src/ tests/
```

**Activity:** Before running the command, scan `src/tax.py` and `tests/test_tax.py` from Tutorial 4. Predict whether ruff will flag any violations.

<details>
<summary>Expected output</summary>

```
All checks passed!
```

The Tutorial 4 code was written with PEP 8 compliance in mind. ruff finds no violations — this is the clean baseline the CI pipeline will protect.

</details>

---

### Step 3: Check Formatting with ruff

`ruff format --check` reports lines that the auto-formatter would change, without actually modifying the files. This is the mode used in CI pipelines: detection only, no silent rewrites.

```bash
uv run ruff format --check src/ tests/
```

<details>
<summary>Expected output</summary>

```
2 files already formatted
```

No formatting changes are needed. The existing code already matches ruff's style rules.

</details>

---

### Step 4: Type-check with mypy

`mypy` reads the type annotations in your source code and verifies they are internally consistent — a function annotated `-> float` that could silently return `None` would fail here.

```bash
uv run mypy src/
```

<details>
<summary>Expected output</summary>

```
Success: no issues found in 1 source file
```

`calculate_deduction` has a complete signature: every parameter is annotated and the return type is `float`. mypy is satisfied.

</details>

---

### Step 5: Activity — Introduce and Fix a Linting Violation

The checks above all passed because Tutorial 4 code was deliberately clean. To understand what these tools actually catch, introduce a violation, observe the failure, and fix it.

**Task:** Open `src/tax.py` and add the following line immediately after the existing constants, before the function definition:

```python
import os  # unused import
```

Re-run ruff:

```bash
uv run ruff check src/
```

<details>
<summary>Expected output and fix</summary>

```
src/tax.py:5:1: F401 [*] `os` imported but unused
Found 1 error.
[*] 1 fixable with the `--fix` option.
```

The `F401` rule flags unused imports. The `[*]` marker means ruff can remove it automatically:

```bash
uv run ruff check src/ --fix
```

ruff deletes the `import os` line. Confirm the file is clean before moving on:

```bash
uv run ruff check src/
```

```
All checks passed!
```

</details>

---

### Step 6: Activity — Introduce and Fix a Type Violation

**Task:** In `src/tax.py`, change the return type annotation from `-> float` to `-> int`:

```python
def calculate_deduction(
    income: float,
    age: int,
    has_spouse: bool,
    disabled: bool,
) -> int:   # changed from float
```

Run mypy:

```bash
uv run mypy src/
```

<details>
<summary>Expected output and fix</summary>

```
src/tax.py:XX: error: Incompatible return value type (got "float", expected "int")  [return-value]
Found 1 error in 1 file (errors prevented inline types from being checked)
```

`deduction` is initialised as `0.0` and incremented by float literals (`700.0`, `300.0`, …), so its type is `float`. The annotation `-> int` contradicts this. Restore the correct annotation:

```python
) -> float:
```

Confirm mypy passes before continuing:

```bash
uv run mypy src/
```

```
Success: no issues found in 1 source file
```

</details>

---

## Part B: Setting Up a GitLab CI Pipeline *(~30 min)*

A CI pipeline runs the same checks you just ran locally — automatically, on every push, on a clean machine that has never seen your code before. The pipeline is declared in a single file: `.gitlab-ci.yml`.

### Step 1: Understand Pipeline Structure

A GitLab CI pipeline is made up of **stages** and **jobs**:

| Concept | Description |
|---------|-------------|
| **Stage** | A named phase of the pipeline (e.g., `lint`, `test`) |
| **Job** | A named set of shell commands that runs within a stage |
| **Pipeline** | The ordered execution of all stages |

Jobs within the same stage run in parallel. A stage is considered failed if any of its jobs fail, and later stages are skipped when an earlier stage fails.

```
push to GitLab
       │
       ▼
┌──────────────────────────────────────────────────────┐
│  Stage: lint                                         │
│  ┌─────────────────┐     ┌──────────────────────┐   │
│  │   ruff-check    │     │    ruff-format        │   │  ← parallel
│  └─────────────────┘     └──────────────────────┘   │
└──────────────────────────────────────────────────────┘
       │  (only if all lint jobs pass)
       ▼
┌──────────────────────────────────────────────────────┐
│  Stage: typecheck                                    │
│  ┌──────────────────────────────────────────────┐   │
│  │                    mypy                      │   │
│  └──────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
       │  (only if typecheck passes)
       ▼
┌──────────────────────────────────────────────────────┐
│  Stage: test                                         │
│  ┌──────────────────────────────────────────────┐   │
│  │         pytest with branch coverage          │   │
│  └──────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
```

---

### Step 2: Create `.gitlab-ci.yml`

Create the file in the root of your project (at the same level as `pyproject.toml`):

```yaml
# .gitlab-ci.yml
stages:
  - lint
  - typecheck
  - test

default:
  image: python:3.12-slim
  before_script:
    - pip install uv --quiet
    - uv sync --frozen

ruff-check:
  stage: lint
  script:
    - uv run ruff check src/ tests/

ruff-format:
  stage: lint
  script:
    - uv run ruff format --check src/ tests/

mypy:
  stage: typecheck
  script:
    - uv run mypy src/

pytest:
  stage: test
  script:
    - uv run pytest tests/ --cov=src --cov-branch --cov-report=term-missing -q
```

**Key decisions:**

| Line | Why |
|------|-----|
| `image: python:3.12-slim` | Every job starts from a clean Docker container — nothing from your local machine carries over |
| `pip install uv --quiet` | The base image ships with pip; uv is not pre-installed |
| `uv sync --frozen` | Installs exact versions from `uv.lock` without updating it — reproducible and fast |
| `ruff-check` and `ruff-format` in the same stage | They are independent and run in parallel, saving time |
| `typecheck` after `lint` | No point type-checking code that does not pass style rules |
| `test` last | Tests are the most expensive step; skip them if earlier checks fail |

> **Note for Monash students:** If you are using [git.infotech.monash.edu](https://git.infotech.monash.edu), confirm that your project has a GitLab Runner assigned (visible under **Settings > CI/CD > Runners**). The Docker executor is required for the `image:` keyword to work.

---

### Step 3: Commit and Push

```bash
git add .gitlab-ci.yml
git commit -m "ci: add GitLab CI pipeline with lint, typecheck, and test stages"
git push origin main
```

> **If `main` is protected** (as configured in Tutorial 1), push to a feature branch and open a merge request:
> ```bash
> git checkout -b ci/add-pipeline
> git push origin ci/add-pipeline
> ```
> Then open a merge request in GitLab. The pipeline runs automatically on the MR branch.

---

### Step 4: Activity — Observe the Pipeline

1. Open your project in GitLab.
2. Navigate to **Build > Pipelines**.
3. Find the pipeline triggered by your push. Click its status badge to open the pipeline graph.
4. Click any individual job to read its terminal log.

**Answer these questions before revealing the expected state:**

1. Which two jobs run in parallel?
2. What is the status of the `test` stage while `lint` is still running?
3. Where in the GitLab UI can you see the coverage percentage from the `pytest` job?

<details>
<summary>Expected pipeline state and answers</summary>

All four jobs should pass and the pipeline should show:

```
Pipeline #xxx  ✔ passed

Stage: lint
  ruff-check    ✔ passed
  ruff-format   ✔ passed

Stage: typecheck
  mypy          ✔ passed

Stage: test
  pytest        ✔ passed
```

The `pytest` job log should end with:

```
Name         Stmts   Miss Branch BrPart  Cover   Missing
---------------------------------------------------------
src/tax.py      12      0      12      0   100%
---------------------------------------------------------
TOTAL           12      0      12      0   100%

8 passed in 0.XXs
```

**Answers:**

1. `ruff-check` and `ruff-format` run in parallel — they share the `lint` stage.
2. The `test` stage is **pending** (waiting) until the `lint` stage completes. GitLab will not start a later stage until all jobs in the previous stage have passed.
3. Click the `pytest` job → the coverage table appears at the bottom of the job log. GitLab can also be configured to parse coverage from the log and display it on the merge request — see **Settings > CI/CD > General pipelines > Test coverage parsing**.

</details>

---

## Part C: Breaking and Fixing the Pipeline *(~20 min)*

A passing pipeline is only useful if it can also fail. This part deliberately breaks the pipeline, reads the failure output, and restores it to green.

### Step 1: Introduce a Deliberate Linting Violation

Add an unused import to `src/tax.py`:

```python
# src/tax.py — add after the existing imports, before the constants
import sys  # unused
```

Commit and push:

```bash
git add src/tax.py
git commit -m "test: introduce unused import to observe CI failure"
git push origin main    # or your feature branch
```

---

### Step 2: Activity — Observe and Diagnose the Failure

Navigate to **Build > Pipelines** and open the new pipeline.

**Predict before looking:**
- Which specific job will fail?
- Which jobs will be skipped as a result?
- Will `ruff-format` also fail?

<details>
<summary>Expected pipeline state and explanation</summary>

```
Pipeline #xxx  ✖ failed

Stage: lint
  ruff-check    ✖ failed
  ruff-format   ✔ passed

Stage: typecheck
  mypy          ⊘ skipped

Stage: test
  pytest        ⊘ skipped
```

Click **ruff-check** to view the job log:

```
$ uv run ruff check src/ tests/
src/tax.py:5:1: F401 [*] `sys` imported but unused
Found 1 error.
ERROR: Job failed: exit code 1
```

**Why `ruff-format` still passes:** formatting style is unaffected by an unused import — the line `import sys` is syntactically valid and correctly formatted. The two jobs within `lint` run independently and in parallel; each reports its own result.

**Why `typecheck` and `test` are skipped:** when the `lint` stage fails (because `ruff-check` exited with a non-zero code), GitLab marks the stage as failed and does not start subsequent stages. There is no point type-checking or testing code that does not meet style requirements.

</details>

---

### Step 3: Activity — Fix and Restore Green

Remove the `import sys` line from `src/tax.py`, commit, and push:

```bash
git add src/tax.py
git commit -m "fix: remove unused sys import"
git push origin main    # or your feature branch
```

Wait for the new pipeline to complete. All four jobs should return to green before you consider this tutorial done.

---

## Summary: Local vs. CI Checks

The same four commands you ran in Part A map directly to the four CI jobs:

| Check | Local command | CI job |
|-------|--------------|--------|
| Linting | `uv run ruff check src/ tests/` | `ruff-check` |
| Formatting | `uv run ruff format --check src/ tests/` | `ruff-format` |
| Type checking | `uv run mypy src/` | `mypy` |
| Tests + coverage | `uv run pytest tests/ --cov=src --cov-branch --cov-report=term-missing -q` | `pytest` |

Running the local commands before every `git push` means CI is confirming what you already know — not surfacing problems you could have caught in seconds on your own machine.

---

## References

- [ruff Documentation](https://docs.astral.sh/ruff/) — Linting rules, formatting configuration, and editor integrations
- [mypy Documentation](https://mypy.readthedocs.io/) — Type checking, common error codes, and `pyproject.toml` configuration
- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/) — Full `.gitlab-ci.yml` reference, runners, and pipeline configuration
- [GitLab Predefined CI/CD Variables](https://docs.gitlab.com/ee/ci/variables/predefined_variables.html) — Variables available in every CI job (e.g., `$CI_COMMIT_SHA`, `$CI_PIPELINE_ID`)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/) — Coverage reporting options and CI integration
