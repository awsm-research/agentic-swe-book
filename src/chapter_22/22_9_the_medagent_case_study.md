## 22.9 The MedAgent Case Study

---

MedAgent is the autonomous clinical decision support agent introduced in Chapter 13 and developed through Chapters 22–24. It illustrates how the abstractions covered in this chapter manifest in a real system operating under clinical safety constraints.

MedAgent's goal structure is hierarchical. A clinician provides a high-level goal: "Review this patient's case and identify whether the proposed medication change requires a specialist referral." The agent must retrieve the patient's history, analyse it against clinical guidelines, formulate a recommendation, and — if a referral is indicated — initiate the referral workflow with appropriate clinical documentation. This is a multi-step goal that spans read operations, clinical reasoning, a write operation, and a human approval checkpoint.

The ReAct loop is the core execution pattern. At each iteration, MedAgent reasons over its current state — the goal, the retrieved patient data, the clinical guidelines it has accessed, and all prior observations — and decides what action to take next. The reasoning is explicit and logged: the agent's thought process at each step is written to a structured trace that the supervising clinician can review. This is not merely good practice; in the clinical context it is an accountability requirement. A recommendation that cannot be traced to the reasoning that produced it is not clinically defensible.

MedAgent's tool set is divided strictly by the read/write distinction. Read tools — patient history retrieval, medication database lookup, clinical guideline search, drug interaction checker — are available at every step without additional approval requirements. Write tools — referral submission, clinical note creation, medication order entry — require a human approval step before execution. This approval step is implemented as a LangGraph node that pauses the execution graph, serialises the current state to persistent storage, and waits for a clinician's confirmation before proceeding. The agent does not timeout or fail if the clinician does not respond immediately — it waits, checkpointed, until the approval is received or a configurable deadline passes.

Memory in MedAgent uses all four categories. In-context memory holds the current session's reasoning trace and tool results. External memory holds the patient's full clinical record, which is too large to include in context in its entirety and is retrieved selectively by structured query. Semantic memory holds the clinical guideline corpus, retrieved by relevance to the current case. Episodic memory holds a log of past recommendations MedAgent has made for this patient, providing continuity across sessions and flagging cases where the agent has previously escalated similar situations.

The LangGraph state machine for MedAgent has explicitly defined nodes for: goal parsing, history retrieval, guideline retrieval, drug interaction checking, clinical reasoning, recommendation formulation, human approval, and write-tool execution. Conditional edges route from the clinical reasoning node to the recommendation node if analysis is complete, or back to the retrieval nodes if additional information is needed. A mandatory termination node is triggered after seven iterations or after thirty minutes of elapsed time, producing a partial analysis report rather than looping indefinitely.

This architecture does not eliminate clinical risk. MedAgent can still reason incorrectly, retrieve irrelevant guidelines, or formulate a flawed recommendation. But the architecture makes every point at which failure can occur visible, auditable, and subject to human oversight at the most consequential steps. That is the standard to which Software 4.0 clinical systems should be held.

---
