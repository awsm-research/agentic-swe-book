## 15.8 Model Cards: Engineering Documentation for AI Systems

---

A *model card* is a structured document describing a trained ML model's intended use, evaluation results, limitations, and deployment constraints. The concept was introduced by Mitchell et al. in 2019 as an engineering artefact analogous to the datasheets that accompany electronic components: standardised, machine-readable documentation that travels with the model and enables anyone who deploys or inherits it to understand what it can and cannot do.

The analogy to hardware datasheets is apt. An engineer who integrates a microprocessor into a circuit board does not need to understand how the chip was fabricated — they need to know its operating voltage range, its timing characteristics, its failure modes under thermal stress, and its compliance certifications. A model card provides the equivalent information for an ML model: what training data it was built on, under what conditions it performs reliably, where it is likely to fail, who it was intended to serve, and what evaluation evidence supports those claims.

A complete model card for ChestScan covers the following:

**Model description**: architecture (ResNet-50, fine-tuned on ImageNet weights), task (binary classification: pneumonia versus normal), training data (Kaggle Chest X-Ray Pneumonia dataset, version 2.0, content hash recorded), training environment (Python 3.10, PyTorch 2.1, NVIDIA A100).

**Intended use**: detection of pneumonia in anterior-posterior chest X-rays of paediatric patients aged one to five, intended as a clinical decision support tool to be reviewed by a qualified clinician, not for autonomous diagnostic use.

**Out-of-scope use**: adult patients, lateral chest X-ray projections, CT imaging modalities, autonomous clinical decision-making without clinician review.

**Evaluation results**: AUC on held-out test set, confusion matrix, per-class precision and recall, calibration plot, subgroup analysis by bacterial versus viral pneumonia subtype (the only demographic dimension available in the dataset).

**Known limitations**: single-centre dataset; population limited to paediatric patients from one hospital in Guangzhou; potential underperformance for patient populations with different age distributions, imaging equipment, or disease prevalence rates; no formal evaluation of performance on any adult population.

**Governance**: clinical lead sign-off recorded, date of approval, identity of approving clinician, version of the model card at time of approval.

Model cards are not marketing materials. They are engineering artefacts. The audiences for a model card include: the clinical team deploying the model, who must understand its limitations to use it appropriately; the compliance team, who must verify that the evaluation methodology satisfies regulatory requirements; and future engineers, who may inherit the system and need to understand what was built and why. A model that has no model card is a model with no documented basis for the decisions made about it — which is not a minor omission in a regulated domain.

---
