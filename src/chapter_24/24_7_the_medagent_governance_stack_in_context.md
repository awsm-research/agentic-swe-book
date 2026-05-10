## 24.7 The MedAgent Governance Stack in Context

---

The three chapters that comprise the MedAgent case study — Chapters 22, 23, and 24 — demonstrate the AgentOps layer of the SE4AI stack applied to a clinical domain. The governance stack is best understood as a system, not as a list of features.

MedAgent is a system that combines multi-agent orchestration (Chapter 22), comprehensive observability (Chapter 23), and the safety and governance layer described in this chapter. The architecture is not the result of adding safety features on top of a capable agent — it is the result of designing the agent from the beginning with safety as an architectural constraint. The approval workflow is not a wrapper around an otherwise unconstrained agent; it is a first-class component of the execution graph whose presence is structurally non-negotiable. The audit log is not an afterthought; it is populated by every tool call, every approval request, every session event, because those records were designed to be captured from day one.

The governance stack answers four questions that a regulator, a clinical governance board, or a post-incident investigator will ask about any agent that acts in a clinical setting. What did the agent do? The session replay capability, grounded in the LangGraph checkpointer, answers this with complete fidelity. Why did it do it? The distributed trace, capturing every reasoning step and tool call in sequence, answers this. Who authorised it? The audit log, containing the approver identifier and timestamp for every irreversible action, answers this. Was it operating within its intended scope? The scope restriction, circuit breakers, and red team assessment together answer this.

A system that cannot answer these four questions is not production-ready for a regulated domain, regardless of its technical performance metrics. RAGAS scores and F1 scores do not tell a regulator or a court what the system did in a specific session. Governance artefacts do.

### 24.7.1 What Governance Cannot Solve

Governance engineering is necessary but not sufficient for responsible agentic AI deployment. It addresses accountability — the ability to reconstruct what happened and who authorised it. It does not address all the underlying sources of agent error.

An agent operating with a full governance stack — append-only audit logs, approval workflows, circuit breakers, scope restriction, and session replay — can still recommend the wrong action to a clinician who approves it without adequate review. The audit log will record that the action was approved; it will not reveal that the approval was reflexive rather than considered. Governance engineering makes the agent accountable; it does not make the human reviewer infallible.

Similarly, governance engineering does not solve the model alignment problem: the question of whether the agent's learned objectives are well-aligned with the intended task. An agent whose reward signal was subtly misspecified during training may consistently propose actions that are locally plausible but systematically biased in a direction that only becomes visible in aggregate. Detecting this kind of systematic error requires the distributional monitoring practices from the MLOps layer — analysing the population of the agent's proposals over time for patterns that individual session review cannot reveal.

The full SE4AI stack exists precisely because no single layer is sufficient. Governance catches what evaluation misses. Evaluation catches what training data engineering misses. Monitoring catches what initial evaluation misses. Each layer exists because the previous layers have known blind spots.

---
