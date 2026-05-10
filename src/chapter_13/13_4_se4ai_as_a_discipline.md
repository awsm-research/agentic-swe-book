## 13.4 SE4AI as a Discipline

SE4AI — Software Engineering for AI — is the application of engineering rigour to the full lifecycle of AI systems. It is not a new field; it is an extension of software engineering into territory that software engineering was not originally designed for.

### 13.4.1 What SE4AI Inherits

SE4AI does not start from scratch. The foundational principles of software engineering — modularity, separation of concerns, version control, automated testing, code review, continuous integration — apply to AI systems as much as to traditional software. The code that implements a data pipeline, a model training script, a serving API, or an agent orchestrator is still code. It should be reviewed, tested, and version-controlled using the same practices described in Part I and Part II of this book.

SE4AI also inherits software engineering's ethical framework: the obligation to build systems that do not cause harm, to be transparent about what systems can and cannot do, and to maintain accountability for decisions that affect users. Chapter 12 covered these obligations in the context of traditional software. SE4AI extends them into contexts where the stakes are often higher and the failure modes are less visible.

### 13.4.2 What SE4AI Adds

Beyond its inheritance, SE4AI introduces practices that have no equivalent in traditional software engineering:

**Data versioning and lineage**: The system's behaviour depends on the data it was trained on. SE4AI requires that data be versioned, its provenance documented, and its relationship to model versions recorded. A model trained on version 2.1 of the dataset is a different system from the same code trained on version 2.2 — and both should be traceable.

**Experiment tracking**: ML development is inherently experimental. You run many configurations, compare their results, and select the best one. Traditional software development does not have this structure — you do not typically compare twenty different implementations of the same function and pick the one with the best benchmark score. SE4AI requires infrastructure for recording, comparing, and auditing experiments.

**Behavioural evaluation**: AI system quality cannot be assessed by passing a test suite. It must be assessed through behavioural evaluation — running the system on carefully constructed input sets, measuring performance across demographic subgroups, testing adversarial inputs, and evaluating outputs using metrics that capture the properties that actually matter for the use case.

**Distributional monitoring**: AI systems can fail silently in production when the input distribution shifts. SE4AI requires monitoring infrastructure that detects these shifts and triggers intervention before user-facing quality degrades.

**Human-in-the-loop governance**: For consequential decisions — clinical recommendations, financial transactions, legal judgements — SE4AI requires explicit mechanisms for keeping humans in the decision loop. This is not a UX requirement; it is an engineering requirement with implications for system architecture, audit trail design, and approval workflow implementation.

### 13.4.3 The Scope of SE4AI

SE4AI covers the full lifecycle of an AI system, from data engineering through production monitoring. It is organised into three sub-disciplines, each addressing a different generation of AI system:

**MLOps** addresses Software 2.0 systems: systems where the core intelligence is a trained model. Its concerns are data pipelines, experiment tracking, model evaluation, model registry, and production serving and monitoring.

**LLMOps** addresses Software 3.0 systems: systems where the core intelligence is a foundation model accessed through an API. Its concerns are prompt engineering, RAG pipeline design, LLM evaluation, cost engineering, and safety guardrails.

**AgentOps** addresses Software 4.0 systems: systems where the core intelligence is an autonomous agent that takes actions. Its concerns are agent design, tool safety, human-in-the-loop workflows, observability, and audit trail design.

These three sub-disciplines are not sequential stages — they are parallel specialisations that may all apply to a single system. An AI-powered clinical decision support system might use a trained model for imaging analysis (MLOps), a language model for clinical note summarisation (LLMOps), and an autonomous agent for care pathway orchestration (AgentOps). Understanding all three is increasingly necessary for anyone building production AI systems.

---
