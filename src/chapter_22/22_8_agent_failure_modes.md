## 22.8 Agent Failure Modes

---

The four primary failure modes of autonomous agents are structural properties of the paradigm, not edge cases. Each requires deliberate engineering controls built into the architecture from the start.

### 22.8.1 Hallucination Cascades

A language model may hallucinate — generate a plausible but false claim — in the Reason step of any iteration. In a single-inference system, a hallucination produces a wrong output that a human may catch. In a ReAct loop, a hallucination in an early reasoning step becomes a premise for subsequent steps. If the agent reasons that a patient's last medication review was six months ago and plans accordingly, every subsequent action taken on that false premise is built on corrupted ground. The hallucination does not announce itself — it is embedded in the reasoning trace as if it were an established fact.

The mitigation is grounding: the Reason step should reason over verified observations, not over its own prior inferences. Tool calls should be used to verify key claims before they become premises for consequential actions. A clinical agent that determines a patient's medication history should retrieve it from a database rather than relying on information mentioned in prior conversation turns that may itself have been inferred incorrectly.

### 22.8.2 Tool Misuse

An agent that calls a tool with invalid parameters does not necessarily receive a clean error. Depending on the tool's implementation, it may receive an empty result (which it may misinterpret as "the patient has no medication history" rather than "the query was malformed"), a partial result, or a generic error that provides no guidance on how to reformulate the call. If the tool's schema is underspecified, the agent may repeatedly generate invalid calls without understanding why they fail.

The mitigation is defensive tool schema design: explicit parameter types, required vs. optional field documentation, and specific error messages that explain what went wrong and how to correct it. A tool that returns "Error: patient_id must be a non-empty string, received null" gives the agent actionable information. A tool that returns "Internal error" does not.

### 22.8.3 Infinite Loops

Without explicit termination conditions, an agent may loop indefinitely: reasoning, calling a tool, observing a failure, reasoning again, calling the same tool with marginally different parameters, observing another failure, and repeating. This is particularly common when the agent's goal is underspecified — it does not have a clear criterion for success and therefore cannot determine when to stop — or when the tool the agent needs is unavailable.

The mitigation is mandatory termination conditions: a maximum iteration count, a maximum elapsed time, and explicit goal-satisfaction criteria that the agent checks at each Reason step. These are not optional safety additions — they are architectural requirements for any agent intended for production use. An agent without a termination condition is not a production agent; it is an experiment.

### 22.8.4 Context Exhaustion

As the ReAct loop iterates, the context window fills with reasoning traces, tool schemas, tool results, and conversation history. When the context approaches the window limit, the agent's performance degrades. Either the system silently truncates earlier context — causing the agent to "forget" observations it made in earlier iterations — or the inference fails with a context-length error.

The mitigation is active context management: summarising completed reasoning chains, pruning redundant tool results, and storing key findings in external memory rather than retaining raw tool output in context. This requires engineering judgement about what to preserve and what to compress, and it should be designed into the agent's architecture from the outset, not added when context exhaustion begins to cause failures in production.

---
