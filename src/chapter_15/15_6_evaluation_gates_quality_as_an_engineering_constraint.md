## 15.6 Evaluation Gates: Quality as an Engineering Constraint

---

An *evaluation gate* is a defined quality threshold that a model must meet before it can advance to the next stage in the deployment lifecycle. The concept borrows from continuous integration in traditional software engineering: just as a CI pipeline blocks a code change from merging if it fails automated tests, an evaluation gate blocks a model from being registered for production if it fails defined quality criteria.

The distinction between a metric and a gate is consequential. A metric is descriptive — it tells you how the model performed. A gate is prescriptive — it tells you whether the model is acceptable. A team that tracks AUC but has no gate is measuring; a team that requires AUC ≥ 0.90 before registration is governing. The difference is whether the evaluation result can be argued away.

For ChestScan, the evaluation gate defines criteria across multiple dimensions:

- Primary metric: AUC on the held-out test set must meet or exceed a defined threshold, compared against the currently registered production model.
- Per-class constraint: recall on the normal class must not fall below a clinically defined minimum, regardless of overall AUC.
- Calibration constraint: the calibration error across the confidence range must be within a defined tolerance.
- Regression constraint: performance must not degrade meaningfully relative to the registered champion, even if both models exceed the primary threshold.

A model that meets the primary metric but fails any constraint is blocked from registration. This is not a soft recommendation — it is an automated check in the model evaluation pipeline that returns a failure status when any criterion is unmet.

The regression constraint deserves particular attention. A new model that achieves modestly higher overall AUC but shows degraded recall on the normal class relative to the champion is not an improvement — it is a regression in a clinically critical dimension. Without an explicit regression gate, these regressions are invisible until they reach production. With the gate, they are caught at the evaluation stage, when the cost of investigation and remediation is orders of magnitude lower.

Evaluation gates also provide an audit trail. When a regulator or clinical governance committee asks how deployment decisions were made, the answer is not "the team reviewed the results and decided the model was good enough." The answer is "these criteria were defined before evaluation began, this model met all of them, and this record shows the results." That difference — between a subjective judgement and an engineering gate — is the difference between a defensible process and an auditable one.

---
