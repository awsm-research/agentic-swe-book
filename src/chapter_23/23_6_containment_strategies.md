## 23.6 Containment Strategies

---

Knowing the failure modes is not enough. A production multi-agent system requires explicit containment mechanisms that limit the blast radius of failure and enable graceful degradation.

### Circuit Breakers

Borrowed from distributed systems engineering, a circuit breaker monitors the failure rate of an agent or downstream service. When failures exceed a threshold — say, three consecutive timeouts from the Research Agent — the circuit breaker opens: subsequent calls to that agent are immediately rejected with a failure signal rather than being allowed to time out. After a cooldown period, the circuit breaker allows a test request through; if it succeeds, the circuit closes and normal operation resumes.

Circuit breakers serve two purposes in a multi-agent context. First, they prevent a slow or failing agent from consuming the timeout budget of the agents waiting on it. Second, they provide a signal to the supervisor or orchestrator that a component is degraded, enabling it to route around the failure rather than waiting.

### Timeout Budgets Per Subtask

Every agent invocation must have an associated timeout — a maximum duration the system will wait for a result. But timeout budgets in multi-agent systems should be hierarchical. The overall workflow has a total time budget. Each subtask has its own subtask budget. The sum of subtask budgets must be less than the total budget, with a margin reserved for orchestration overhead and aggregation.

Setting timeout budgets requires empirical calibration. Observe the distribution of response times for each agent under normal operating conditions and set the timeout at a percentile that covers the vast majority of legitimate cases — typically the ninety-fifth or ninety-ninth percentile — rather than at the mean. A timeout set at the mean will trigger on half of all normal requests.

### Fallback Behaviour

When an agent fails, times out, or exceeds its error threshold, the system should have a defined fallback. Fallbacks take several forms:

- **Retry with modified parameters**: Retry the subtask with a simpler prompt, a shorter context, or a reduced scope.
- **Substitute agent**: Route the subtask to a different agent with overlapping capability but lower specialisation.
- **Graceful degradation**: Skip the optional subtask and mark the output as partial.
- **Human escalation**: Flag the task for human review when no automated fallback is sufficient.

The choice of fallback depends on the criticality of the subtask and the cost of delay. A clinical documentation system that cannot retrieve the patient's medication history should not fabricate one — it should escalate to a human reviewer. A research summarisation system that cannot access one of five databases should note the gap and proceed with the remaining four.

### Scope Restrictions on Agent Write Permissions

Not every agent in a system should be able to write to every store. A least-privilege model — in which each agent is granted write access only to the specific stores, fields, or records it legitimately needs to modify — contains the blast radius of a malfunctioning or compromised agent.

This is an engineering constraint that must be enforced at the infrastructure level, not just at the prompt level. An agent instructed not to modify the patient's demographic record can still do so if the infrastructure grants it write access. Scope restrictions implemented only through prompting are not containment; they are convention. Real containment requires that the agent cannot perform the action even if it attempts to.

Audit logging of all agent write operations — recording which agent wrote what, when, and based on what input — is the complementary requirement. Containment prevents unintended writes; audit logs enable post-hoc investigation when something goes wrong despite the containment.

---
