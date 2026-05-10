## 14.5 Dataset Versioning and Documentation

A production ML application is only as reproducible as the dataset it was built on. If the dataset changes — images are added, removed, or relabelled — but the change is not recorded, the application cannot be reproduced from the training pipeline alone. Dataset versioning treats datasets as immutable, versioned artifacts with the same discipline applied to software source code.

### 14.5.1 Content-Based Versioning

The most reliable versioning mechanism is content-based: compute a cryptographic hash of the dataset contents and record that hash alongside every model trained on it. If the hash matches, the dataset is identical. If it differs, something changed. This makes the hash a tamper-evident seal: any claim to have reproduced a result can be verified by comparing hashes, and any undocumented change to the dataset is detectable.

### 14.5.2 Datasheets for Datasets

Gebru et al. proposed that every dataset should be accompanied by a structured document — a datasheet — answering questions about its collection, composition, preprocessing, intended uses, and known limitations, modelled on the datasheets that accompany electronic components ([Gebru et al., 2021](https://doi.org/10.1145/3458723)).

For the Kaggle Chest X-Ray dataset, a datasheet records: the Guangzhou Women and Children's Medical Centre as the source institution, the paediatric age range (1–5 years) as the sampled population, the expert physician review process as the labelling methodology, and the inapplicability of any application built on it to adult patients as a known and documented limitation. Without this datasheet, a team inheriting the application has no principled basis for knowing where it can safely be deployed.

### 14.5.3 Data Lineage

Data lineage is the end-to-end record of how a dataset was produced: what raw data was ingested, what transformations were applied, what validation checks passed, and what the output was at each stage. In software engineering, the equivalent is a build log — the record of every step that produced a software artifact from source code. For ML applications, data lineage is the build log for the training dataset.

Maintaining data lineage serves three purposes that directly affect the production application. It enables reproduction: given the lineage record and the original raw data, the training dataset can be recreated exactly. It enables root-cause analysis: when an application produces suspicious outputs, the lineage record allows investigators to determine whether the issue originated in raw data, a transformation step, or the split strategy. And in regulated domains, it enables compliance: demonstrating that training data was collected and processed according to documented standards is increasingly required by law.

---
