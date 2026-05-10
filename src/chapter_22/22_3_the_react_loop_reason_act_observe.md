## 22.3 The ReAct Loop: Reason, Act, Observe

---

The architectural pattern that governs most practical agent design is the ReAct loop, formalised by Yao et al. in 2022 (Yao et al., arXiv:2210.03629). The name is a portmanteau of Reason and Act, but the loop has three phases: Reason, Act, and Observe.

In the **Reason** phase, the agent uses the language model to interpret its current state — the original goal, the conversation history, and all prior observations — and to decide what action to take next. This is not passive question-answering. The model is prompted to produce explicit reasoning: what do I know, what do I need to find out, and what action will advance me toward the goal? The reasoning trace is not decoration — it is the mechanism by which the agent identifies which tool to call and with what parameters.

In the **Act** phase, the agent executes the action decided during the Reason step. In practice, this means calling a tool: retrieving information from a database, executing a search query, writing a file, calling an external API, or invoking another agent. The act step produces an outcome in the world — or, for read tools, an observation about the world.

In the **Observe** phase, the agent receives the result of the action and appends it to its working state. The observation is concrete: the text returned by a database query, the status code returned by an API call, the content of a retrieved document. This observation is not interpreted yet — that happens in the next Reason step.

The loop then repeats. The agent reasons over its updated state, decides on the next action, acts, and observes. This continues until one or more of the following conditions are met — and production systems should enforce all three simultaneously: the agent determines the goal has been achieved, the agent determines the goal cannot be achieved and generates a failure report, or a termination condition enforced by the system is triggered (a maximum step count, a timeout, or a circuit breaker).

The power of the ReAct pattern is that it grounds the agent's reasoning in observations from the real world at each step. Without the Observe step, the agent's reasoning would compound on itself — each step generating inferences based on prior inferences, with no corrective signal from reality. The Schwartz case illustrates exactly this failure: a language model generating text without an observe step that could have checked each citation against a real database. The ReAct loop, properly implemented, makes that failure structurally impossible, because the tool call either returns a confirmed record or returns a null result that the agent must reason about.

Yao et al.'s empirical finding was that the combination of reasoning and acting outperformed both pure reasoning (chain-of-thought without tool use) and pure acting (tool use without explicit reasoning) across a range of tasks. The reasoning step helps the agent select better actions; the observations ground subsequent reasoning in verifiable fact. Neither alone is sufficient.

---
