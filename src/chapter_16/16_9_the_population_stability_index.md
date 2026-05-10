## 16.9 The Population Stability Index

---

The Population Stability Index (PSI) is a metric for quantifying how much a distribution has shifted between a reference period and a current period. It was developed in the credit risk industry to monitor the stability of scorecard populations over time, and it has become widely adopted in ML monitoring because it provides a single interpretable number that summarises the magnitude of a distribution shift and maps to agreed-upon action thresholds.

### 16.9.1 How PSI Works

To compute PSI, both the reference distribution and the current distribution are divided into a set of bins — typically ten or twenty. For each bin, the fraction of observations falling into that bin is computed for both distributions. The PSI is then:

$$\text{PSI} = \sum_{i=1}^{n} \left( A_i - E_i \right) \times \ln\!\left(\frac{A_i}{E_i}\right)$$

where *Aᵢ* is the actual (current) proportion in bin *i* and *Eᵢ* is the expected (reference) proportion. This weighting has an important property: bins where one distribution has far more observations than the other contribute more to the PSI than bins where the distributions are similar, and the contribution grows superlinearly with the degree of divergence. A distribution where one bin has shifted from 10% to 1% contributes more to the PSI than one where a bin has shifted from 10% to 9%.

For prediction class distributions — where the categories are discrete rather than continuous — PSI is computed directly on class proportions without binning. The reference proportions come from the training dataset class distribution, and the actual proportions come from the production predictions in the monitoring window.

### 16.9.2 Interpreting PSI

The standard PSI thresholds, established by convention in the credit industry and adopted broadly in ML monitoring practice, are:

| PSI Range | Interpretation | Recommended Action |
|---|---|---|
| Below 0.1 | No significant shift | Continue routine monitoring |
| 0.1 to 0.2 | Moderate shift | Investigate the source of the shift; increase monitoring frequency |
| Above 0.2 | Significant shift | Retraining evaluation is warranted; treat current predictions with reduced confidence |

These thresholds are heuristics, not physical laws. A PSI of 0.21 is not categorically different from a PSI of 0.19. The thresholds provide a common vocabulary for operationalising drift alerts, not a precise characterisation of when model performance degrades.

### 16.9.3 Limitations of PSI

PSI has three practical limitations that a production monitoring system must account for.

**Sample size dependence.** PSI computed on a small number of observations is unreliable. With fewer than one hundred observations in the current distribution, the bin proportions are dominated by sampling noise, and PSI values can fluctuate above the alert threshold for reasons unrelated to any genuine distribution shift. Monitoring systems should require a minimum sample count — typically one hundred observations in the monitoring window — before computing and acting on PSI.

**Insensitivity to the source of shift.** PSI quantifies how much a distribution has shifted, but not what caused the shift or what its practical consequences are. A PSI of 0.3 computed on prediction confidence scores may indicate a population shift, a genuine improvement in the model's calibration, or a systematic preprocessing error. The PSI value triggers investigation; it does not conclude it.

**Dependence on bin boundaries.** For continuous distributions, the PSI value depends on how the bins are defined. Different bin widths and different numbers of bins produce different PSI values for the same pair of distributions. Bin boundaries should be established from the reference distribution and held fixed for all subsequent monitoring periods to ensure comparability over time.

---
