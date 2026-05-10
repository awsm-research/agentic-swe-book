## 15.5 Subgroup Evaluation: The Demographic Blind Spot

---

Aggregate metrics evaluate a model's average performance across the entire test set. They are insensitive to performance variation across identifiable subgroups — and in clinical AI, that variation is often clinically and ethically significant.

The DeepMind Streams case described at the opening of this chapter is one instance of a pattern that has been documented repeatedly. The Obermeyer et al. study of commercial healthcare algorithms found systematic underestimation of Black patients' healthcare needs. Buolamwini and Gebru's Gender Shades study (2018) found that commercial facial recognition systems had error rates up to 34 percentage points higher for darker-skinned women than for lighter-skinned men. A 2021 systematic review of chest X-ray AI models found that most published models had not been evaluated across demographic subgroups, and those that had frequently showed significant performance disparities across imaging equipment type and patient population (Roberts et al., 2021).

For ChestScan, the Kaggle Chest X-Ray dataset is collected from paediatric patients aged one to five at a single centre in Guangzhou. The dataset does not include sufficient demographic metadata to support full subgroup analysis by sex, age band within the paediatric range, or disease severity. This is itself a documented limitation: the evaluation framework can only detect performance disparities along dimensions that are recorded in the data. What cannot be measured cannot be monitored.

The engineering requirement is to evaluate performance separately for every subgroup that is identifiable in the data and clinically relevant. For a clinical imaging application, relevant subgroups typically include age band, sex, imaging equipment type, and clinical presentation severity. Within each subgroup, compute the full suite of metrics — not just accuracy, but precision, recall, and calibration. Where sample sizes are too small for reliable estimates, document the limitation explicitly rather than treating the absence of evidence as evidence of absence.

Subgroup evaluation is a quality assurance requirement. The fairness framing is secondary; the practical consequence is more direct: a model whose overall recall is 0.92 but whose recall for a specific demographic subgroup is 0.61 is unreliable for that population — and that population will encounter it in production. Documenting the gap as a known limitation does not make the model acceptable; it makes the risk visible so that a deployment decision can be made with full information.

---
