## 23.2 Orchestration Patterns

---

Four orchestration patterns account for the majority of multi-agent system designs. Each reflects a different answer to the question of how agents communicate, who holds authority over task decomposition, and how results are aggregated. Choosing the wrong pattern for a context is an architectural mistake that manifests as fragility, latency, or coordination failure.

### Supervisor/Worker

In the supervisor/worker pattern, a planner agent — the supervisor — receives a high-level task, decomposes it into subtasks, delegates each subtask to a specialist worker agent, and aggregates the returned results into a final output.

The supervisor holds the task model. It understands the goal, the dependencies between subtasks, and the criteria for a satisfactory result. Workers hold domain expertise. They do not need to understand the full task — only their assigned slice of it. The supervisor is responsible for sequencing, for detecting when a worker has failed, and for deciding whether to retry, substitute, or escalate.

This pattern suits tasks with clear decomposition into specialist domains, where the overall goal is well-defined upfront. Clinical documentation is a strong example: a supervisor decomposes "generate a discharge summary" into records retrieval, evidence lookup, and note drafting — each handled by a specialist. Legal contract review, multi-source research synthesis, and software architecture analysis follow the same structure.

The pattern's weakness is its single point of authority. If the supervisor's decomposition is wrong — if it misidentifies the subtasks, misunderstands dependencies, or produces an aggregation that loses critical nuance from the workers — the entire pipeline is compromised. Supervisors require careful evaluation of their planning quality, not just their output quality.

### Pipeline

In the pipeline pattern, agents are arranged as a chain. Each agent consumes the prior agent's output, transforms or enriches it, and passes the result to the next. There is no central planner. The task flows through a predetermined sequence of transformations.

This pattern is appropriate when the transformation sequence is stable and well-understood — when the same steps apply to every instance of the task in the same order. Data enrichment pipelines fit this model well: raw data enters, a cleaning agent processes it, an enrichment agent annotates it, a validation agent checks it, and a formatting agent renders it. Document translation, multi-stage code generation, and extract-transform-load workflows are natural pipeline tasks.

The pipeline pattern's strength is its simplicity and predictability. Each agent has a single, defined responsibility. Testing is straightforward: test each stage in isolation, then test the integration. The weakness is rigidity. Pipelines assume the sequence is fixed. If stage three needs information that only becomes available at stage five, the pipeline cannot accommodate that without restructuring. Pipelines also accumulate errors: a problem introduced at stage two propagates through stages three, four, and five, often becoming harder to diagnose at each step.

### Peer-to-Peer

In the peer-to-peer pattern, agents communicate directly with each other without a central coordinator. Any agent can initiate communication with any other agent. There is no authority structure; coordination emerges from the communication protocols the agents follow.

This pattern is most appropriate when tasks are genuinely open-ended and the path to a solution is not known upfront — when agents must negotiate, challenge each other's outputs, and iteratively refine results. Debate architectures, where multiple agents argue different positions and converge on a resolution, are the canonical use case. Multi-agent code review, where a security agent, a performance agent, and a correctness agent comment on each other's assessments, is a practical application.

The peer-to-peer pattern is the most powerful and the most dangerous. Its power is flexibility: agents can respond to what they actually encounter, not to what a planner predicted they would encounter. Its danger is complexity: without a supervisor, runaway conversations, deadlocks, and conflicting conclusions are harder to detect and contain. Implementing peer-to-peer systems requires robust message schemas, explicit termination conditions, and careful logging of all agent-to-agent communication.

Do not use peer-to-peer where a supervisor/worker pattern will serve. The complexity cost is real.

### Blackboard

In the blackboard pattern, agents share a common knowledge store — the blackboard — and no direct agent-to-agent messaging occurs. Each agent reads from the blackboard, performs its contribution, writes results back to the blackboard, and the system progresses as the shared state accumulates contributions.

The blackboard architecture was formalised through AI research of the 1970s and 1980s — the HEARSAY-II speech understanding system is among its most cited early implementations (Erman et al., 1980). Its contemporary form appears in multi-agent systems where agents must each contribute domain knowledge to a growing shared representation, but where tight coupling between agents would create brittleness.

The blackboard pattern suits tasks where the knowledge required to solve the problem is distributed across specialists, where the order in which specialists contribute is flexible, and where the final answer is read from the accumulated state rather than computed by any single agent. Security posture analysis — where a network agent, a code analysis agent, and a configuration review agent each annotate a shared vulnerability register — is a good fit. So is distributed evidence gathering, where multiple research agents contribute findings to a shared evidence base from which a synthesis agent eventually draws.

The pattern's weakness is that the blackboard itself becomes a consistency challenge. If two agents write to the same field simultaneously with conflicting values, the system must have a conflict resolution strategy. Blackboard systems require explicit schemas, write locking or versioning, and audit trails of which agent wrote what and when.

| Pattern | Authority | Communication | Best For | Primary Risk |
|---|---|---|---|---|
| **Supervisor/Worker** | Centralised (supervisor) | Supervisor to/from Workers | Decomposable tasks with clear specialist domains | Supervisor planning errors |
| **Pipeline** | Implicit (sequence) | Sequential handoff | Fixed transformation sequences | Error propagation, rigidity |
| **Peer-to-Peer** | Distributed | Any-to-any | Open-ended negotiation and debate | Runaway loops, conflicting conclusions |
| **Blackboard** | None (shared state) | Via shared store | Distributed knowledge contribution | State conflicts, consistency |

---
