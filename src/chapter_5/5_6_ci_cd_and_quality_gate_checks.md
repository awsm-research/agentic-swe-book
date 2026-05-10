## 5.6 CI/CD and Quality Gate Checks

Continuous integration (CI) is the practice of merging all developer branches into the main branch frequently — at least daily — with each merge triggering an automated build and test run ([Fowler, 2006](https://martinfowler.com/articles/continuousIntegration.html)). Continuous delivery (CD) extends CI to ensure the software is always in a deployable state.

A *quality gate* is a CI step that fails the pipeline if a quality threshold is not met — coverage below 80%, any linting error, any type error, any medium-severity security finding. Quality gates convert code quality from a guideline into an enforced constraint.

### 5.6.1 GitLab CI Configuration

GitLab CI is configured through a `.gitlab-ci.yml` file at the repository root. Pipelines are composed of *jobs* grouped into *stages*; jobs within a stage run in parallel, and stages run sequentially.

```yaml
# .gitlab-ci.yml
image: python:3.11-slim

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip

stages:
  - lint
  - test
  - security

before_script:
  - pip install -r requirements.txt
```

The `before_script` block runs before every job, installing dependencies. The `cache` block persists the pip download cache across pipeline runs, reducing install time.

### 5.6.2 Multi-Stage Pipeline

Splitting the pipeline into stages makes failures fast and legible: a lint failure in stage 1 blocks the expensive test stage from running, giving the author immediate feedback at minimum cost.

```yaml
# Stage 1: lint
ruff:
  stage: lint
  script:
    - ruff check src/ tests/
    - ruff format --check src/ tests/

mypy:
  stage: lint
  script:
    - mypy src/ --strict

# Stage 2: test
unit-tests:
  stage: test
  script:
    - pytest tests/unit/ --cov=src --cov-report=xml --cov-fail-under=80
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

integration-tests:
  stage: test
  script:
    - pytest tests/integration/ -v
  allow_failure: false

```

**Key configuration details:**

- `coverage:` is a regex that extracts the coverage percentage from pytest output; GitLab displays it on the pipeline page and merge request
- `artifacts: reports: coverage_report:` uploads the Cobertura XML so GitLab renders inline coverage annotations on the diff
- `allow_failure: false` (the default) means a failing job fails the entire pipeline and blocks merge
- Jobs within a stage (`unit-tests` and `integration-tests`) run in parallel automatically
