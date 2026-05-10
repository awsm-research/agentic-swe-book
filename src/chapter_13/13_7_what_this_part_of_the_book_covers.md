## 13.7 What This Part of the Book Covers

The chapters that follow apply this framework through three extended case studies:

**ChestScan** (Chapters 14–16) is a medical imaging classifier that demonstrates the MLOps lifecycle end to end. It shows how data engineering decisions affect model quality, how run management enables systematic comparison, how evaluation gates prevent unsafe models from reaching production, and how production monitoring detects clinical distribution shifts.

**MedChat** (Chapters 17–21) is a clinical RAG chatbot that demonstrates the LLMOps lifecycle. It shows how RAG pipeline design determines answer quality, how prompt engineering is a testable software discipline, how LLM evaluation frameworks quantify quality at scale, and how serving infrastructure controls cost and latency in production.

**MedAgent** (Chapters 22–24) is an autonomous clinical decision support agent that demonstrates the AgentOps lifecycle. It shows how multi-agent orchestration distributes complex tasks, how human-in-the-loop design prevents unintended autonomous actions, and how observability and audit trail design create the accountability structures that regulated domains require.

These three systems are not separate — they are the same clinical AI platform built layer by layer. ChestScan provides the imaging analysis. MedChat provides the knowledge retrieval and conversational interface. MedAgent orchestrates both into autonomous clinical workflows. By the end of Chapter 24, you will have seen a complete SE4AI system from first principles, and you will have the engineering vocabulary to reason about the systems you will build in your own careers.

---

### Review Questions

1. Andrej Karpathy described Software 2.0 as a shift in who "writes" the program. Using the Obermeyer et al. healthcare algorithm as a case study, explain what that shift means for software engineering's responsibility. What engineering practice that exists for Software 1.0 had no equivalent for the Software 2.0 system in that case, and what should it have been?

2. A colleague argues that a well-written unit test suite is sufficient quality assurance for an AI system: "if the model passes all the tests, it's good to ship." Identify two specific properties of AI systems that make this argument fail, and describe what additional quality assurance each property requires.

3. You are joining a team that has just deployed its first production machine learning model. The team has no MLOps practices in place: no experiment tracking, no model registry, no production monitoring. The model is performing well. Prioritise the three most important MLOps practices to introduce first, and justify your ranking. What specific failure does each practice prevent?

4. Describe the difference in risk profile between a Software 2.0 error, a Software 3.0 error, and a Software 4.0 error, using a medical domain example for each. How does the appropriate engineering response differ across the three generations?

5. An organisation is building a clinical decision support system that combines a trained imaging classifier, an LLM-based report summariser, and an autonomous agent that books follow-up appointments. Map each component to its SE4AI sub-discipline and describe the single most important engineering practice each component requires that the others do not share.

6. The SE4AI lifecycle is described as a loop, not a pipeline. Explain what happens if the production monitoring stage is omitted. Give a specific example of a failure mode that would be invisible without monitoring but would be detected by a correctly configured monitoring system.

---
