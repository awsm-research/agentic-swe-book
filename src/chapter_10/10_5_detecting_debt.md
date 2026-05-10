## 10.5 Detecting Debt

You cannot manage what you do not measure. Each category of debt has detection tools that are mature, free, and ignored.

### Self-Admitted Technical Debt

The cheapest debt detector is `grep`. Authors who know they are writing debt mark it — `TODO`, `FIXME`, `HACK`, `XXX`. The empirical literature on *self-admitted technical debt* (SATD) is consistent: most TODOs are never repaid, and the median lifetime of a FIXME comment is measured in years ([Potdar & Shihab, 2014](https://users.encs.concordia.ca/~eshihab/pubs/Potdar_ICSME2014.pdf)). The fact that authors admitted the debt is exactly what makes SATD valuable to track — it represents the part of the debt landscape that is already labelled.

```bash
# Mine the repository for self-admitted debt
rg -n '(TODO|FIXME|HACK|XXX)\b' --type py
```

A simple metric — *SATD count per thousand lines of code*, tracked over time — is one of the easiest debt indicators a team can adopt.

### Code-Level Metrics

Cyclomatic complexity, originally proposed by Thomas McCabe in 1976 ([McCabe, 1976](https://ieeexplore.ieee.org/document/1702388)), counts the number of linearly independent paths through a function. It correlates roughly with both bug density and the cognitive cost of understanding a function. A method with cyclomatic complexity above 15 is a refactoring candidate; above 30 it is a hazard.

| Tool | Language | Measures |
|---|---|---|
| `radon`, `lizard` | Python, multi-language | Cyclomatic complexity, maintainability index |
| `vulture` | Python | Unused functions, classes, imports |
| `ts-prune`, `knip` | TypeScript | Dead exports |
| `jscpd`, `pmd-cpd` | Multi-language | Duplicate code blocks |
| `ruff`, `pylint` | Python | Style, smells, simple bugs |
| SonarQube, CodeScene | Multi-language | Hosted dashboards combining all of the above |

### Hotspot Analysis

Adam Tornhill's *churn × complexity* analysis is the single most actionable debt detector ([Tornhill, 2018](https://pragprog.com/titles/atevol/software-design-x-rays/)). The argument is simple: complex code that nobody touches is not costing you anything; complex code that changes weekly is where every defect accumulates. Multiplying file-level complexity by the count of recent changes produces a heat map of the files where debt is actively burning capacity.

```bash
# Approximate hotspot detection from git
git log --since="6 months ago" --name-only --pretty=format: \
  | sort | uniq -c | sort -rn | head -20
```

The output is the list of files most worth investigating with `radon` or `lizard`. Tools like `code-maat` and CodeScene formalise the analysis and produce visualisations.

### Dependency, Security, and Test Debt

Dependency debt is detected by automated auditors:

| Tool | Ecosystem |
|---|---|
| `pip-audit`, `safety` | Python |
| `npm audit`, `pnpm audit` | JavaScript |
| `cargo audit` | Rust |
| Dependabot, Renovate | Hosted, multi-ecosystem |

Security debt is detected by SAST tools (Bandit, Semgrep, CodeQL — covered in Chapter 8) and secret scanners (GitLeaks, TruffleHog).

Test debt requires a more careful instrument. Coverage is necessary but not sufficient — a test suite with 95% line coverage and no meaningful assertions is debt dressed as quality. *Mutation testing* introduces small modifications to the production code and verifies that at least one test fails for each mutation. A high mutation score is much harder to fake than a high coverage number.

```bash
# Mutation testing for Python
uv add --dev mutmut
uv run mutmut run --paths-to-mutate=src/
uv run mutmut results
```

Mutation testing is computationally expensive and slow. The pragmatic approach is to run it on hotspots, not the whole codebase.

---
