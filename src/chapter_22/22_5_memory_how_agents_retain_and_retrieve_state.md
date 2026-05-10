## 22.5 Memory: How Agents Retain and Retrieve State

---

A language model, in isolation, has no memory. Each inference is stateless — the model processes the tokens in its context window and produces an output, then the context is discarded. Agents require memory that persists across inference steps, across conversation turns, and in some cases across sessions. The engineering of agent memory is one of the most consequential and least standardised areas of current agent design.

There are four distinct categories in the agent memory taxonomy, each with different persistence characteristics, retrieval mechanisms, and appropriate use cases.

### 22.5.1 In-Context Memory

In-context memory is the agent's working state within a single execution session: the original goal, the conversation history, all prior reasoning steps, all tool calls and their results. It is the most immediate form of memory — zero retrieval latency, fully coherent, always current — and also the most constrained. Every token in the context window competes for space, and context windows, however large they have become, are finite.

The practical consequence is that in-context memory is exhaustible. An agent that accumulates observations without pruning its context will eventually overflow the window. When this happens, either the system truncates the oldest context (losing earlier observations that may still be relevant) or the inference fails entirely. Context exhaustion is one of the four primary agent failure modes and must be addressed by design, not managed reactively.

The engineering response to in-context memory limits is selective summarisation: at defined intervals or when context approaches a threshold, the agent (or a separate summarisation process) compresses the conversation history into a denser representation, preserving the conclusions reached in prior steps without retaining every verbatim tool result. This is not without risk — summarisation can lose detail that later proves relevant — but the alternative, unlimited context accumulation, is architecturally untenable.

### 22.5.2 External Memory

External memory persists beyond the context window and beyond the current session. It is retrieved on demand and injected into the context when needed. The canonical pattern is a key-value store or database that the agent can query through a read tool. Patient records in a clinical system, prior conversation summaries in a long-running workflow, completed task logs in a multi-session agent — these are all forms of external memory.

External memory's strength is persistence and scale: it is not constrained by the context window and can store an arbitrary volume of information. Its limitation is retrieval: the agent must know what to query and must have a tool that can retrieve the right information efficiently. If retrieval fails — because the query is poorly formulated, because the index is stale, or because the relevant information was stored in a format that does not support efficient lookup — the agent cannot benefit from information that nominally exists.

### 22.5.3 Semantic Memory

Semantic memory is external memory organised for relevance-based retrieval rather than exact-match lookup. The underlying mechanism is a vector store: documents, records, or knowledge fragments are embedded into a high-dimensional vector space, and retrieval finds the items most semantically similar to a query. This is the retrieval mechanism at the heart of RAG systems, described in detail in Chapters 17–21.

For agents, semantic memory is particularly valuable for grounding reasoning in domain knowledge that would be impractical to include in a prompt. A clinical agent might use a semantic memory store containing drug interaction data, clinical guidelines, and relevant research — retrieving the specific passages most relevant to the current patient case and injecting them into the context before the reasoning step. The quality of the agent's clinical reasoning depends directly on the quality of the semantic memory's indexing, embedding, and retrieval.

Semantic memory is not a substitute for structured external memory. When retrieval precision matters — "get the exact lab result for this patient on this date" — a structured query against a relational store is more reliable than a similarity search that might return adjacent but not exact records. The two forms of memory are complementary and most production agent systems use both.

### 22.5.4 Episodic Memory

Episodic memory is a record of what the agent has done: a log of completed tasks, past interactions, prior decisions, and their outcomes. It differs from external memory (which stores facts about the world) and from semantic memory (which stores knowledge for retrieval) in that it stores the agent's own history of action.

The primary function of episodic memory is to prevent repetition and to enable learning from prior outcomes. An agent that keeps an episodic record of which tool sequences resolved which classes of clinical query can, over time, use that record to make more informed routing decisions. An agent that has no episodic memory must treat each new task as entirely novel, regardless of how many similar tasks it has completed before.

In current practice, episodic memory is often implemented as append-only log storage combined with a summarisation step that distils completed sessions into a compact record. The implementation is straightforward; the engineering challenge is deciding what granularity of episode to store. Too coarse and the record loses the detail needed for meaningful retrieval; too fine and the store grows without bound and retrieval becomes expensive.

---
