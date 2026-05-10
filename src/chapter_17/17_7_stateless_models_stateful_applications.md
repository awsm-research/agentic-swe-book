## 17.7 Stateless Models, Stateful Applications

---

The LLM API is stateless. Every call to the API is independent. The model has no memory of previous calls. If you want the model to behave as if it remembers a prior conversation, you must include the relevant prior context in the current call's input. This statelessness is a design property, not a limitation: it enables horizontal scaling, simplifies model serving infrastructure, and makes each request independently reproducible. But it places the full burden of conversational state management on the application layer.

### 17.7.1 Session Management

A session is a sequence of related user interactions that share context. For most conversational applications, a session corresponds to a single user's conversation during a continuous use period. The application must identify session boundaries, assign session identifiers, store the session's accumulated state, and retrieve it for each new turn.

Session management is straightforward when sessions are short and users are few. It becomes a production engineering challenge at scale. A session store that holds all conversation history for all concurrent users must handle concurrent writes, efficient retrieval, appropriate expiry, and — in regulated domains — appropriate audit retention. The session store is infrastructure: it must be designed, deployed, monitored, and maintained with the same rigour as any other application database.

### 17.7.2 Conversation History

Conversation history is the primary mechanism by which LLM applications provide the model with memory of prior turns. Each prior turn — the user's message and the model's response — is included in the current call's message list, in chronological order. The model reads this history and uses it to generate a contextually appropriate response.

The engineering complexity of conversation history stems from two competing pressures. Including more history gives the model more context and produces more coherent multi-turn behaviour. Including less history reduces token cost and reduces context drift risk. The resolution is history management: actively curating what history is included rather than passively accumulating everything.

The three canonical approaches to history management each have appropriate use cases. The sliding window approach — include only the last N turns, drop the oldest when the budget is exceeded — is simple, predictable, and appropriate for applications where each turn is relatively self-contained. Summarisation — compress older history into a compact summary and include the summary alongside recent turns — is more sophisticated and preserves the semantic content of earlier turns without their token cost. Selective pruning — use semantic similarity to identify which prior turns are most relevant to the current query and include only those — is the most computationally expensive approach and is generally warranted only when sessions are very long and earlier turns are frequently relevant.

### 17.7.3 Memory Beyond the Session

For some applications, context from past sessions is relevant to current ones. A clinical chatbot that has established a patient's allergy history, current medication list, and relevant conditions in prior sessions can provide more appropriate responses in new sessions if that context is available. This requires a memory layer that persists selected information across session boundaries.

Memory introduces engineering complexity that is qualitatively different from within-session history management. Cross-session memory must be stored, indexed, and retrieved selectively — not all past context is relevant to every new query. It must be versioned, because information that was correct in a past session may have changed. And it raises significant data governance questions: who owns the stored memory, how long is it retained, who can access it, and what happens when the user requests its deletion?

For most applications, the engineering cost of a full cross-session memory system is not justified. A well-designed retrieval layer that can efficiently access a user's persistent profile — a structured record of known preferences, relevant history, and standing constraints — is often a simpler and more maintainable approach than a general-purpose memory system.

---
