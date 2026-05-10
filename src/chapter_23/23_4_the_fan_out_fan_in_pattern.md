## 23.4 The Fan-Out/Fan-In Pattern

---

The fan-out/fan-in pattern is the mechanism by which multi-agent systems realise parallelism. A coordinator dispatches a set of independent subtasks to multiple agents simultaneously — the fan-out. Each agent works independently and returns its result. The coordinator aggregates the results — the fan-in — and produces a combined output.

When the subtasks are genuinely independent, fan-out/fan-in delivers significant latency reduction. Three research agents working in parallel on three independent questions return their results in the time it takes the slowest one to complete, rather than in three times the time of the average. For tasks with a natural parallel structure — multi-source retrieval, parallel code analysis, simultaneous translation into multiple target documents — fan-out/fan-in is the correct pattern.

### When Parallelism Is Dangerous

Parallelism is appropriate only when the subtasks are truly independent. Independence means: the output of subtask A does not affect the correct execution of subtask B; and neither A nor B modifies shared state that the other reads.

When these conditions are not met, fan-out creates races. Two agents simultaneously editing the same document, or simultaneously querying and updating the same database record, produce conflicts that may be silent — no error is raised, but the result is incorrect. The correctness of the system depends on the agents not interfering with each other, and that dependency must be verified at design time, not assumed at runtime.

A second danger is resource exhaustion. Fanning out to fifty agents simultaneously may exceed API rate limits, memory budgets, or downstream service capacity. Fan-out must be bounded. A maximum concurrency parameter — the maximum number of agents operating in parallel at any moment — is a required design element, not an optional optimisation.

Fan-in introduces its own risks. If the aggregation logic is incorrect — if it silently drops results from agents that returned partial data, or if it naively concatenates outputs without checking for contradictions — the fan-in step can produce a worse result than any individual agent would have produced alone. Aggregation logic deserves the same engineering attention as the agents themselves.

---
