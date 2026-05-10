## 5.3 Limitations of Manual Code Review

Code review is effective but not free. Understanding its costs helps teams apply it well rather than applying it uniformly.

**Time and cognitive load.** A careful review of 400 lines takes a skilled engineer 45–60 minutes. At scale, review becomes a significant fraction of total engineering time. Teams that treat review as a low-priority interrupt find that PRs sit unreviewed for days, blocking delivery.

**Inconsistency.** Human reviewers vary in thoroughness, focus, and knowledge. The same code reviewed by two different engineers will produce different feedback. Style and convention issues — the easiest mechanical problems to fix — consume disproportionate reviewer attention.

**Fatigue effects.** Research on inspection data finds that defect detection rate drops significantly after the first hour of review ([Capers Jones, 1991](https://dl.acm.org/doi/10.5555/573262)). Large PRs exploit this effect: reviewers find early defects carefully and then accelerate through the rest.

**Coverage gaps.** Manual review catches design and logic problems well but is unreliable for performance, security, and concurrency bugs, which require systematic analysis rather than reading. A reviewer who does not think to check for SQL injection will not find it.

Manual review should therefore focus on what humans do best — evaluating design decisions, business logic, and domain correctness — while mechanical checks are delegated to automated tools.

---
