## 14.4 Data Splitting and Leakage

The split strategy is the single data engineering decision with the largest direct impact on whether a production ML application performs as its evaluation claims.

### 14.4.1 Random Splitting and Its Failure Mode

The simplest split strategy is random: shuffle all examples and assign them to train, validation, and test partitions by proportion. For many applications, this is appropriate. The assumption it makes is that all examples are independent — that knowing any one example gives you no information about any other. This assumption fails in medical imaging.

A patient who has had multiple chest X-rays taken — on different days, from slightly different angles, with different positioning — contributes multiple images to the dataset. Random splitting distributes those images across partitions. The model then trains on images from patients who also appear in the test set. It learns to recognise patient-specific anatomy — ribcage geometry, lung density patterns, cardiac silhouette shape — rather than disease-specific pathology. Evaluated performance is inflated by this patient memorisation, and the inflation is invisible in the metric.

### 14.4.2 Patient-Level Splitting

Patient-level splitting corrects this by treating the patient as the unit of partitioning. All images from a patient go to exactly one partition. This ensures that test performance reflects genuine generalisation to unseen patients — the condition the application will face in production.

The Kaggle Chest X-Ray dataset was distributed as pre-partitioned train/, val/, and test/ directories, designed to reflect patient-level separation. Using this structure directly is the correct engineering choice. Re-splitting the data randomly — even with the intention of creating a larger validation set — destroys the patient-level guarantee unless the patient identifier embedded in each filename is used to preserve patient-level assignment throughout.

### 14.4.3 Temporal Splitting

For applications operating in changing environments, temporal leakage is a second concern. If training data includes examples from after the test period, the model incorporates information about future patterns during training. Temporal splitting assigns examples to partitions based on collection date, preserving the chronological separation between training and evaluation that reflects real deployment conditions.

### 14.4.4 The Production Consequence

The production consequence of leakage is a systematically overconfident application. The evaluation says it performs well; production reveals it does not. In a clinical setting, this gap manifests as diagnostic errors on patients the application was supposed to help. No architecture change fixes an evaluation designed to succeed on leaked data. The model performs exactly as trained — the evaluation was wrong.

---
