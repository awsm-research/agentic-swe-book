## 15.4 Calibration: When Confidence Misleads

---

A model's output is typically a probability — a number between 0 and 1 representing the model's confidence that the input belongs to a particular class. The clinical use of this probability depends entirely on whether that confidence is meaningful. *Calibration* measures the degree to which a model's expressed confidence corresponds to its actual accuracy.

A perfectly calibrated model has the following property: across all inputs where the model predicts a 70% probability of pneumonia, approximately 70% of those patients actually have pneumonia. A poorly calibrated model might assign 70% confidence while being correct only 45% of the time — or 90% of the time. In both cases, the model's numerical output is a misleading signal for any downstream system that treats it as a probability.

This matters clinically because the threshold used to convert a model's output into a binary decision — flag or do not flag — is typically chosen with the assumption that the model's output is a probability. If the model is systematically overconfident, the chosen threshold will be too permissive, generating more false positives than intended. If it is underconfident, the threshold will be too restrictive, missing cases that should be flagged.

The standard diagnostic for calibration is a *calibration plot* — sometimes called a reliability diagram — which bins the model's predictions by confidence interval and plots the mean predicted probability against the actual positive rate within each bin. A perfectly calibrated model produces a diagonal line. Deviations above the diagonal indicate underconfidence; deviations below indicate overconfidence. Deep neural networks trained with cross-entropy loss are well-documented to be systematically overconfident: they assign higher probabilities to their predictions than their actual accuracy justifies (Guo et al., 2017). This is not a property of a specific architecture; it appears to be a consequence of the training objective.

Calibration is correctable after training — techniques like temperature scaling or isotonic regression adjust the raw model outputs to bring them into alignment with observed accuracy — but only if calibration has been evaluated in the first place. A model evaluation that measures only AUC and F1 has no visibility into whether the model's output can be trusted as a probability, and a clinical decision support system built on top of an uncalibrated model is making decisions on the basis of numerically meaningless confidence scores.

---
