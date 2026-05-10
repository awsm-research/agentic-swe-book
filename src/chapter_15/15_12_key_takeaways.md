## 15.12 Key Takeaways

1. **Accuracy is the wrong metric for imbalanced clinical datasets.** A model that predicts the majority class for all inputs achieves high accuracy while being clinically useless. AUC, per-class recall, and F1 encode the properties that accuracy obscures.

2. **Aggregate metrics hide subgroup failures.** A confusion matrix and per-class performance report are required, not supplementary. An evaluation that reports only a single summary metric is incomplete — and in clinical settings, the gaps it conceals may be clinically dangerous.

3. **Calibration is a separate quality requirement from discrimination.** A model can discriminate well between classes while producing confidence scores that are systematically wrong. Calibration must be evaluated independently, and uncalibrated models should not be deployed in contexts where their output probabilities are used to drive decisions.

4. **Subgroup evaluation is a quality requirement, not a fairness exercise.** Evaluating performance across demographic subgroups reveals unreliability that aggregate metrics are insensitive to. The engineering obligation is to evaluate across every subgroup that is identifiable in the data and clinically relevant to the deployment context.

5. **An evaluation gate is an engineering artefact, not a number.** A metric tells you how the model performed. An evaluation gate — defined criteria, automated checks, a pass/fail result — tells you whether the model is acceptable. The distinction is the difference between measurement and governance.

6. **Explainability tools are diagnostic, not corrective.** Grad-CAM and SHAP reveal what influenced a prediction; they do not prove the model is reasoning correctly, and they cannot substitute for rigorous quantitative evaluation. Their value is in surfacing distributional artefacts and providing evidence for clinical review.

7. **A model card is the model's engineering documentation.** It records intended use, evaluation results, limitations, and governance approvals — and travels with the model through its lifecycle. A model deployed without a model card has no documented basis for the decisions made about it.

8. **The model registry is a governance system, not a storage system.** Its value is in recording every decision about a model: what it passed, who approved it, when it was promoted, and when it was retired. This record is the evidence base that regulated deployments require.

9. **The alias pattern decouples deployment from version management.** Configuring serving infrastructure to load a named alias rather than a specific version number enables zero-downtime model updates and instant rollback without redeployment — the model management equivalent of a feature flag.

10. **Governance is an engineering discipline in regulated domains.** Clinical lead sign-off, data governance review, and technical governance review are not bureaucratic overhead — they are the human checkpoints that verify properties no automated evaluation can check. Treating them as retroactive documentation rather than pre-deployment constraints is the failure mode that the DeepMind Streams case illustrates.

---

### Review Questions

1. A colleague proposes using accuracy as the primary evaluation metric for a clinical AI classifier that predicts hospital readmission within 30 days. The positive class (readmission) represents 18% of the dataset. Construct a specific numerical example demonstrating how accuracy can mislead in this setting, and identify two metrics that would better reflect the application's clinical requirements.

2. An ML team evaluates a chest X-ray classifier and reports an AUC of 0.92 on the test set. Describe three distinct problems that this AUC value cannot reveal, and for each problem, identify the evaluation analysis that would detect it.

3. A pneumonia detection model has been in production for six months. The clinical lead raises a concern that the model appears to flag more false positives for patients under two years of age than for older children in the paediatric range. The team responds that overall precision is within the evaluation gate threshold. How would you investigate the concern, what evaluation methodology would you apply, and what outcome would justify escalating to a model update?

4. You have been asked to design the evaluation gate for a new version of the ChestScan model that adds a third output class — "uncertain, requires senior review" — in addition to pneumonia and normal. Describe the evaluation criteria you would define, explaining why each criterion is necessary and what failure mode it prevents.

5. A clinical governance committee has approved three previous versions of a pneumonia detection model. A fourth version achieves higher overall AUC but the Grad-CAM analysis shows that, for a subset of pneumonia cases, the model is attending to a text annotation burned into the image header rather than to the lung field. The quantitative evaluation gate passes. How would you handle this, what does the governance framework require, and what is the engineering response?

6. An organisation is deploying its first clinical AI system and has no formal model registry or governance process. The engineering lead proposes a lightweight alternative: the team reviews evaluation results informally, approval is verbal, and model versions are tracked in a shared spreadsheet. Describe the specific risks this approach introduces — using the evaluation gate, model registry, and governance concepts from this chapter — and propose the minimum viable governance process that would address the most critical risks.

---
