## 16.12 Key Takeaways

---

1. **A registered model is not a production system.** The gap between a trained artefact and a reliable serving system includes model loading, input validation, preprocessing replication, health monitoring, update mechanisms, and drift detection. Each element must be explicitly engineered.

2. **Batch inference and online inference are distinct architectural patterns.** The choice between them is driven by latency requirements, throughput characteristics, and whether predictions can be computed in advance. Online inference requires a persistent serving process; batch inference is a scheduled pipeline.

3. **Train/serve skew is self-inflicted and preventable.** Duplicating preprocessing code between training and serving pipelines creates the conditions for train/serve skew. The correct response is a shared module imported by both, not an attempt to keep two implementations synchronised.

4. **ML serving containers have specific requirements.** Model weights should not be baked into the image. GPU access requires explicit configuration at every layer of the stack. Multi-stage builds separate build-time and runtime dependencies. Non-root execution is a baseline security requirement.

5. **The three-tier architecture separates concerns.** Frontend handles presentation, the backend API handles validation and model invocation, and the model serving tier handles the model lifecycle. Each tier can be updated, scaled, and replaced independently.

6. **The `@champion` alias decouples serving from versioning.** Loading a model by alias rather than version number enables zero-downtime model updates and staged rollouts without any change to serving infrastructure or application code.

7. **Data drift and concept drift are different failure modes requiring different responses.** Data drift means the inputs have changed; concept drift means the relationship between inputs and labels has changed. Monitoring the input distribution detects the former; monitoring performance on labelled production samples detects the latter.

8. **PSI quantifies distribution shift but does not explain it.** PSI above 0.2 is a signal to investigate, not a conclusion. The investigation must identify the source of the shift and determine whether retraining is the appropriate response.

9. **Retraining triggers fall into three categories.** Drift-based triggers catch fast shifts; time-based triggers catch the slow accumulation that falls below any single-window detection threshold; performance-based triggers catch what both miss — degradation that is visible only in labelled outcomes.

10. **The reference distribution for monitoring must match the deployment population.** Using a training dataset's class distribution as a monitoring baseline is appropriate only when the deployment population matches the training population. A deployment-specific baseline, established from early production data, is more reliable for systems serving populations that differ from the training distribution.

---

### Review Questions

---

1. A hospital deploys ChestScan to support a general adult radiology department, whereas the training data was drawn entirely from a paediatric population aged one to five years. Describe two specific ways this mismatch could manifest in production monitoring signals, distinguish between the drift types involved, and explain what investigation should follow before retraining is authorised.

2. A team builds a model serving API that loads the model from disk at application startup and processes ten concurrent requests per second. Six months after deployment, the API begins responding with latency spikes at the 99th percentile. The team traces the issue to the model being reloaded from disk on every fifth request, because a new developer added a model loading call inside the prediction handler instead of using the singleton. Identify the architectural principle that was violated, describe how the singleton pattern prevents this class of failure, and explain what additional monitoring signal would have detected the problem earlier.

3. The drift detection script for ChestScan is scheduled to run daily. One morning it reports PSI of 0.31 on the prediction class distribution, triggered by a three-day window during which 94% of predictions were classified as bacterial pneumonia (the training baseline is 47.5%). The team immediately initiates a retraining cycle. Describe two alternative explanations for this PSI value that do not represent model degradation, explain why the immediate retraining decision may have been premature, and propose a more structured investigation protocol for this type of alert.

4. A colleague argues that the `@champion` alias pattern adds unnecessary complexity — the team could simply update an environment variable in the deployment configuration to point to a new model URI whenever a model is updated. Compare these two approaches across the dimensions of auditability, downtime risk, rollback capability, and governance, and explain why the alias pattern is the superior choice for a clinical decision support application.

5. An organisation is designing a production monitoring system for a credit risk scoring model. Ground truth labels — whether a loan actually defaults — are available, but only twelve to eighteen months after the loan is issued. Propose a monitoring strategy that uses PSI to detect distribution shift in the shorter term while incorporating performance-based triggers over the longer term, and explain how the organisation should calibrate its retraining thresholds given this label lag.

6. The ChestScan serving API logs each prediction to MLflow. A new requirement asks that the logging be made synchronous — the prediction response should not be returned until the log write has confirmed success. Evaluate this requirement: what reliability guarantee does synchronous logging provide, what latency and availability risk does it introduce, and under what circumstances would the trade-off be justified?

---
