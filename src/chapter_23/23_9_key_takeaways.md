## 23.9 Key Takeaways

---

1. **Single agents fail at scale for structural reasons.** Context window limits, specialisation gaps, and sequential bottlenecks are not temporary technical limitations — they are inherent properties of single-agent architectures that multi-agent systems address through decomposition and parallelism.

2. **Orchestration pattern choice is an architectural decision.** Supervisor/worker suits decomposable tasks with clear specialist domains. Pipeline suits fixed transformation sequences. Peer-to-peer suits open-ended negotiation. Blackboard suits distributed knowledge contribution. Each has a specific failure mode that must be engineered against, and no pattern is universally superior.

3. **Shared state and message passing present a fundamental tradeoff.** Shared state is intuitive but requires explicit concurrency control to prevent silent corruption. Message passing is safer under concurrency but introduces overhead and requires careful schema design. Hybrid approaches are common and often pragmatic.

4. **Fan-out/fan-in delivers parallelism only when subtasks are genuinely independent.** Parallelism across dependent subtasks creates races and conflicts. Fan-out must be bounded by a maximum concurrency parameter to prevent resource exhaustion. Fan-in aggregation logic deserves the same engineering rigour as the agents themselves.

5. **Multi-agent failure modes are emergent and distributed.** Cascading failure, conflicting state, partial completion, and runaway loops arise from agent interaction, not from any individual agent's malfunction. Diagnosing them requires visibility into the full inter-agent communication trace, not just individual agent outputs.

6. **Containment is an engineering requirement, not a prompt instruction.** Circuit breakers, timeout budgets, fallback policies, and write-permission restrictions must be implemented at the infrastructure level. Containment implemented only through prompting — telling agents what they should not do — is not containment.

7. **Human-in-the-loop placement is a safety/latency tradeoff governed by the cost of uncaught error.** Placing humans before dispatch provides maximum safety at maximum latency cost. Placing humans before final output provides the baseline safety guarantee at minimum latency cost. The appropriate placement depends on the stakes of the domain and the reversibility of the downstream action.

8. **Audit logs of agent writes are a non-negotiable requirement in production.** When a multi-agent system produces an incorrect output, the ability to trace which agent wrote what, when, and from what input is the difference between a diagnosable incident and an opaque system failure.

9. **The Flash Crash pattern generalises.** Systems composed of individually rational agents that interact without adequate orchestration, state management, and failure containment will produce emergent failures that no single component caused and no single component can resolve. This is not a historical curiosity — it is the defining risk of multi-agent system design.

---

### Review Questions

---

1. The Research Agent in a clinical documentation pipeline returns a response containing a hallucinated drug-drug interaction warning. The Drafting Agent incorporates the warning into a patient discharge summary, which a clinician approves without checking the provenance trail. Trace the failure through the system and identify which containment mechanisms — validation at handoff, human-in-the-loop placement, or write-permission restrictions — would most effectively have contained it, and at what cost to system latency.

2. You are designing a legal contract analysis system. A supervisor decomposes the task into four parallel subtasks: jurisdiction analysis, clause extraction, risk identification, and precedent lookup. After fan-out, the jurisdiction analysis agent returns an unexpected result that changes which precedents are relevant — but the precedent lookup agent has already completed using the wrong jurisdiction. Design a fan-out strategy that accommodates this dependency while preserving as much parallelism as possible, and explain what invariants the system must check at fan-in.

3. Two worker agents in a blackboard-pattern system simultaneously identify a conflict in a customer's order record and write their respective resolutions to the shared blackboard. Agent A writes "conflict resolved: apply discount code" and Agent B writes "conflict resolved: reject discount code." Neither write fails. Describe the state the system is now in, explain why this failure mode is particularly dangerous, and specify the concurrency control mechanism that would have prevented it.

4. A peer-to-peer multi-agent system designed for software architecture review enters a state in which the Security Agent repeatedly requests clarification from the Performance Agent, which requests clarification from the Correctness Agent, which requests clarification from the Security Agent. No agent is producing final output. Diagnose the failure mode, identify which of the four orchestration patterns would have prevented it by design, and specify the minimum set of architectural constraints that would prevent this condition from occurring in a peer-to-peer design.

5. A supervisor/worker pipeline has a total time budget of sixty seconds. The three worker agents have observed ninety-fifth percentile response times of eight seconds, fifteen seconds, and twelve seconds respectively. The aggregation step takes approximately five seconds. Design a timeout budget allocation, specify the fallback policy for each worker, and explain what the system should do if the total budget is exhausted before the aggregation step completes.

6. Your team is deploying a multi-agent system for automated financial reporting. A risk analyst argues that a human approval gate should be placed before the supervisor dispatches any agents, to review the decomposition plan. The product manager argues the gate should be placed only before the final report is committed to the reporting database, to minimise latency. Both positions have merit. Take a position, justify it by reference to the specific failure modes of each placement, and propose a hybrid approach that addresses the strongest objection to your preferred position.

---
