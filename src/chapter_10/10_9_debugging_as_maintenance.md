## 10.9 Debugging as Maintenance

Debugging is not separate from maintenance — it is the visible part of corrective maintenance, and the methodology applies to every other category. The disciplined approach is older than computing: observe, hypothesise, experiment, conclude. Brian Kernighan and Rob Pike made the argument explicit in *The Practice of Programming* — debugging is a scientific activity, and programmers who treat it as guessing are doing science badly ([Kernighan & Pike, 1999](https://www.cs.princeton.edu/~bwk/tpop.webpage/)).

### Reproduce First

A bug you cannot reproduce is not a bug you can fix. The first task in any debugging session is to find an input — a request, a sequence of actions, a fixture — that reliably triggers the failure. Reproduction is sometimes the entire job: a Heisenbug that vanishes when observed is usually a concurrency or timing issue, and finding the conditions under which it appears is harder than fixing it.

### Bisection

`git bisect` is binary search through history. Given a known good commit and a known bad commit, it walks through the intermediate commits in O(log n) steps until it identifies the first commit that introduced the failure.

```bash
git bisect start
git bisect bad HEAD
git bisect good v1.4.0
# git checks out a midpoint commit; you run your reproduction
git bisect good   # or 'git bisect bad'
# repeat until git reports the first bad commit
git bisect reset
```

For a repository with 1,024 commits between good and bad, bisection reaches the offending commit in about ten test runs. An agent can accelerate the process further: given the diff of a single commit and a description of the failure, it can usually identify the responsible line in seconds.

### Observability

A bug observed only in production cannot be debugged with a debugger. The investigation depends on the artefacts the system produced — logs, traces, metrics. Charity Majors' definition is useful: observability is the property of a system that lets you ask new questions about its behaviour without shipping new code ([Majors et al., 2022](https://www.oreilly.com/library/view/observability-engineering/9781492076438/)). A system without structured logs and distributed traces is a system you cannot debug; building observability into a service is preventive maintenance for the next outage.

### Postmortems

A blameless postmortem treats an incident as an output of the system, not the fault of an individual. The format Google popularised — timeline, impact, root cause, contributing factors, action items — is now standard ([Beyer et al., 2016](https://sre.google/sre-book/postmortem-culture/)). The discipline matters more than the format: a culture that punishes engineers for incidents teaches engineers to hide incidents, which is how the CBA case in Chapter 1 went undetected for three years.

---
