## 13.6 The SE4AI Lifecycle

The SE4AI lifecycle is the loop that connects data to production and back again. It is not a pipeline — pipelines are linear, with a defined start and end. The SE4AI lifecycle is circular: production systems generate data that feeds back into training, and the loop runs continuously as long as the system operates.

```
Data Engineering → Experiment Tracking → Model Evaluation → Model Registry
       ↑                                                              ↓
  Retraining ← Production Monitoring ← Model Serving ← Governance Review
```

Each stage has clear engineering ownership and clear artefacts:

**Data Engineering** produces a versioned, validated dataset with documented provenance. The artefact is a dataset version with a hash fingerprint, a schema, split documentation, and quality checks. Skipping this stage means the model is trained on data of unknown quality and unknown lineage.

**Experiment Tracking** produces a complete record of every training run: hyperparameters, per-epoch metrics, artefacts, code version, environment, and data version. The artefact is a tracked run in a system like MLflow. Skipping this stage means you cannot reproduce your best model, cannot explain why it performs as it does, and cannot defend your design choices to an auditor.

**Model Evaluation** produces a decision: does this model meet the quality bar for production? This is not a metric — it is a gate. The artefact is an evaluation report: performance on a held-out test set, stratified by relevant subgroups, with explainability analysis and a comparison against the current production model. Skipping this stage means deploying models that may be worse than what they replace.

**Governance Review** (in regulated domains) is the human checkpoint before production deployment. Someone with authority over the domain — a clinical lead, a compliance officer, a product owner — reviews the evaluation report and makes a decision. The artefact is a signed approval. Skipping this stage in regulated domains is not an engineering shortcut; it is a compliance failure.

**Model Serving** makes the model's predictions available to downstream systems or users. The artefact is a deployed service with a versioned API. Skipping this stage — or treating it as a trivial deployment step — is where train/serve skew is introduced: the preprocessing applied at serving time differs from the preprocessing applied at training time, and performance degrades silently.

**Production Monitoring** observes the model's behaviour in production: input distribution statistics, prediction distribution statistics, and (where labels are available) performance metrics. The artefact is a monitoring dashboard with alerting configured on drift thresholds. Skipping this stage means you learn about model degradation from users complaining, rather than from your own instrumentation.

**Retraining** closes the loop: when monitoring detects degradation, new data is incorporated, and a new model is trained, evaluated, and deployed through the same loop. Treating retraining as a one-time event is not MLOps — it is just ML.

---
