## 14.1 Data as an Engineering Concern

The gap between a prototype ML application and a production ML application is, more often than not, a data engineering gap. When a deployed model degrades, when it produces biased outputs, when results from development cannot be reproduced in staging — the root cause is more frequently a data problem than a model problem. This has been recognised explicitly enough that it has generated a named shift in practice: data-centric AI, the proposition that systematic improvements to data quality yield greater returns for most production applications than further architectural refinement of models on fixed data.

For ChestScan — the pneumonia detection application that serves as this part's case study, the data is the Kaggle Chest X-Ray Pneumonia dataset: 5,856 chest X-ray images from the Guangzhou Women and Children's Medical Centre, collected from paediatric patients aged one to five. Every engineering decision downstream — model architecture, class weighting strategy, evaluation methodology, deployment scope — is constrained by the properties of this dataset. The class distribution (73% pneumonia, 27% normal) determines which metrics are meaningful. The population specificity (paediatric, single centre, single country) determines the valid deployment context. The imaging protocol (anterior-posterior projection) determines the equipment assumptions baked into the trained model.

None of these properties are visible in the pixel values of the images. They are properties of the collection process, and they must be documented as part of building the application.

---
