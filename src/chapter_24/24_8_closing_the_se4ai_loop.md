## 24.8 Closing the SE4AI Loop

---

Chapter 13 introduced the SE4AI lifecycle as a loop, not a pipeline: a circular structure connecting data engineering through experiment tracking, model evaluation, governance review, model serving, production monitoring, and retraining, each stage feeding back into the next. It described three sub-disciplines — MLOps, LLMOps, and AgentOps — as parallel specialisations addressing three generations of AI systems. This final chapter closes that loop.

The loop from Chapter 13 bears repeating, because this chapter represents the closing of it:

Data Engineering produces versioned, validated training data with documented provenance. Without this, no model's behaviour is reproducible or auditable.

Experiment Tracking produces a complete record of every training run, enabling the reproduction of the model that is actually in production and the explanation of why it performs as it does.

Model Evaluation produces a gate: a documented decision that this model meets the quality bar for deployment, supported by stratified performance metrics and a comparison against the current production model.

Governance Review is the human checkpoint before production deployment — the clinical lead or compliance officer who reviews the evaluation report and makes a decision. In regulated domains, this step is not optional, and the decision must be signed and retained.

Model Serving makes the model's capabilities available through a versioned API, with the preprocessing applied at serving time matching the preprocessing applied at training time.

Production Monitoring observes the model's behaviour in production, detecting distribution shift and performance degradation before users bear the consequences.

Retraining closes the loop: when monitoring signals degrade, new data is incorporated, a new model is trained, and the loop runs again.

AgentOps — the layer this book's final chapters have demonstrated — sits above this loop, coordinating the agent's actions against the outputs of the MLOps and LLMOps layers below. The agent calls the imaging model endpoint built in Chapters 14–16. It retrieves from the vector index built in Chapter 17. It reasons with the LLM governed by the prompt management and evaluation framework of Chapters 18–21. And it acts — but only through the safety and governance controls that make those actions accountable.

### 24.8.1 What the SE4AI Discipline Still Lacks

The SE4AI field is not mature. Its practices are still being established, and significant open problems remain. Intellectual honesty about these open problems is itself a governance practice — overstating the discipline's maturity is a form of risk concealment.

Agent evaluation is the most significant gap. The evaluation frameworks described in this book — RAGAS for RAG systems, scenario-based evaluation for agents — provide useful signal, but they do not reliably predict agent behaviour in production for novel inputs. The input space of a clinical agent is effectively unbounded, and the test suites that can be constructed before deployment are necessarily finite. The gap between evaluation performance and production performance is structural, not fixable by adding more test cases. The field lacks a principled theory of agent evaluation coverage that is equivalent to code coverage in traditional software testing.

Trust calibration is a related open problem. A human-in-the-loop approval workflow works as a safety control only if the human reviewer actually reviews the proposed action. Automation bias — the tendency to approve AI-proposed actions without adequate scrutiny, particularly when the system has a strong prior track record — is a well-documented phenomenon in human factors research. The engineering controls described in this chapter prevent the agent from acting without human approval; they do not prevent the human from approving without genuine consideration. The design of interfaces and workflows that promote genuine human review, rather than reflexive approval, is a human factors problem that the engineering discipline has not yet solved.

Autonomous system governance at scale is the third open problem. The governance controls described in this chapter are designed for systems that operate in a single regulated domain with a defined set of tools and a human reviewer in the loop for irreversible actions. The governance of systems that operate across multiple domains, with dynamically composed tool sets, at a scale where human review of individual actions is not feasible, is an unsolved engineering and policy problem. The frameworks are emerging — the EU AI Act provides a regulatory structure, and technical standards bodies are developing conformity assessment frameworks — but the practical engineering discipline for governing autonomous systems at scale does not yet exist in mature form.

These open problems are not reasons to avoid deploying agentic systems. They are reasons to deploy them with epistemic humility: clear about what the current controls do and do not provide, committed to monitoring for the failure modes that current evaluation cannot detect, and structured to incorporate improvements as the discipline matures.

---
