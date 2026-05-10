## 5.4 Automated Code Review Using Static Analysis

Automated code review tools analyse source code without executing it, systematically checking for a class of issues that manual review catches inconsistently. They are fast, cheap, and consistent — running in seconds on every commit with no reviewer fatigue.

Tools are most effective at:
- Enforcing style and formatting rules uniformly
- Catching type errors before runtime
- Identifying known security anti-patterns
- Flagging unused imports, dead code, and obvious bugs

They are least effective at:
- Understanding business context and domain logic
- Evaluating architectural decisions
- Catching subtle security vulnerabilities that require contextual reasoning
- Judging whether a change is the *right* change to make

The practical pattern is to run automated analysis as a *pre-filter* before human review: CI blocks the PR if automated checks fail, so reviewers can focus their attention on what tools cannot catch.

---
