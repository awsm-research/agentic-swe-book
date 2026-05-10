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
