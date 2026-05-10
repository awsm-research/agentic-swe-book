## 23.1 Why a Single Agent Is Not Enough

---

The appeal of a single, general-purpose agent is real. One agent, one context window, one set of instructions — simple to reason about, simple to monitor, simple to debug. For many tasks, a single agent is exactly the right tool. Ask it to summarise a document, draft a response, or answer a question grounded in retrieved context, and a well-prompted single agent will perform well. The problems emerge when the task grows beyond what a single agent can hold, know, or do.

### Context Window Limits

Every language model has a finite context window. For current frontier models this window is large — hundreds of thousands of tokens — but it is not unlimited, and it degrades before it is full. Research consistently shows that retrieval accuracy and reasoning coherence decline as context length increases; models tend to attend more strongly to content near the beginning and end of the window, with content in the middle receiving less reliable attention. A task that requires simultaneously holding a large codebase, a regulatory specification, a conversation history, and a set of intermediate results will eventually exceed what a single agent can process reliably, regardless of the nominal context limit.

This is a structural property of single-agent design, not a transient limitation that larger context windows will eliminate. Even as context windows grow, the tasks organisations want to automate grow with them. The gap between what the agent can hold in mind and what the task requires is structural, not incidental.

### Specialisation Gaps

A single general-purpose agent is, by design, not a specialist. Clinical reasoning, legal analysis, software security review, financial modelling — each domain has developed vocabularies, heuristics, and evaluation standards that benefit from focused fine-tuning or specialised prompting. A general agent asked to produce a clinical decision support recommendation alongside a security audit of the code that serves it will perform both tasks less reliably than two specialised agents each doing one.

The analogy to human teams is imperfect but instructive. We do not expect a single engineer to simultaneously be the database administrator, the security architect, and the UX researcher on a complex project. We form teams. Multi-agent systems are the automated equivalent of that division of labour.

### Sequential Bottlenecks

A single agent processes tasks sequentially. Even if a task has naturally parallel sub-components — three independent research threads, five separate data transformations, a set of unit tests that share no state — a single agent must execute them one after another. As task complexity grows, this sequential bottleneck imposes latency costs that are unacceptable in production systems.

These three pressures — context limits, specialisation gaps, and sequential bottlenecks — constitute the engineering case for multi-agent design. The question is not whether to use multiple agents, but how to organise and safeguard them.

---
