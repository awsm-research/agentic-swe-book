# Chapter 10: Software Maintenance and Technical Debts

> *"Shipping first-time code is like going into debt. A little debt speeds development so long as it is paid back promptly with a rewrite. The danger occurs when the debt is not repaid."*
> — Ward Cunningham, OOPSLA 1992

---

On 1 August 2012, the high-frequency trading firm Knight Capital deployed new software to its order-routing system. The deployment was manual. One of eight servers did not receive the new code, and an old feature flag — repurposed for the new release — was reactivated on that server, waking up an eight-year-old block of dead code that had never been removed. Over the next forty-five minutes, the dormant code executed roughly four million erroneous trades across 154 stocks. By the time the firm halted trading, it had lost USD 440 million — more than its market capitalisation at the time ([SEC, 2013](https://www.sec.gov/litigation/admin/2013/34-70694.pdf)). Knight Capital was acquired the following year and ceased to exist as an independent company. The bug was not in the new code. It was in the code that should have been deleted years earlier — and in the deployment process that allowed half a release to ship to production.

---

## Learning Objectives

By the end of this chapter, you will be able to:

1. Distinguish the four classes of software maintenance and explain why preventive maintenance is consistently underfunded.
2. Apply Fowler's debt quadrant to classify technical debt and identify the categories most likely to arise from AI-generated code.
3. Identify the major types of technical debt — code, design, architecture, test, dependency, infrastructure, security, and documentation — and choose a detection method for each.
4. Compare repayment strategies (Boy Scout rule, opportunistic refactor, debt budget, strangler fig, branch by abstraction, parallel change) and select an appropriate one for a given debt shape.
5. Use AI assistants safely for refactoring legacy code, including the use of characterisation tests as a regression safety net.
6. Conduct a structured debugging investigation using reproduction, bisection, and observability — and write a blameless postmortem.

---

## 10.1 Why Maintenance Dominates the Software Lifecycle

Software engineering textbooks devote most of their pages to building new systems. Industry spends most of its money keeping old ones running. Empirical studies dating back to Lientz and Swanson's 1980 survey put post-deployment maintenance at 60–80% of total software cost over a system's lifetime ([Lientz & Swanson, 1980](https://dl.acm.org/doi/book/10.5555/539249)). Sommerville's 2016 textbook puts the figure at the high end of that range. The numbers have not improved in forty years — they have got worse, because systems live longer and integrate with more dependencies than they used to.

The British computer scientist Manny Lehman articulated why maintenance is unavoidable in his 1980 *Laws of Software Evolution* ([Lehman, 1980](https://ieeexplore.ieee.org/document/1456074)). Three of the laws matter for our purposes:

- **Continuing change** — a system used in the real world must be continually adapted, or it becomes progressively less useful.
- **Increasing complexity** — as a system evolves, its complexity rises unless explicit work is done to reduce it.
- **Declining quality** — the perceived quality of a system declines unless it is rigorously maintained and adapted to a changing environment.

Lehman's laws have a quiet implication: doing nothing is not stable. A codebase left alone gets worse, because the world around it keeps moving. Operating systems upgrade. Browsers deprecate APIs. Dependencies publish breaking changes. Regulators introduce new compliance requirements. Code that was correct in 2018 may be insecure, slow, or non-compliant in 2026 — without anyone editing a single line.

### The AI Inversion

For most of the field's history, the ratio of writing to reading code was roughly 1:10 — engineers spent ten times longer reading existing code than writing new code. Coding agents have inverted the writing speed, but they have done nothing to change the reading and reviewing burden. If an agent can produce a thousand lines of code in five minutes, the question is no longer "can we build it?" but "can we maintain it?". Every line generated becomes a future obligation. Knight Capital's USD 440 million loss came from forgetting to delete eight-year-old code; agentic systems can produce that volume of forgotten code in an afternoon.

---

## 10.2 The Four Types of Maintenance

The ISO/IEC 14764 standard divides maintenance into four categories based on what triggers the work ([ISO/IEC, 2006](https://www.iso.org/standard/39064.html)). The taxonomy is forty years old and still useful — most teams are unbalanced across these categories, and naming them helps to see the imbalance.

| Type | Trigger | Example |
|---|---|---|
| **Corrective** | A defect was found in production | Hotfix a NullPointerException reported by a user |
| **Adaptive** | The environment changed | Migrate from Python 3.9 to 3.13 |
| **Perfective** | The code works, but should be better | Refactor a 600-line class into smaller units |
| **Preventive** | Reduce the likelihood of future defects | Add tests to a fragile module before touching it |

Corrective maintenance dominates most teams' attention because it is the loudest — bugs get reported, paged, escalated. Preventive maintenance is the quietest, because nothing visible happens when you do it well. The result is predictable: teams underinvest in prevention, defects accumulate, and corrective work crowds out everything else. The pattern is the maintenance equivalent of running a hospital that only has an emergency department.

The economic argument for preventive maintenance is well-established. Barry Boehm's 1981 *Software Engineering Economics* established the now-canonical 1:5:10:50 cost progression — defects fixed in design cost roughly one unit; the same defect in production costs fifty ([Boehm, 1981](https://dl.acm.org/doi/book/10.5555/539302)). Capers Jones' later work extended this with broader industry data confirming a 30–100× factor between design-time and production-time fixes ([Jones, 2013](https://www.springer.com/gp/book/9781441973269)). The Knight Capital incident is at the extreme end of this curve — eight years of deferred dead-code removal cost the firm its existence.

---

## 10.3 What Technical Debt Actually Means

The term *technical debt* was coined by Ward Cunningham in 1992 to explain to non-technical stakeholders why the software team needed to refactor before adding features ([Cunningham, 1992](http://wiki.c2.com/?WardExplainsDebtMetaphor)). His original framing was specific. Shipping code that did not yet reflect the team's full understanding of the problem was acceptable — even desirable, if it accelerated learning — *provided the team came back and refactored once the understanding had matured*. The debt was the gap between what the code expressed and what the team knew. The interest was the friction that gap caused on every subsequent change.

The metaphor has been corrupted in common usage. *Technical debt* is now used as a synonym for *code I do not like*, *legacy*, or *anything that should be rewritten*. The corrupted version is rhetorically convenient but analytically useless — if every imperfection is debt, the term carries no information.

### Fowler's Debt Quadrant

In 2009, Martin Fowler refined the metaphor with a four-quadrant classification ([Fowler, 2009](https://martinfowler.com/bliki/TechnicalDebtQuadrant.html)):

|  | Deliberate | Inadvertent |
|---|---|---|
| **Prudent** | "We must ship now and deal with the consequences" | "Now we know how we should have done it" |
| **Reckless** | "We don't have time for design" | "What's layering?" |

The quadrant is not symmetric. *Deliberate prudent* debt is rational engineering — a team chooses to ship a known compromise to meet a deadline, and tracks it for repayment. *Inadvertent prudent* debt is the inevitable cost of learning — you only see the right design after you have built the wrong one. Both are normal.

The dangerous quadrants are the reckless ones. *Deliberate reckless* debt — "we don't have time for design" — is a management failure. *Inadvertent reckless* debt — "what's layering?" — is a competence failure. The latter is where AI-generated code lands by default: an agent does not know your project's layering rules unless you have specified them in context, and the code it produces will violate boundaries it does not know exist. A reviewer who waves the code through inherits the debt without realising it has been incurred.

---

## 10.4 A Taxonomy of Debt

Debt is not one thing. Different categories of debt have different detection methods, different costs, and different repayment strategies. The taxonomy below covers the categories that recur in production systems.

| Category | What it looks like | Why it costs |
|---|---|---|
| **Code debt** | Duplication, dead code, deep nesting, long methods | Every change becomes more expensive |
| **Design debt** | Wrong abstractions, leaky boundaries, god objects | New features fight the existing structure |
| **Architecture debt** | Distributed monolith, missing layers, circular service dependencies | Cannot scale or evolve subsystems independently |
| **Test debt** | Missing coverage, flaky tests, tautological assertions | Cannot refactor safely; bugs reach production |
| **Documentation debt** | Stale README, missing ADRs, undocumented invariants | Onboarding takes weeks; the same questions get re-answered |
| **Dependency debt** | Outdated, abandoned, vulnerable, or licence-incompatible packages | Security exposures; future upgrades become coordinated migrations |
| **Infrastructure debt** | Manual deploys, snowflake servers, missing IaC | Releases are risky; recovery from incidents is slow |
| **Security debt** | Known CVEs, missing auth checks, leaked secrets | A single exploit becomes a regulatory event |
| **Data debt** | Denormalised tables, missing constraints, dirty production data | Reports lie; migrations are dangerous |
| **Process debt** | Manual release steps, no rollback plan, undocumented runbooks | Every incident is novel; recovery time is unpredictable |

The categories interact. Test debt makes code debt unrepayable — you cannot refactor safely without tests. Infrastructure debt makes dependency debt unrepayable — you cannot upgrade safely without a reliable deploy and rollback path. The interaction is why teams that try to pay down one category at a time often fail: the prerequisites for repayment are themselves in debt.

### AI-Induced Debt

AI-generated code introduces a category that did not exist before agentic tools became commonplace. The patterns are distinct enough to warrant their own list:

- **Hallucinated APIs** — generated code calls functions that do not exist, or uses signatures from an older version of the library
- **Confidently wrong logic** — code that compiles, passes a happy-path test, and is silently incorrect on edge cases the agent did not consider
- **Over-abstraction** — agents reach for design patterns when a function would do
- **Copy-paste at scale** — agents replicate near-duplicates faster than humans can refactor them away
- **Stylistic drift** — every prompt produces slightly different conventions; the codebase becomes a fragmented archaeology of past sessions
- **Phantom dependencies** — agents add libraries the project does not need
- **Test theatre** — generated tests that mock the system under test and assert on the mocks

What makes AI-induced debt distinctive is its plausibility. Human carelessness leaves recognisable fingerprints: shortcuts, half-finished refactors, comments admitting the workaround. AI-induced debt looks like competent code written by someone who does not know your project. It passes review because it reads as confident. The Samsung incident from Chapter 12 — three engineers leaking proprietary code to an AI service in 2023 — is the visible version of this problem. The invisible version is the thousand pull requests that look fine and quietly erode the codebase.

---

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

## 10.6 Quantifying and Communicating Debt

The SQALE model, developed by Jean-Louis Letouzey in 2010 and adopted by SonarQube, expresses debt in *remediation hours* — the estimated time to repay each detected issue ([Letouzey, 2012](https://www.sqale.org/)). A *debt ratio* is then computed as remediation cost divided by estimated development cost. The numbers are not precise. They are useful for trend, not for absolute claims.

The persistent problem with debt quantification is that engineers and product managers speak different dialects. Telling a product manager that the codebase has 412 hours of technical debt does not motivate action. Telling them that the team's average cycle time has increased from 3.2 to 5.7 days over the last quarter, and that the top three hotspots account for 60% of post-merge defects, will. Translate debt into delivery delay, defect rate, and time-to-recover before bringing it to a stakeholder conversation.

The DORA metrics — deployment frequency, lead time for changes, change failure rate, and time to restore service ([Forsgren et al., 2018](https://itrevolution.com/product/accelerate/)) — are a useful complement to debt metrics. They measure the consequences of debt rather than debt itself, and they are the metrics product and engineering leaders already share.

---

## 10.7 Repayment Strategies

There is no universal repayment strategy because there is no universal debt shape. The table below summarises the major strategies, when each works, and when each fails.

| Strategy | When it works | When it fails |
|---|---|---|
| **Boy Scout Rule** — leave the file cleaner than you found it | Diffuse, low-grade debt across many files | Concentrated structural debt that no single change can address |
| **Opportunistic refactor** — fix when you are already in the file | Code that is being touched anyway | Code nobody touches — it rots in the dark |
| **Tech debt budget** — commit a fixed share of capacity (typically 20%) | Mature teams with backlog discipline and stakeholder trust | Teams whose product partners do not yet trust them to spend that capacity |
| **Dedicated debt sprint** | One large, localised piece of debt | Teams that pretend a one-time sprint will solve a continuous problem |
| **Strangler fig** — incremental rewrite of a legacy system around a façade | Legacy systems that still earn money and cannot be turned off | Greenfield projects where there is nothing to strangle |
| **Branch by abstraction** | Mid-flight migrations across many call sites | Small-scope changes that can be made directly |
| **Parallel change (expand–contract)** | API and schema changes with external consumers | Tightly-coupled internal code where dual-running is impractical |
| **Rewrite from scratch** | Almost never | Almost always |

The case against rewrites deserves a paragraph of its own. In 2000, Joel Spolsky published *Things You Should Never Do, Part I*, in which he argued that Netscape's decision to rewrite its browser from scratch was the single worst strategic mistake the company ever made — it gave Microsoft three years to ship Internet Explorer unopposed and effectively killed the company ([Spolsky, 2000](https://www.joelonsoftware.com/2000/04/06/things-you-should-never-do-part-i/)). The pattern has repeated since: rewrites consistently take longer than expected, ship with fewer features than the original, and reproduce the bugs that the original system had spent years patching. Michael Feathers' alternative — incrementally taming legacy code with tests and seams — is unglamorous and almost always correct.

### Choosing by Debt Shape

A simple decision procedure helps:

1. **Is the debt diffuse or concentrated?** Diffuse debt favours Boy Scout and opportunistic refactor. Concentrated debt needs dedicated effort.
2. **Is the affected code touched often?** Untouched code is not paying interest — leave it alone unless there is a specific reason (security, compliance, dependency upgrade).
3. **Is the debt structural or cosmetic?** Cosmetic debt (style, naming) yields to small refactors. Structural debt (architecture, schema) needs strangler fig or parallel change.
4. **Are there external consumers?** External consumers force expand–contract; internal-only changes can be more direct.

---

## 10.8 AI-Assisted Maintenance

Coding agents are unusually well-suited to maintenance work — and unusually dangerous when used without guardrails.

### Reading Legacy Code

The first useful agentic task on a legacy system is exposition, not modification. Asking an agent to summarise a module, draw the call graph, list the invariants, or trace a request through the system surfaces structure that the original authors never documented. The output is a draft, not a finding — every claim must be checked against the code — but the draft is faster to verify than the codebase is to read cold.

### Characterisation Tests Before Refactoring

Michael Feathers' *Working Effectively with Legacy Code* defines legacy code as code without tests ([Feathers, 2004](https://www.oreilly.com/library/view/working-effectively-with/0131177052/)). His core technique is the *characterisation test* — a test that pins down what the existing code currently does, without making any claim about what it should do. Once behaviour is pinned, the code can be refactored with a regression safety net.

This is exactly the workflow agents accelerate. A prompt of the form *"Generate characterisation tests for this module that exercise every public method with at least three input variants, asserting on the current return values"* produces a test suite in minutes that would take a careful human a day. The catch is that the tests must be reviewed — agents will sometimes assert on whatever the code happens to do today, including bugs. The tests pin the bug as well as the behaviour. Some of those tests need to fail, deliberately, before the refactor begins.

### Generating Refactor Variants

A productive pattern is to ask an agent for *three* refactor variants of the same function, optimising for different qualities — readability, performance, testability — and then evaluate them against the characterisation test suite. The variant that passes all the tests, reduces complexity, and reads cleanly wins. The other two are discarded. This is more disciplined than asking for *the* refactor, because it forces the reviewer to evaluate trade-offs explicitly.

### Migration Scripts and Bulk Chores

Agents do well at the unglamorous work that humans avoid: language version migrations, framework upgrades, type-annotation backfill, docstring generation, bulk renaming. The risk is uniform — agents replicate small mistakes consistently — so the verification strategy must be uniform too: run the test suite after every batch, not at the end.

### The Anti-Pattern

The most damaging way to use an agent in maintenance is to ask it to *clean up* a module without a regression safety net. The agent will produce code that looks better, passes the type-checker, and silently changes behaviour. Without characterisation tests, the change reaches production. The bug is then attributed to the agent, but the failure was the workflow.

---

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

## 10.10 Working with Legacy Code

Feathers' definition is worth restating: *legacy code is code without tests*. Under this definition, code an agent produced last week with no tests is legacy code, regardless of its age. The techniques for working with legacy systems are therefore relevant to every team using AI assistants.

The key concept is the *seam* — a place where you can change behaviour without editing the code itself. A function that takes a database connection as a parameter has a seam at the parameter; you can pass a fake connection in tests. A function that constructs the connection internally does not have a seam, and must be refactored before it can be tested. Identifying seams is the first step in taming legacy code.

Feathers' *sprout method* and *wrap method* techniques add new functionality alongside legacy code without modifying it. New code is written cleanly, with tests; legacy code is left alone until it can be incrementally absorbed. The technique is the small-scale version of the strangler fig.

### Code Archaeology

When the original author is unavailable — and on a long-lived system, this is the norm rather than the exception — the commit history becomes the primary source. `git log --follow` traces a file's history across renames; `git blame` identifies the last author of each line; commit messages, when written carefully, preserve the *why* that the code itself does not record. Teams that write disposable commit messages ("WIP", "fix bug", "address review") are accumulating a kind of historical debt — they are deleting their own future investigative tools.

---

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

## 10.12 The Maintenance Maturity Model

The model below is descriptive, not prescriptive. It describes where teams are; it does not claim that every team should reach Level 5.

| Level | Behaviour |
|---|---|
| **L1 — Firefighting** | All maintenance is corrective; debt is invisible until it explodes |
| **L2 — Reactive** | Debt is acknowledged but only addressed when it blocks features |
| **L3 — Scheduled** | Recurring debt budget; dependencies updated on cadence |
| **L4 — Measured** | Hotspots identified; debt metrics tracked; trends watched |
| **L5 — Continuous renewal** | Debt repayment is part of every change; the codebase improves over time |

Most organisations sit between L1 and L2 — and ship anyway. The economic case for moving up the model is not abstract: at L1, every incident is a novel emergency; at L4, most incidents are recognised patterns with known runbooks. The cost difference compounds.

AI-assisted teams can move faster up the model than teams without agents, because the work that distinguishes higher levels — characterisation tests, migration scripts, hotspot investigation, ADR drafting — is exactly the work agents do well. The same tools that produce AI-induced debt can repay it, when directed.

---

## 10.13 Key Takeaways

1. **Maintenance is the majority of the work.** Sixty to eighty per cent of total software cost is incurred after deployment. Engineering practices that treat maintenance as an afterthought are budgeting against forty years of evidence.

2. **Lehman's first law is decisive.** A system used in the real world must change, or it loses value. Doing nothing is not a stable state — the world around the code keeps moving.

3. **Cunningham's debt metaphor is precise; the popular usage is not.** Debt is the gap between what the code expresses and what the team understands. Calling every imperfection *technical debt* drains the term of meaning.

4. **The dangerous quadrant is reckless and inadvertent.** This is exactly where AI-generated code lands by default, because the agent does not know the rules it is breaking. Reviewers who wave it through inherit the debt without realising.

5. **Different debts need different detectors.** SATD mining, cyclomatic complexity, churn × complexity hotspots, dependency audits, and mutation scores each surface a different category. Pick the detector that matches the debt you are trying to manage.

6. **Pin behaviour with characterisation tests before you refactor.** This is non-negotiable when an agent is doing the refactor. An agent's "clean-up" is a behaviour change unless tests prove otherwise.

7. **Choose repayment strategy by debt shape.** Boy Scout for diffuse, dedicated effort for concentrated, strangler fig for structural, parallel change for external APIs. Rewrites are almost always the wrong answer.

8. **Debugging is a scientific activity.** Reproduce, bisect, hypothesise, observe, conclude. Postmortems are blameless because punishing engineers teaches them to hide failures, not prevent them.

9. **Documentation debt has no compiler.** Code rots when tests fail; documentation rots silently. ADRs, runbooks, and "why" comments are how a team preserves the reasoning that the code itself cannot record.

---

## Review Questions

1. *Hotspot triage*: A churn × complexity report identifies one file as the top hotspot in a backend repository. The file has cyclomatic complexity 47, has been edited by twelve different engineers in the last six months, and has 14% test coverage. Walk through how you would decide whether to refactor it, ignore it, rewrite it, or strangle it — and what evidence you would gather before committing to a strategy.

2. *AI refactor with no safety net*: A junior engineer used an agent to "clean up" a 600-line revenue-reporting module. The pull request reduces cyclomatic complexity from 38 to 9, removes 200 lines, passes the existing test suite, and is open for review. What do you do before approving — and what change would you make to the team's process so that the next agent-driven refactor cannot land this way?

3. *Strangler fig argument*: A legacy payments service still processes 30% of company revenue. Two engineers have proposed rewriting it from scratch over a quarter "because the code is unmaintainable". Make the case for or against the rewrite, propose a strangler fig alternative, and identify the three pieces of work the team must complete before the strangler fig can begin.

4. *Reframing debt for a product manager*: A product manager rejects a debt-payoff sprint with "we don't have time for that — we have features to ship". Reframe the cost of the existing debt in terms the product manager is responsible for. Use specific metrics from this chapter, and identify the smallest piece of work that would produce the evidence you need.

5. *Knight Capital postmortem*: Re-read the Knight Capital incident in the chapter opening. Identify three categories of debt from Section 10.4 that contributed to the failure, and describe one preventive maintenance practice that could have addressed each. What process change — not technology change — would have most reduced the blast radius?

---

## Further Reading

- Cunningham, W. (1992). *The WyCash Portfolio Management System*. OOPSLA Experience Report. [c2.com](http://wiki.c2.com/?WardExplainsDebtMetaphor)
- Fowler, M. (2009). *TechnicalDebtQuadrant*. [martinfowler.com](https://martinfowler.com/bliki/TechnicalDebtQuadrant.html)
- Feathers, M. (2004). *Working Effectively with Legacy Code*. Prentice Hall.
- Tornhill, A. (2018). *Software Design X-Rays: Fix Technical Debt with Behavioral Code Analysis*. Pragmatic Bookshelf.
- Lehman, M. M. (1980). *Programs, life cycles, and laws of software evolution*. Proceedings of the IEEE, 68(9). [ieeexplore](https://ieeexplore.ieee.org/document/1456074)
- Spolsky, J. (2000). *Things You Should Never Do, Part I*. [joelonsoftware.com](https://www.joelonsoftware.com/2000/04/06/things-you-should-never-do-part-i/)
- Nygard, M. (2011). *Documenting Architecture Decisions*. [cognitect.com](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- Beyer, B., Jones, C., Petoff, J., & Murphy, N. R. (2016). *Site Reliability Engineering: How Google Runs Production Systems*. O'Reilly. [sre.google](https://sre.google/sre-book/postmortem-culture/)
- US Securities and Exchange Commission. (2013). *In the Matter of Knight Capital Americas LLC*. [SEC Order](https://www.sec.gov/litigation/admin/2013/34-70694.pdf)
