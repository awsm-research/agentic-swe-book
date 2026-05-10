## 23.5 Failure Modes Specific to Multi-Agent Systems

---

Single-agent systems fail in predictable ways: the model produces a wrong answer, the context is misunderstood, the tool call fails. These failures are local and visible. Multi-agent systems introduce failure modes that are distributed, emergent, and significantly harder to diagnose.

### Cascading Failure

In a pipeline or supervisor/worker system, one agent's output is another agent's input. When Agent A produces a subtly wrong result — a hallucinated citation, an incorrect extraction, a misclassified entity — Agent B receives that wrong result as authoritative ground truth and builds upon it. Agent B's output is then wrong in a different and compounded way. By the time the error reaches the final output, its origin may be untraceable.

The Flash Crash is the non-AI illustration of this pattern: each trading system behaved rationally given its inputs, but those inputs were themselves the outputs of other systems behaving rationally given their now-corrupted inputs. The error did not originate in any single system; it emerged from their interaction.

Containing cascading failure requires validation at agent handoff points. Each agent should receive not just the raw output of the prior agent but also a structured confidence assessment or a set of invariants that the output must satisfy before the next agent processes it. When an agent's output fails validation, the pipeline should halt and route to a fallback, not propagate the corrupted result.

### Conflicting State

When two agents write to shared state concurrently, the result depends on the order of writes — and in an asynchronous system, that order is not guaranteed. Agent A concludes that a patient's allergy status is "penicillin-allergic" and writes that to the shared record. Simultaneously, Agent B, working from an older snapshot, concludes the allergy record is clear and writes that. One of these writes is wrong. Without a conflict detection mechanism, neither agent nor the system knows which update is current, and the downstream effect — a clinical decision based on incorrect allergy data — can be serious.

Conflicting state is not limited to concurrent writes. It also arises when agents are working from stale snapshots of shared state. If Agent B's snapshot was taken before Agent A's update was committed, Agent B's reasoning is based on information that is no longer true.

The containment strategy is explicit concurrency control: versioned writes, where each agent must include the version of the record it read and the write is rejected if the version has changed; or event sourcing, where writes are appended as events and the current state is computed by replaying the event log. Both approaches make conflicts visible rather than silent.

### Partial Completion

In a fan-out system, some agents may complete successfully while others fail, time out, or return partial results. The system must decide how to proceed. The options are: wait for all agents, which may block indefinitely if one agent is stuck; proceed with available results, which may produce an incomplete output; or retry the failed agents, which may simply reproduce the failure.

Partial completion is a normal operating condition, not an exceptional one. A multi-agent system must have an explicit policy for each subtask: is the subtask's result required — without it, the final output is invalid — or is it optional, meaning the system can produce a useful output even without it? Required subtasks that fail should trigger escalation — either a retry with modified parameters, a fallback to a simpler strategy, or a human escalation. Optional subtasks that fail should be noted in the output so downstream consumers know the result is partial, but should not block the system.

The most dangerous failure is silent partial completion: the system produces a final output without communicating that some subtasks did not complete. A user who receives a research summary without knowing that the most relevant database was unavailable during retrieval may act on an incomplete picture.

### Runaway Loops

In peer-to-peer systems, or in any system where agents can invoke other agents, the potential for recursive invocation without termination is real. Agent A calls Agent B for additional context. Agent B, encountering ambiguity, calls Agent C. Agent C calls Agent A for clarification. The cycle continues, consuming compute budget and producing no output.

Runaway loops can also occur in non-circular patterns. A supervisor that repeatedly retries a failing worker without a maximum retry count will loop indefinitely. A planning agent that decomposes a task, discovers the plan is insufficient, and re-decomposes without a convergence condition will similarly loop.

Every agent invocation must be governed by a timeout budget and a maximum invocation depth. These are not optimisations — they are mandatory safety constraints. An agent that exceeds its budget should return a partial result or a failure signal, not continue executing.

---
