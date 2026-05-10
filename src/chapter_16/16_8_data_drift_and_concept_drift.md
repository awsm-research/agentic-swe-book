## 16.8 Data Drift and Concept Drift

---

The language of drift in ML monitoring distinguishes between two fundamentally different failure modes that require different detection approaches and different responses.

### 16.8.1 Data Drift

Data drift — also called covariate shift in the statistical literature — occurs when the distribution of input features in production changes relative to the distribution the model was trained on. The relationship between features and labels is assumed to remain the same; only the inputs have changed.

For the ChestScan application, data drift might arise from a change in imaging equipment. A hospital upgrades its X-ray machine, and the new machine produces images with different contrast characteristics, different noise profiles, or a different spatial resolution. The patients presenting with pneumonia are the same; the features the model uses to identify pneumonia are the same; but the pixel distributions the model receives no longer match the distributions it was trained on. The model's performance degrades not because the task has changed, but because the representation of the task has changed.

Data drift also arises from demographic shifts. If the deployment context expands — from paediatric patients to adult patients, or from one clinical centre to multiple centres with different imaging protocols — the inputs the model receives will differ systematically from its training distribution. These shifts may be deliberate (expanding the scope of the application) or incidental (a change in referral patterns). Either way, the model was not designed for the new distribution, and its performance on that distribution is unknown.

Detecting data drift requires monitoring the statistical properties of the inputs and comparing them to a baseline established from the training data. Common approaches include the Kolmogorov-Smirnov test for continuous distributions, the chi-squared test for categorical distributions, and the Population Stability Index for overall distribution shift.

### 16.8.2 Concept Drift

Concept drift occurs when the relationship between inputs and the correct output changes. The input distribution may be unchanged, but the label that should be assigned to a given input is different. This is a more serious failure mode than data drift because it cannot be resolved by retraining on more data from the same distribution — the distribution itself has become misaligned with the task.

For the ChestScan application, concept drift might arise from a change in clinical definition. If the diagnostic criteria for bacterial versus viral pneumonia are revised — for example, following the emergence of a new pathogen that produces radiographic presentations that straddle the existing categories — the model's learned decision boundary may no longer correspond to the clinically correct boundary. Images that the model confidently classifies as bacterial pneumonia may now be correctly classified as viral by updated clinical standards.

Concept drift can also arise from more subtle processes. If clinicians begin ordering chest X-rays under different conditions — earlier in the disease course, from asymptomatic contacts, or as a screening rather than diagnostic tool — the case mix changes in ways that may not be reflected in the input distribution but affect the correct classification.

Detecting concept drift in the absence of ground truth labels is genuinely difficult. The most direct approach is to collect ground truth labels for a sample of production predictions — ideally through a structured feedback loop in which clinicians can confirm or correct the model's output — and compute performance metrics on that sample. If performance metrics are unavailable, changes in prediction confidence distributions may serve as a proxy: a model whose average confidence on correctly classified inputs is declining may be encountering inputs that are closer to its decision boundary, which can indicate concept drift.

### 16.8.3 Population Shift

Population shift — also called prior probability shift — is a third failure mode distinct from both data drift and concept drift. The relationship between features and labels is unchanged. The feature distribution is unchanged. But the prevalence of each class in the production population has changed.

If a respiratory illness outbreak increases the prevalence of viral pneumonia from its training-set rate of approximately 25% to 60% of presenting cases, a model calibrated on the original prevalence will produce confidence scores that are miscalibrated to the new prevalence. A predicted probability of 0.7 for viral pneumonia that was appropriate in the original class distribution may substantially understate the posterior probability in the new distribution, because the prior has changed. Monitoring prediction class distribution against the training baseline detects this shift directly.

---
