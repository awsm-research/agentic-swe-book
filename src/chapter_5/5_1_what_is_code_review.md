## 5.1 What Is Code Review?

Code review is the practice of having one or more developers read and evaluate a change to the codebase before it is merged. Its primary goals are defect detection, knowledge sharing, and enforcing standards — and it is among the most effective quality practices known in software engineering ([Fagan, 1976](https://ieeexplore.ieee.org/document/5388086); [Rigby & Bird, 2013](https://dl.acm.org/doi/10.1145/2491411.2491444)).

### 5.1.1 Fagan Inspection

The formal origin of code review is the *Fagan inspection*, introduced by Michael Fagan at IBM in 1976. A Fagan inspection is a structured, meeting-based process with defined roles:

- **Author**: the developer who wrote the code
- **Moderator**: facilitates the meeting and keeps it on track
- **Reader**: reads the code aloud, paraphrasing to expose gaps in understanding
- **Reviewers**: evaluate the code against a checklist and raise defects

Fagan found that inspections caught 60–90% of defects before testing — a rate that testing alone rarely matches. The key insight was that a *structured* process with defined roles and an explicit checklist performs better than ad-hoc reading.

### 5.1.2 Code Review Checklist

Modern teams rarely run formal Fagan inspections, but the checklist principle survives. A reviewer should systematically ask:

| Category | Questions |
|---|---|
| **Correctness** | Does the code do what the description claims? Are edge cases handled? |
| **Tests** | Are there sufficient tests? Do they cover the happy path and failure cases? |
| **Design** | Does the change fit the existing architecture? Does it introduce unnecessary coupling? |
| **Readability** | Can you understand the code without asking the author? Are names clear? |
| **Security** | Does the change introduce injection risks, broken auth, or unsafe defaults? |
| **Performance** | Are there N+1 queries, unbounded loops, or unnecessary allocations? |
| **Error handling** | Are errors caught and surfaced appropriately? Are resources released on failure? |
| **Documentation** | Are public interfaces documented? Do comments explain *why*, not *what*? |

Reviewers are not responsible for finding every bug — that is what tests are for. The goal is a second pair of eyes that catches what the author's familiarity with their own code conceals.

---
