## 22.2 The Spectrum from Chatbot to Autonomous Agent

---

Understanding what agents are requires understanding what they are not. Three categories occupy a spectrum of autonomy, and engineers who conflate them build systems with mismatched safety assumptions.

A **chatbot** is a system that responds to a single input and produces a single output. Its intelligence is entirely within the response generation step. It has no state between turns other than what is explicitly included in the conversation history. It takes no actions beyond returning text. The risk profile of a chatbot is bounded: the worst it can do is produce a harmful or misleading response, which a human then acts upon or ignores. The human remains in control of every consequential action.

A **copilot** is a system that assists a human who retains explicit control. The copilot may invoke tools — searching documentation, retrieving context, generating code — but it does so in response to a human instruction and presents the result for human review before any consequential action occurs. GitHub Copilot suggests code; the developer decides whether to accept the suggestion. The copilot's tool calls may have side effects (a search query, a retrieval operation), but the write actions that affect the world outside the system require human approval. A copilot with well-designed read-only tools is relatively safe because the human oversight layer intercepts every consequential decision.

An **autonomous agent** pursues a multi-step goal with minimal human intervention at each step. It decides which tools to invoke, in what sequence, based on its own reasoning and the observations it accumulates. A human may define the goal and may be consulted at defined checkpoints, but the agent executes the intermediate steps without waiting for approval. This is where the risk profile changes qualitatively. The agent's write actions — modifying a database, sending a message, executing a transaction — happen before a human sees them. Errors compound. An incorrect early inference, if unchecked, propagates through subsequent steps and may trigger actions that cannot be reversed.

The appropriate engineering posture differs across all three. A chatbot requires output safety guardrails. A copilot requires read-tool safety and human approval workflows for write actions. An autonomous agent requires all of the above, plus termination conditions, state checkpointing, audit trails, and circuit breakers. Treating a system built to copilot standards as if it were safe to operate autonomously is one of the most common and consequential mistakes in current AI engineering practice.

---
