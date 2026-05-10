## 22.1 What an Agent Actually Is

---

The word "agent" has been used loosely enough in the AI industry to mean almost anything: a chatbot with a system prompt, a RAG pipeline with a retrieval step, a Python script that calls an API. This imprecision causes engineers to underestimate what genuine agency requires and to overestimate what their systems can safely do.

The formal definition from Wooldridge and Jennings (1995) is useful precisely because it is demanding. An agent is a computational system situated in an environment that is capable of autonomous action in that environment in order to meet its design objectives. Four properties follow from this definition: reactivity (the agent perceives and responds to the environment), pro-activeness (the agent pursues goals, not just responses), social ability (the agent interacts with other agents or systems), and continuity (the agent operates over time, not just in a single request-response cycle). The social ability property — interaction with other agents or systems — is treated in depth in Chapter 23; this chapter focuses on the single-agent case.

By this standard, most systems marketed as "AI agents" in 2024 are not agents. A chatbot that answers questions is reactive but not pro-active — it waits for prompts. A code completion copilot is pro-active in a narrow sense but operates within a single interaction context and does not plan across multiple steps. A genuine agent receives a goal — "research the patient's medication history and flag any contraindications with the proposed treatment" — and then plans and executes a sequence of actions autonomously until the goal is achieved or it determines that it cannot be.

This distinction connects directly to the Software 4.0 framing from Chapter 13. In Software 1.0, the engineer decides the logic. In Software 3.0, the prompt decides what the model does within a single inference. In Software 4.0, the agent decides the sequence of steps required to achieve a goal. The locus of control has shifted from the engineer and user to the system itself. That shift moves safety obligations from the human in the loop to the system's architecture — a change in accountability structure, not merely a capability upgrade. When an engineer writes a function that sends an email, the engineer is responsible for that action. When an agent decides to send an email as one step in a longer workflow, the question of accountability is more complex — and the engineering discipline required to make the answer tractable is what AgentOps addresses.

---
