# Labs — Runnable Code from the Book and Tutorials

Each folder contains the code blocks extracted from one chapter or tutorial,
trimmed to the artefacts that are runnable, reviewable, or load-bearing for
the activity. Pure prose snippets (4-line illustrations, single-line shell
hints) are not extracted here — they are easier to read inline in the
markdown source.

## Index

| Folder | Source | Summary |
|---|---|---|
| [`ch03_design/`](ch03_design/) | Chapter 3 | SOLID, GoF patterns (Singleton, Factory, Observer, Strategy, Repository), and clean-naming snippets |
| [`ch04_testing/`](ch04_testing/) | Chapter 4 | Calculator module + AAA-pattern unit tests with `assertRaises` and coverage commands |
| [`ch08_security/`](ch08_security/) | Chapter 8 | Vulnerable + safe pairs for SQL injection, command injection, path traversal, deserialisation, hardcoded credentials, and PII detection |
| [`ch09_agent_security/`](ch09_agent_security/) | Chapter 9 | Prompt-injection examples, trust-boundary wrappers, and subagent-config attack/defence cases |
| [`ch11_packaging/`](ch11_packaging/) | Chapter 11 | Standalone Dockerfile, Compose, and `.env` examples (illustrative digests) |
| [`ch12_ethics/`](ch12_ethics/) | Chapter 12 | Non-compliant DELETE endpoint and PII-guarded `safe_ai_request` |
| [`tut01_setup/`](tut01_setup/) | Tutorial 1 | uv-scaffolded Python project with calculator, pre-commit, and `.gitignore` |
| [`tut03_lms_design/`](tut03_lms_design/) | Tutorial 3 | Broken `TaskService`, pre-refactor `proc`, and sample UML diagrams |
| [`tut04_unit_testing/`](tut04_unit_testing/) | Tutorial 4 | Tax-deduction calculator + 8-test suite at 100% branch coverage |
| [`tut05_quality_cicd/`](tut05_quality_cicd/) | Tutorial 5 | `.gitlab-ci.yml` with lint → typecheck → test stages |
| [`tut06_spec_to_code/`](tut06_spec_to_code/) | Tutorial 6 | `assign_job` specification fed to the AI agent, sample Gherkin |
| [`tut07_well_tested/`](tut07_well_tested/) | Tutorial 7 | Sample-answer pytest suite for `AssignJobService` |
| [`tut08_sast/`](tut08_sast/) | Tutorial 8 | Vulnerable Flask app + triage-worksheet runbook |
| [`tut09_security_cicd/`](tut09_security_cicd/) | Tutorial 9 | `example_vulnerable.py`, `security_review.py` aggregator, custom Semgrep rule, GitHub + GitLab pipelines |
| [`tut10_refactor/`](tut10_refactor/) | Tutorial 10 | Four staged versions of `shipping.py` (initial → guard → lookup → extract) plus the test contract |
| [`tut11_compose/`](tut11_compose/) | Tutorial 11 | Full bookshop stack: FastAPI + nginx + Postgres with health checks, secrets, digest pinning |
| [`tut12_responsible_ai/`](tut12_responsible_ai/) | Tutorial 12 | Presidio PII guards, GDPR endpoint specification, licence-audit CI pipelines |

## Conventions

- Files use the exact filenames the book gives (`src/calculator.py`,
  `tests/test_tax.py`, `compose.yaml`, etc.) so the commands in the chapter
  text run unmodified.
- Image digests in `Dockerfile` and `compose.yaml` are the illustrative values
  shown in the book. Substitute real digests via `docker pull` and
  `docker inspect` before building.
- Snippets that reference symbols intentionally undefined in the book (`db`,
  `app`, `smtp`, `psycopg2.connect`) are preserved verbatim — they are
  pedagogical illustrations, not standalone executables.
