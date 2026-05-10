## 15.11 ChestScan: Bringing Evaluation, Registry, and Governance Together

---

The ChestScan pneumonia detection application provides a concrete context in which evaluation methodology, the model registry, and governance are not three separate concerns but three components of a single engineering system. This section traces the path a model takes from a completed training run to production deployment.

**Stage 1: Evaluation**

When a training run completes, the evaluation pipeline automatically retrieves the logged model artefact and evaluates it against the held-out test set. The pipeline computes AUC, per-class precision and recall, the confusion matrix, and a calibration plot. It then runs the evaluation gate: is AUC above the minimum threshold? Does recall on the normal class meet the clinical minimum? Is calibration error within tolerance? Does the model fail to regress on any dimension relative to the registered champion?

If any criterion fails, the evaluation returns a non-zero exit code, the model is not registered, and the failure reason is recorded in the experiment tracking system alongside the run metrics. The team is alerted. No human decision is required to block the model — the gate is automated.

If all criteria pass, the evaluation pipeline logs the evaluation report as an artefact, attaches a tag to the run marking it as gate-passed, and registers the model as a new version in the registry under the name `ChestScan-PneumoniaDetector` with lifecycle stage None.

**Stage 2: Clinical Review**

The clinical lead is notified of the new registry version. They access the evaluation report — AUC, confusion matrix, per-class metrics, calibration plot — and the model card draft, which is populated automatically from the run metadata. They examine Grad-CAM maps generated on a stratified sample of test examples: correctly classified normal cases, correctly classified pneumonia cases, and misclassified examples from each class.

If the maps show that the model attends to lung fields on pneumonia cases and to the absence of opacity on normal cases, this is consistent with expected clinical reasoning. If maps on misclassified cases show attention to imaging artefacts or the border of the image rather than the lung field, the clinical lead flags this as a concern and requests investigation before promotion.

Assuming the review is satisfactory, the clinical lead signs off and records their approval in the governance system with a reference to the specific registry version reviewed. The model version is promoted to Staging.

**Stage 3: Staging Validation**

The model in Staging is deployed to a pre-production environment that receives a replay of recent production traffic — not live patient data, but a representative sample processed through the full serving pipeline. The staging environment runs for a defined period, collecting latency, throughput, and output distribution statistics. Any train/serve skew — divergence between predictions in the training evaluation and predictions in the serving environment — would manifest here as an output distribution anomaly.

If staging validation passes, the technical governance review is completed: the security configuration is checked, monitoring alert thresholds are verified against the defined evaluation gate thresholds, and the rollback procedure is tested against the current champion.

**Stage 4: Production Promotion**

The clinical lead and technical lead jointly approve production promotion. The governance system records this approval — who approved, what evidence was reviewed, what version was approved, and when. The `@champion` alias is transferred to the new version. The serving infrastructure loads the new model on its next request. Monitoring begins recording its production behaviour against the same metric thresholds used in the evaluation gate.

**Stage 5: Continuous Monitoring**

Production monitoring is not a separate concern — it is the evaluation gate running continuously against production data. If recall on the normal class falls below the defined minimum in a rolling production window, an alert fires, the clinical lead is notified, and the team investigates. If the decline is persistent and the cause is distributional shift — a new imaging protocol introduced at a hospital site, a seasonal change in disease prevalence — retraining is triggered and the cycle begins again.

Governance here is a continuous property of the production system, not a one-time pre-deployment checkpoint — maintained automatically by the evaluation gate, the registry, and the monitoring infrastructure, with human review at the points where human judgement adds value that automation cannot replicate.

---
