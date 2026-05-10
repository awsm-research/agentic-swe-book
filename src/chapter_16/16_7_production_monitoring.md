## 16.7 Production Monitoring

---

A deployed model that is not monitored is a system that degrades without warning. The performance metrics computed during evaluation — AUC, precision, recall, F1 — are measurements on a fixed test set at a fixed point in time. Production data is not fixed. It changes as populations shift, equipment is upgraded, usage patterns evolve, and the world the model was trained to represent moves on. Monitoring is the engineering practice that connects the static snapshot of evaluation to the continuous reality of deployment.

### 16.7.1 What to Monitor

Production monitoring for ML systems divides into three categories of signal, each providing information that the others cannot substitute.

**Input distribution monitoring** tracks the statistical properties of the data the model is receiving at serving time. For image-based applications, this includes pixel intensity distributions, image dimensions, aspect ratios, and file format characteristics. Shifts in input distribution indicate that the data arriving in production is changing — which may or may not affect model performance, but always warrants investigation.

**Prediction distribution monitoring** tracks the distribution of the model's outputs. What fraction of requests are classified into each class? How does that fraction compare to the training set class distribution? Is the distribution of confidence scores shifting over time? A model that was calibrated to predict pneumonia in roughly 73% of cases (matching the training set prevalence) but is now predicting pneumonia in 95% of cases is exhibiting a prediction distribution shift. Whether this reflects a genuine change in the patient population or a degradation in the model's calibration cannot be determined from the prediction distribution alone — but the shift is the signal that investigation is needed.

**Performance metric monitoring** tracks the accuracy, precision, recall, and other quality metrics of the model's predictions relative to ground truth labels. This is the most direct signal of model degradation, and the most difficult to obtain in practice: ground truth labels are often not available at serving time, because the correct label for a prediction may only be known days, weeks, or months later (after a clinical test, a transaction resolution, or an outcome measurement). Where ground truth labels are available — even for a sample of predictions — they should be used.

### 16.7.2 Operational Metrics

Alongside the ML-specific signals, operational metrics apply to every production service: request rate (how many predictions per second is the system handling?), error rate (what fraction of requests result in an error response?), latency (how long does the prediction endpoint take to respond at the median and 99th percentile?), and resource utilisation (CPU, memory, GPU VRAM).

Operational metrics tell you whether the service is up; they cannot tell you whether the model is right. A system can be operationally healthy — all requests completing successfully, latency within bounds, resources within capacity — while the model is producing systematically incorrect predictions due to input distribution shift. Conversely, a system can exhibit degraded operational metrics due to infrastructure issues that have nothing to do with the model. A team running only operational monitoring will miss a model that is healthy at the infrastructure layer and systematically wrong at the prediction layer.

---
