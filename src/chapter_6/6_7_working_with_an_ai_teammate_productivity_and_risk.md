## 6.7 Working with an AI Teammate: Productivity and Risk

Hoda (2025) argues that the field risks making a categorical error: treating agentic software engineering as an acceleration of *coding* when it is actually a transformation of *the entire software process* ([Hoda, 2025](https://arxiv.org/abs/2510.19692)). Teams that adopt AI agents to write code faster while leaving their requirements practices, design processes, review cultures, and testing disciplines unchanged are, in Hoda's framing, using a paradigm-shifting tool within a paradigm that has not shifted. The efficiency gains are real but bounded. The deeper opportunity — and the deeper risk — lies in what happens when AI agents are applied across the full socio-technical process, not just the coding step.

### Productivity Expectations

The 10x productivity claim — that AI coding agents can make a single engineer ten times as productive — circulates widely, and the evidence is mixed in instructive ways.

Studies consistently find productivity gains for *specific task types*: routine code generation, test scaffolding, documentation, boilerplate, and translation between languages. [GitHub's internal study (2023)](https://github.blog/2022-09-07-research-quantifying-github-copilots-impact-on-developer-productivity/) found Copilot users completed certain coding tasks 55% faster. McKinsey (2023) found mid-complexity tasks saw 20–45% time reductions. These are real and significant gains.

The 10x claim typically comes from productivity profiles that are heavily skewed toward tasks AI handles well. A developer whose work is 80% boilerplate and routine CRUD implementation may see near 10x on that work. A developer whose work is 80% novel domain logic, architectural decisions, and stakeholder negotiation will see modest gains.

AI coding agents make a developer dramatically more productive at the tasks AI handles well, while leaving the tasks that require judgment, domain knowledge, and interpersonal communication essentially unchanged. The proportion of work that falls into each category varies widely by role, seniority, and domain.

### Risks and Concerns

The productivity gains are real, but so are the incident reports. In 2025, reports of *agentic incidents* — cases where AI coding agents took destructive, irreversible actions — proliferated across developer communities. Engineers reported agents with broad shell access interpreting "clean up temporary files" as a mandate to delete untracked directories, wiping configuration that was not in version control. Others reported agents generating and executing database migration scripts against production instances after staging tests passed — dropping columns used by features not covered by the test suite. A widely circulated case involved an agent connected to an AWS environment that, acting on a refactoring task, deleted S3 buckets it identified as unused — with no backup, no confirmation step, and no rollback path. In each case the agent had done exactly what it understood its instructions to mean. The gap was between what the engineer intended and what the agent inferred, and there was no checkpoint in between.

Liu et al. (2023) document the baseline problem: 32.2% of ChatGPT-generated code samples produced incorrect outputs, and nearly half had maintainability issues detectable by standard static analysis ([Liu et al., 2023](https://arxiv.org/abs/2307.12596)). ChatGPT could self-repair some defects when shown the errors — but only when the engineer knew to ask. An engineer who accepted the output without verification shipped the failure.

**Overreliance and skill atrophy.** Perry et al. (2022) identified a mechanism beyond the immediate code errors: Copilot users relied on the tool as a substitute for understanding, rather than as an accelerator for it. Engineers who stop practising a skill because AI does it for them lose the judgment needed to verify AI's execution of that skill. Overreliance is not a hypothetical future risk — it is a documented present-day outcome ([Perry et al., 2022](https://arxiv.org/abs/2211.03622)).

**Responsibility and accountability.** When AI-generated code causes a production incident, the question of who is responsible is not legally ambiguous: the engineer who committed the code and the organisation that deployed it are responsible. AI systems are not legal persons. They cannot be held accountable. The accountability sits with the humans in the chain.

**Intellectual property and licences.** AI models are trained on publicly available code, much of it under open-source licences. When an agent generates code that closely resembles a licensed open-source function, questions arise about licence obligations. As of 2025, this remains an active area of litigation in multiple jurisdictions. Engineering teams working on proprietary products should understand their organisation's policy on AI-generated code and verify that generated output does not reproduce copyrighted material verbatim.

**Autonomy and the expanding blast radius.** As agents become more capable and are delegated more consequential tasks, the potential damage from a single bad agentic session increases. An agent that generates a wrong function is a minor problem. An agent that refactors a database schema incorrectly, generates a migration script, and runs it against a production database is a major incident. The appropriate response is not to avoid agentic tools — it is to match the agent's autonomy to the reversibility of its actions, a principle addressed in Section 6.8.

**Security attack surface.** Agents that are connected to external systems — issue trackers, CI pipelines, production APIs — can be manipulated through malicious content in those systems. *Prompt injection* attacks embed AI instructions in user-controlled content (a ticket title, a code comment, a test fixture) that the agent reads and executes as instructions. Chapter 9 covers this threat in detail; for now, the principle is: treat any content the agent reads from an external system as untrusted input, just as you would user-supplied data in a web application.

---
