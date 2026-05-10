## 24.4 Safety Constraints Engineering

---

Observability tells you what happened after the fact. Safety constraints prevent harmful things from happening in the first place. For agentic systems, there are four engineering patterns that together constitute the minimum viable safety constraint stack. Any agent that takes irreversible actions in a regulated domain must implement all four.

### 24.4.1 Scope Restriction: Least Privilege for Agents

The principle of least privilege — that a system component should have access only to the resources it needs to perform its current function — is one of the oldest and most important principles in computer security. Applied to agents, it means that an agent should have access only to the tools it needs for its current task, with no access to tools that are not relevant to the current goal.

Scope restriction is more than a security control — it is a reliability control. An agent with access to twenty tools is significantly more likely to select an inappropriate tool than an agent with access to five. The LLM's tool selection is based on semantic similarity between the task description and the tool descriptions; when irrelevant tools are in scope, there is a non-trivial probability that the agent selects one by mistake, particularly in edge cases where the task description is ambiguous. Restricting scope reduces the probability of tool misselection while simultaneously reducing the attack surface for prompt injection attacks that attempt to cause the agent to invoke a tool it would not otherwise have selected.

In practice, scope restriction is implemented through task-specific tool sets. A clinical documentation agent has access to read-only records tools and a draft-note writing tool. A referral agent has access to specialist directory lookup and referral submission tools. A medication review agent has access to drug interaction search and allergy verification tools. No single agent receives the full tool set of the platform.

### 24.4.2 Approval Workflows: Human-in-the-Loop Checkpoints

An approval workflow is an architectural pattern in which the agent proposes an irreversible action and then suspends execution, waiting for an explicit human decision before proceeding. The critical word is architectural. An approval workflow implemented through prompt engineering — instructing the agent to "always ask the user before taking irreversible actions" — is not a reliable safety control, because it can be bypassed by a sufficiently clever input or a reasoning failure. An approval workflow implemented through the agent framework's execution model — where the agent's graph is structured such that irreversible action nodes are unreachable without traversing an approval gate node — cannot be bypassed through prompt manipulation.

This distinction matters enormously. In a representative class of prompt injection incidents, the agent has been instructed to perform a verification step before taking an irreversible action, and that instruction is in the system prompt. The attack works not by removing the instruction but by providing a sufficiently compelling synthetic context — a falsified tool result — that causes the agent to conclude the verification has already been completed. An approval gate implemented at the graph level presents the proposed action to a human reviewer regardless of what the agent believes about its prior reasoning.

The design of approval workflows must also address the rejection path. An agent that is told "your proposed action was rejected" must be capable of replanning — generating an alternative course of action that achieves the user's goal without the rejected action. An agent that cannot replan from a rejection is not suitable for deployment in a human-in-the-loop system; its inability to recover from rejection will cause clinicians to approve actions reflexively rather than carefully, negating the safety benefit of the workflow.

### 24.4.3 Circuit Breakers: Automatic Halting

A circuit breaker is a control that automatically halts an agent when it crosses a defined threshold — in action budget, time budget, error rate, or cost. The name comes from electrical engineering: a circuit breaker opens the circuit when current exceeds a safe level, preventing damage to downstream components.

For agents, the most important circuit breaker thresholds are: maximum number of tool calls per session (a session that has executed fifty tool calls without reaching a terminal state is very likely stuck in a loop or pursuing a goal that cannot be achieved with the available tools); maximum session duration (a session that has been running for thirty minutes without completing may have encountered an irresolvable state); maximum error rate (a session in which three consecutive tool calls have returned errors should be paused for investigation rather than allowed to continue making calls that may have unknown side effects); and maximum session cost (a session that has consumed ten times the median token cost may be processing maliciously large content or caught in a token-amplifying loop).

Circuit breakers must be non-bypassable by the agent. An agent that can disable its own circuit breakers — for example, by setting a flag in its state that suppresses the circuit breaker check — provides no safety guarantee. Circuit breakers must be implemented as infrastructure-level controls, external to the agent's own state machine.

### 24.4.4 Sandboxing: Isolation of Agent Actions

Sandboxing means isolating agent actions so that failures cannot propagate to production systems. The principle is the same as in operating system security: processes run in isolated environments so that a compromised process cannot affect other processes or the underlying system. For agents, the most important sandbox boundaries are: separate test and production environments (an agent in a test environment cannot accidentally take actions that affect production data), read-only access to production data for development-phase agents (an agent that can only read production data cannot cause direct harm during development testing), and staged rollout of new tool capabilities (a new tool is deployed first to a small fraction of sessions, with its actions monitored for anomalies before full rollout).

The MedAgent system developed across Chapters 21–24 implements this through environment-specific configurations: development instances use a synthetic patient dataset and mock implementations of irreversible action tools that log the proposed action without executing it. The integration with real hospital systems is enabled only in the production environment, after the system has passed the full evaluation and red team process.

---
