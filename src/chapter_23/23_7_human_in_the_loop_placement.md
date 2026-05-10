## 23.7 Human-in-the-Loop Placement

---

The phrase "human-in-the-loop" describes a design choice, not a single mechanism. In a multi-agent system, a human can be placed at multiple points in the workflow, and the choice of placement determines the tradeoff between safety and latency.

### Before Dispatch: Approving the Plan

A supervisor/worker system that plans before executing can surface its plan for human review before dispatching any worker agents. The human sees: "I intend to decompose this task into these three subtasks, delegate them to these three agents, and aggregate results in this way. Do you approve?" If the plan is wrong — if the decomposition misses a critical component, if the wrong agent is assigned to a sensitive subtask — it can be corrected before any work is done.

This checkpoint is the highest-safety option. It catches decomposition errors before they propagate. Its cost is latency: every task waits for a human to review the plan before execution begins. For high-stakes, infrequent tasks, this cost is acceptable. For high-volume, time-sensitive tasks, it is not.

### Between Agents: Approving Intermediate Results

A checkpoint placed at the handoff between agents — after the Research Agent completes but before the Drafting Agent begins — allows a human to verify the intermediate result before it becomes the input to the next stage. This checkpoint is particularly valuable when the intermediate result will be difficult to audit once it has been transformed by subsequent agents.

In a clinical documentation system, approving the retrieved clinical evidence before it enters the drafting stage is a meaningful safety gate. If the retrieved evidence contains an error, it is far easier to correct at this point than after a clinician note has been drafted from it.

The tradeoff is that human reviewers become a bottleneck. If the pipeline has three inter-agent checkpoints and each requires human approval, the latency of the workflow is dominated by human response time. Selective placement — checkpoints only at the highest-risk handoffs, not at every transition — is the practical approach.

### Before Final Output: Approving Before Action

The most common placement is a final approval gate before the system takes an irreversible action — before the drafted note is committed to the clinical record, before the generated email is sent, before the automated code change is deployed. This gate catches errors that have survived the entire pipeline but have not yet caused harm.

Final approval is the minimum viable human-in-the-loop implementation. It provides a last line of defence but does not catch errors that have already compounded through multiple pipeline stages. A drafting agent that has built on incorrect retrieved evidence will produce an incorrect draft, and the final approval gate requires the approver to be sufficiently expert to detect the error — which may not be guaranteed at production volume.

| Placement | Safety | Latency Cost | Appropriate When |
|---|---|---|---|
| **Before dispatch** | Highest | Highest | High-stakes, infrequent tasks; novel task decompositions |
| **Between agents** | Medium | Medium | High-risk handoffs; irreversible intermediate transformations |
| **Before final output** | Baseline | Lowest | Routine tasks with well-validated pipelines; final action is irreversible |

Place the human checkpoint where the cost of an uncaught error exceeds the cost of the wait. For clinical, legal, financial, and safety-critical domains, that threshold is lower than for routine information tasks.

---
