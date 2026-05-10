## 23.3 State Management Across Agents

---

How agents share information is not a secondary implementation concern. It is an architectural decision that determines how correct, debuggable, and recoverable the system will be.

### Shared State

In a shared state model, all agents read from and write to a common data store — a database, an in-memory object, or a structured document. Every agent sees the same representation of the task's current state. When an agent updates the state, the update is immediately visible to all other agents.

Shared state is intuitive and efficient. It avoids the overhead of passing large data payloads between agents. It makes the current system state inspectable from any point. But it creates a coordination problem: when multiple agents write concurrently, conflicts arise. Agent A reads a record, decides to update a field, and writes its update. Between Agent A's read and write, Agent B reads the same record, updates the same field with a different value, and writes its update. One update silently overwrites the other. In a multi-agent system without careful concurrency control, this is not an edge case — it is the default.

Shared state systems require explicit concurrency management: optimistic locking, transactional writes, or event sourcing with conflict detection. Without these controls, shared state becomes shared corruption.

### Message Passing

In a message passing model, agents communicate exclusively by sending messages to each other or to a message broker. No agent accesses another agent's internal state directly. Each agent maintains its own local state and shares information only by including it in messages.

Message passing is inherently safer under concurrency. Because agents do not share mutable state, the failure modes of simultaneous writes do not arise. Messages can be queued, replayed, and audited. The system's communication history is an implicit log of everything that happened.

The cost is overhead and complexity. Large data payloads must be serialised and transmitted with each message. If Agent B needs context from Agent A's earlier work, that context must be explicitly included in the message — it is not implicitly available through shared access. Message schemas must be designed carefully; once agents depend on a schema, changing it requires coordinated updates across all agents that use it.

### Choosing Between Them

The choice is not purely technical. Shared state fits systems where agents are tightly coupled by design, where the shared representation is the product (a document, a data record, a structured report), and where the system can afford the engineering investment in concurrency control. Message passing fits systems where agents are loosely coupled, where auditability of inter-agent communication is a requirement, and where the failure surface of concurrent writes is unacceptable.

Hybrid approaches — a shared read-only knowledge store combined with message passing for agent coordination — are frequently the better choice.

---
