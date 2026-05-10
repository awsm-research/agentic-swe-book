## 15.3 Confusion Matrices and Per-Class Performance

---

A *confusion matrix* is the foundational diagnostic tool for understanding what an aggregate metric conceals. For a binary classifier, it records four counts: true positives (the model correctly predicted the positive class), true negatives (the model correctly predicted the negative class), false positives (the model predicted positive when the truth was negative), and false negatives (the model predicted negative when the truth was positive). Every aggregate metric — accuracy, precision, recall, F1, AUC — is a function of these four values. The confusion matrix reveals the raw structure beneath the aggregation.

For ChestScan, examining the confusion matrix separates two failure modes that aggregate metrics conflate. A model that achieves 0.91 AUC might produce a confusion matrix revealing that its 9% error rate is distributed as 2% false negatives and 7% false positives. Alternatively — same AUC, different matrix — it might distribute errors as 7% false negatives and 2% false positives. In clinical terms, these are radically different models: one misses far more pneumonia cases, the other over-diagnoses far more normal patients. The AUC does not distinguish them. The confusion matrix does.

Per-class performance — computing precision and recall separately for each class and not just across the whole dataset — extends this analysis to multi-class problems. A model predicting across bacterial pneumonia, viral pneumonia, and normal may achieve 0.93 AUC overall while performing at 0.71 recall on the normal class specifically. The overall metric is buoyed by strong performance on the two pneumonia subtypes, which form the majority of the test set. The per-class view makes the weakness visible.

The engineering implication is that no model should be registered for production without a full confusion matrix and per-class precision/recall report. These are not supplementary visualisations — they are the primary evidence on which the production decision is made. An evaluation that reports only AUC is incomplete, and an evaluation gate that thresholds only on AUC will pass models that a confusion matrix would reveal as clinically unacceptable.

---
