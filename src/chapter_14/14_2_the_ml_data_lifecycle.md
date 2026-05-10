## 14.2 The ML Data Lifecycle

The ML data lifecycle is the sequence of transformations that raw data undergoes before it can be used to build a production ML application. Each stage produces an output that the next stage depends on, and each stage is a potential source of failures that standard software testing is not equipped to catch.

### 14.2.1 Collection

Collection is the point at which the world is sampled. The key engineering question is representativeness: does the collected sample faithfully represent the distribution the application will encounter in production?

Population coverage is the first dimension. A clinical imaging dataset collected at a single centre reflects that centre's patient population, equipment, imaging protocols, and clinical practices. A pneumonia detection application built on that data may not perform reliably at other centres with different equipment or patient demographics. This is not a flaw in the dataset — it is a property of the dataset that constrains the application's deployment scope and must be documented accordingly.

Label quality is the second dimension. In supervised learning, the label is the training signal, and the upper bound on what the model can learn is determined by the quality of that signal. Labels produced by a single annotator under time pressure are not equivalent to labels produced by consensus among expert clinicians following a structured protocol. The labelling process must be documented with the same engineering rigour as the collection process. For the Kaggle dataset, labels were produced by expert physicians with viral versus bacterial distinction confirmed by laboratory culture results — a high-quality process, but one specific to one centre's diagnostic methodology.

### 14.2.2 Validation

Data validation is the process of verifying that collected data meets the expectations of the downstream application pipeline. It is analogous to input validation at a system boundary in traditional software engineering: you do not trust data arriving from an external source without checking it.

The critical distinction is that data validation failures are not always binary. A dataset may pass schema validation — all expected fields are present, all values are within range — while still containing images with pixel distributions that differ materially from the normalisation assumptions built into the training pipeline. Validation must therefore cover both structural properties (schema, file integrity, label distribution) and statistical properties (pixel value distributions, class balance, duplicate detection).

For the chest X-ray application, structural validation checks include: verifying that all images are readable and not corrupted, that the label distribution matches the documented class proportions, and that the train and test split directories do not share patient identifiers. Statistical validation adds: confirming that pixel intensity distributions are consistent with the greyscale profiles expected from chest X-ray imaging, and flagging any images whose distributions suggest a different imaging modality or equipment calibration.

### 14.2.3 Preprocessing

Preprocessing transforms raw data into the form the model expects. For image data, this includes resizing, normalisation, and augmentation. The engineering requirement is that preprocessing must be reproducible and shared across every component of the application that touches data.

The normalisation parameters applied during training — the mean and standard deviation used to standardise pixel values — must be identical at serving time. If they are not, the model receives inputs from a distribution it was not trained on and performance degrades silently. This failure mode is called train/serve skew, a data validation risk the ML Test Score rubric identifies as one of the most impactful sources of silent production degradation ([Breck et al., 2017](https://doi.org/10.1109/BigData.2017.8258038)).

The solution is architectural: define preprocessing as code in a shared module that is imported by both the training pipeline and the serving API. The parameters are fixed at the time training data is prepared and versioned alongside the model artifact. When the model is loaded for serving, it retrieves its preprocessing configuration from the same versioned artifact store.

### 14.2.4 Splitting

The split strategy determines whether the application's performance metrics mean anything at all. A correct split ensures the test set is a genuine held-out sample the model has never seen. An incorrect split allows information from the test set to leak into training, producing an application that appears to perform better than it does — until it encounters real production traffic. Section 14.4 addresses this in depth.

### 14.2.5 The Training Artifact

The output of the data lifecycle is the training artifact: a versioned, documented dataset ready to be consumed by the model training pipeline. In a mature ML engineering practice, a training artifact includes: the dataset itself, a content hash for tamper detection, a documented schema, a provenance trail (source, collection date, collection methodology, labelling process), the split indices used to partition it, and the validation report confirming it met quality requirements before training began.

A missing dataset version hash is the single most common reason a model cannot be re-evaluated six months after deployment — by that point the dataset may have been updated and the original training state is unrecoverable. Without the split indices, the evaluation that justified deploying the model cannot be reproduced. Without the provenance trail, there is no principled basis for defining where the model can safely be used.

---
