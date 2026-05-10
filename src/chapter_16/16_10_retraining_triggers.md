## 16.10 Retraining Triggers

---

Monitoring produces signals. Those signals must be connected to actions. The action most commonly associated with drift detection is retraining — returning to the beginning of the ML lifecycle with new or updated training data to produce a model that is better aligned with the current production distribution. Retraining is not always the correct response to every monitoring signal, and triggering it incorrectly wastes engineering time and introduces the risk of deploying a regression.

Three categories of retraining trigger correspond to three different conditions that monitoring may detect.

### 16.10.1 Drift-Based Triggers

A drift-based trigger fires when a monitoring metric exceeds a threshold. For the ChestScan system, the trigger fires when PSI on the prediction class distribution or the confidence distribution exceeds 0.2 over a rolling seven-day window. The trigger is automated: the drift detection script computes PSI, and if the threshold is exceeded, it notifies an engineer and initiates the retraining pipeline.

The drift-based trigger is sensitive but not specific. Not every PSI exceedance requires a full retraining cycle. A sudden PSI spike caused by an unusual week of clinical cases — a viral outbreak, a batch of unusual presentations, a referral pattern anomaly — may resolve without any model change as the population returns to its baseline. The appropriate response to a drift alert is investigation before retraining: confirm that the shift is persistent, identify its source, and determine whether retraining on the current production distribution would improve performance or merely fit the anomalous period.

### 16.10.2 Performance-Based Triggers

A performance-based trigger fires when measured model performance on production data — where ground truth labels are available — falls below the evaluation gate threshold. For the ChestScan system, this means AUC below 0.92 on a sample of predictions for which the clinical diagnosis has been confirmed.

The performance-based trigger is the most direct signal that the model has degraded below an acceptable level. It is also the most difficult to operationalise, because ground truth labels may be unavailable, delayed, or expensive to obtain. Where clinical feedback loops are in place — structured radiologist review of the model's outputs — performance-based triggers are feasible. Where they are not, drift-based triggers serve as an earlier, less specific proxy.

### 16.10.3 Time-Based Triggers

A time-based trigger fires on a schedule regardless of observed drift or measured performance. The rationale is that a model trained on data from a fixed point in time will accumulate distribution shift as the world changes, even if no individual monitoring metric exceeds its threshold on any given day. The accumulated drift may be small and gradual — below any detection threshold in any monitoring window — while still producing a meaningful degradation in performance over months.

Quarterly retraining as a baseline, regardless of observed drift, is a defensible engineering policy for a system serving a changing population in a changing clinical environment. It does not eliminate the need for drift-based or performance-based triggers; it complements them by providing a scheduled opportunity to incorporate recent data even in the absence of a specific alert.

---
