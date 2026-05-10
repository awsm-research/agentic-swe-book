## Learning Objectives

By the end of this chapter, you will be able to:

1. Explain why complex tasks require multi-agent architectures and identify the specific limits of single-agent systems.
2. Compare the four primary orchestration patterns — supervisor/worker, pipeline, peer-to-peer, and blackboard — and select the appropriate pattern for a given context.
3. Describe the tradeoffs between shared state and message passing for inter-agent communication.
4. Design a fan-out/fan-in strategy for parallel agent dispatch, including conditions under which parallelism is unsafe.
5. Identify the failure modes specific to multi-agent systems and apply containment strategies — circuit breakers, timeout budgets, fallback behaviours, and write-permission restrictions — to each.
6. Determine the appropriate placement of human-in-the-loop checkpoints in a multi-agent workflow, balancing safety against latency.

---
