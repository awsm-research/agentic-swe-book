## 14.3 Dataset Quality Dimensions

Data quality is not a single property — it is a family of properties, each of which can fail independently and each of which has distinct consequences for the ML application built on it.

**Validity** is the degree to which data conforms to defined rules and constraints. An image with a corrupt header is invalid. A label that assigns a patient to two mutually exclusive classes is invalid. Validity is the easiest dimension to check programmatically and is the most commonly monitored.

**Accuracy** is the degree to which data correctly represents the real-world entity it describes. A chest X-ray correctly identified as showing bacterial pneumonia is accurate. One mislabelled as normal is inaccurate. Accuracy cannot be verified purely programmatically — it requires expert review of a sampled subset. The accuracy of the labelling process is the single most important quality dimension for supervised learning applications, because it determines the ceiling on what the model can learn.

**Completeness** is the degree to which required data is present. In imaging datasets, completeness failures often manifest as missing metadata rather than missing images: a patient record without an age field, or a pneumonia case without a subtype label. Incomplete metadata limits the evaluation analyses that can be performed — if age is missing, age-stratified performance analysis is impossible.

**Consistency** is the degree to which data is free of contradictions within and across the dataset. Inconsistency arises when the same labelling guideline is applied differently by different annotators, at different times, or with different reference materials. In the Kaggle dataset, the bacterial/viral distinction is encoded in the filename prefix rather than in a structured label field — a consistency risk that requires explicit handling in the preprocessing pipeline and documentation in the datasheet.

**Timeliness** is the degree to which data reflects the current state of the world it was sampled from. A model built on chest X-rays collected in 2015 may not reflect the imaging protocols, patient demographics, or disease patterns of 2025. Timeliness failures are particularly dangerous because they produce gradual, silent degradation: the application continues to generate predictions, but those predictions become progressively less reliable as the distribution it was built on diverges from the distribution it is operating in.

---
