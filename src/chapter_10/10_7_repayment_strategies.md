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
