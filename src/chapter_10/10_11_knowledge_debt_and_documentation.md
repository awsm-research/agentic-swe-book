## 10.11 Knowledge Debt and Documentation

Code records what the system does. Documentation records why. The why decays faster than the what, because the what is enforced by the compiler and the tests, while the why exists only in human memory and prose.

### Architecture Decision Records

Michael Nygard's 2011 proposal for *Architecture Decision Records* (ADRs) is now widespread practice ([Nygard, 2011](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)). An ADR is a short markdown document — typically under a page — recording one architectural decision: the context, the alternatives considered, the decision made, and the consequences accepted. ADRs live in the repository alongside the code, are versioned with the code, and are reviewed in pull requests.

```
# ADR-0014: Use SQLite for Local Development Cache

## Status
Accepted, 2026-03-14

## Context
The CLI needs a local cache for command outputs. Options considered:
- SQLite (chosen)
- A flat JSON file
- Redis

## Decision
SQLite. It ships with Python, requires no separate process, and gives us
indexed lookups for free.

## Consequences
- No new infrastructure dependency
- Concurrent writes are limited (acceptable for our usage)
- Cache files are not human-readable (we accept this)
```

The format is unglamorous on purpose. The discipline is showing up to write it.

### Comments: Why, Not What

Code-level documentation has one rule: explain *why*, not *what*. A comment that paraphrases the code below it is noise — the code is its own description. A comment that captures a non-obvious constraint, a hidden invariant, or the reason for a workaround is information that cannot be recovered from the code itself. The first kind rots; the second kind earns its keep.

### Runbooks

A *runbook* is the documentation that prevents 3am pages. It records the failure modes a system has encountered, how to diagnose each, and how to recover. Runbooks are read under stress, by someone who did not write the system, with limited time. They should be written for that reader. The act of writing a runbook is itself preventive maintenance — the questions you cannot answer while writing become the next batch of work to do.

---
