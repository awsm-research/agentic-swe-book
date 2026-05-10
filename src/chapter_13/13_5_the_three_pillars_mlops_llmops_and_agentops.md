## 13.5 The Three Pillars: MLOps, LLMOps, and AgentOps

### 13.5.1 MLOps

MLOps emerged from the recognition that deploying a machine learning model is not the same as deploying software, and that the practices that work for software deployment do not transfer cleanly. The term was formalised in industry between 2018 and 2019, building on infrastructure practices documented in Google's seminal "Hidden Technical Debt in Machine Learning Systems" paper, which established the conceptual foundation (Sculley et al., 2015).

MLOps provides practices and tooling for: reproducible data pipelines, experiment tracking (logging parameters, metrics, and artifacts for every training run), model evaluation against defined quality thresholds, model registration and versioning, and production serving with monitoring. The MLflow platform — covered in Chapters 14 and 16 of this book — implements these practices in an open-source, vendor-neutral way.

The central insight of MLOps is that the trained model is an artifact of a process, and that artifact's quality depends on every step of the process that produced it. You cannot trust a model whose training data, preprocessing choices, hyperparameters, and evaluation methodology are not fully recorded. MLOps provides the discipline to record all of them.

### 13.5.2 LLMOps

LLMOps is a younger discipline, emerging rapidly after 2022 with the widespread adoption of foundation models in production systems. It addresses the engineering challenges specific to applications built on large language models: systems that are defined primarily by their prompt and retrieval design rather than by trained model weights.

Where MLOps is primarily concerned with training and evaluation, LLMOps is primarily concerned with the application layer — the stack that sits between the foundation model and the end user. This stack is more complex than it initially appears: prompts must be versioned and tested, retrieval indexes must be built and maintained, model outputs must be evaluated for quality and safety, serving costs must be controlled at scale, and guardrails must prevent the system from producing harmful or incorrect outputs.

The tools of LLMOps — RAG frameworks, prompt regression test suites, LLM evaluation libraries like RAGAS, unified serving gateways like LiteLLM — are newer and less standardised than their MLOps counterparts. The practices are still being established. Teams that treat prompt management as informal risk undetected prompt regressions, runaway inference costs, and safety failures that no monitoring catches.

### 13.5.3 AgentOps

AgentOps is the newest of the three, and its practices are the least settled. The challenge is that autonomous agents introduce a category of risk that MLOps and LLMOps do not address: irreversible real-world actions. A classification model that makes an error produces a wrong label. An LLM application that hallucinates produces a wrong string. An agent that makes an error may send an email, delete a file, execute a transaction, or take a clinical action that cannot be undone.

AgentOps provides the engineering practices to manage this risk: tool design with explicit safety constraints, human-in-the-loop workflows for consequential actions, distributed tracing to reconstruct what an agent did and why, circuit breakers to halt runaway agent loops, append-only audit logs to create accountability, and red teaming methodologies to surface failure modes before deployment.

The frameworks for AgentOps — LangGraph for agent state management, LangSmith for tracing, OpenTelemetry for observability — are available, but the engineering discipline around their use is still emerging. Part VI of this book provides one structured approach.

### 13.5.4 How the Three Pillars Relate

MLOps, LLMOps, and AgentOps address different layers of the AI stack, and in complex systems, all three may be active simultaneously. The relationship is not hierarchical — one is not a prerequisite for the others — but they share common concerns that express themselves differently in each context:

| Concern | MLOps | LLMOps | AgentOps |
|---|---|---|---|
| Versioning | Dataset + model weights | Prompt + retrieval index | Agent graph + tool definitions |
| Testing | Metric thresholds on test set | Prompt regression tests | Scenario-based agent evaluation |
| Monitoring | Input distribution + model performance | Output quality + cost per query | Action frequency + failure rate |
| Rollback | Load previous model version | Revert prompt to previous version | Disable tool or agent route |
| Governance | Model card + approval gate | Safety guardrails + human review | Approval workflows + audit log |

The experiment tracking insight from MLOps — log everything, before you need it — applies directly to prompt versioning in LLMOps. The circuit breaker pattern from software reliability engineering applies directly to agent loop management in AgentOps.

---
