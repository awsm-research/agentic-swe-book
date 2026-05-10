## 22.10 Key Takeaways

---

1. **Agents are not chatbots with tools.** The defining property of an autonomous agent is goal-directed action across multiple steps, where the agent decides the sequence of actions without human approval at each step. This shifts the locus of control from engineer or user to the system itself, with profound implications for safety engineering.

2. **The ReAct loop is the foundational pattern.** Reason, Act, Observe, repeat — this three-phase cycle grounds agent reasoning in real-world observations at each step, preventing the hallucination cascades that occur when a model reasons only over its own prior inferences.

3. **Tool schema design is a first-class engineering concern.** The description, parameter types, constraints, and failure documentation of every tool directly determine whether the agent can use it correctly. Underspecified tool schemas produce tool misuse; overloaded schemas produce confusion.

4. **The read/write distinction is the most important safety boundary in tool design.** Read tools can be called freely; write tools require validation, idempotency design, human approval gates for consequential actions, and immutable audit logging.

5. **Agents need four types of memory.** In-context memory is immediate but finite. External memory is persistent and structured. Semantic memory enables relevance-based retrieval from large knowledge corpora. Episodic memory provides continuity across sessions and supports learning from prior outcomes.

6. **Explicit planning improves performance when tasks have multi-step dependencies or parallelisable subtasks.** For simpler tasks, the overhead of planning exceeds its benefit, and the ReAct loop alone is more efficient.

7. **LangGraph models agents as state machines.** Nodes represent actions, edges represent transitions, and conditional edges encode safety logic. State persistence enables checkpointing for long-running workflows and human-in-the-loop approval steps.

8. **The four primary failure modes require architectural controls, not runtime patches.** Hallucination cascades require grounding. Tool misuse requires defensive schema design. Infinite loops require mandatory termination conditions. Context exhaustion requires active context management. Each is a design requirement, not an operational concern.

9. **The chatbot–copilot–agent spectrum is a risk spectrum.** Moving from copilot to autonomous agent removes a layer of human oversight from every consequential action. The engineering obligations that come with that removal — termination conditions, audit trails, human approval gates, circuit breakers — are proportional to the autonomy granted.

10. **MedAgent is the clinical embodiment of these principles.** Its design — the ReAct loop for reasoning, the strict read/write tool taxonomy, the four-category memory architecture, the LangGraph state machine with mandatory human approval nodes — is a concrete answer to the question of what it takes to operate an autonomous system safely in a regulated, high-stakes domain.

---

### Review Questions

---

1. A product team proposes an "autonomous customer service agent" that can access order history, process refunds, and send emails — all without human approval at any step. Using the read/write tool distinction, identify which of these capabilities require explicit human approval gates, and explain what failure mode you would expect to see in production if those gates are absent.

2. A clinical engineering team reports that their agent intermittently produces recommendations that contradict earlier observations it made in the same session. They have no structured trace logging. Using the ReAct loop and the hallucination cascade failure mode, explain what is likely happening, what data you would need to diagnose it, and what architectural change would prevent it.

3. An agent is deployed to perform quarterly financial audits. Each audit involves retrieving hundreds of transaction records and performing multi-step reconciliation. After six months, users report that the agent's recommendations become less coherent in the later steps of each audit. Identify which memory failure mode is most likely responsible, and describe two architectural mitigations.

4. A team is designing a software agent that automates legal contract review. They argue that because the agent only reads documents and produces a summary report — never modifying any external system — they do not need termination conditions or circuit breakers. Evaluate this argument, identifying which failure modes remain applicable for a read-only agent and which do not.

5. You are designing the LangGraph state machine for a multi-step travel booking agent. The agent must search for flights, check availability, suggest itineraries, and — upon user confirmation — book the selected flights. Describe the node and edge structure in prose, specifying which edges are conditional and what the termination conditions are. Explain where the human approval gate sits and why it is positioned there rather than at a different node.

6. MedAgent uses all four memory categories for a single patient case. Explain why no single memory category is sufficient on its own, using a specific failure scenario that would occur if each category were absent from the design.

---
