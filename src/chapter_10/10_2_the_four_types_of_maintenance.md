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
