## 14.6 Managing ML Application Runs

Building a production ML application involves more than a single training run. Teams compare architectures, tune hyperparameters, and evaluate the effect of preprocessing changes. Each of these produces a trained model with different characteristics. Without systematic management of these runs, selecting the right model for production is an act of memory rather than an engineering decision.

Run management is the practice of recording every training run in a way that makes it reproducible, comparable, and auditable — enabling teams to make principled decisions about which model should be deployed, and to defend those decisions to reviewers and auditors.

### 14.6.1 What a Run Record Contains

A complete run record contains six elements:

**Parameters**: Every value that was set before training began — learning rate, batch size, number of training steps, model architecture, regularisation settings, augmentation configuration. Recording parameters before training starts ensures that even a run that fails due to hardware error leaves a complete configuration record.

**Metrics**: Every numerical measurement produced by the run — loss values at each training step, validation accuracy, test AUC, inference latency. Metrics recorded at each training step create time-series that reveal how the model learned: whether training loss decreased smoothly, whether validation loss diverged (indicating overfitting), and at what point peak performance was reached.

**Artifacts**: Every binary file produced by the run that a downstream process might need — model weights, confusion matrices, performance reports, visualisations. Artifacts are stored separately from the metadata and referenced by the run record.

**Environment**: The software context in which the run executed — Python version, package versions, GPU driver version, hardware. The environment record is what allows the run to be reproduced on different infrastructure.

**Source version**: The exact version of the code that produced the run — specifically, the Git commit hash. A commit hash uniquely identifies the state of the entire codebase at the time the run was executed. Combined with the dataset version and environment record, it completes the provenance chain.

**Dataset version**: The content hash of the dataset used for training. This closes the loop between the dataset versioning practice described in section 14.5 and the run record: the record answers not just "how was the model trained" but "on what data."

### 14.6.2 The Reproducibility Guarantee

A complete run record provides a reproducibility guarantee: given the record, someone with access to the same raw data and code repository can reproduce the model to within the limits of hardware non-determinism. This guarantee fails if any of the six elements is missing. Missing the dataset version means the guarantee fails if the dataset is subsequently modified. Missing the environment means the guarantee fails when package versions change — which they will.

### 14.6.3 Selecting a Model for Production

When multiple runs have been completed, the production selection decision requires more than sorting by the primary metric. Three additional considerations matter.

First, robustness: does the model with the highest test AUC also have reasonable performance across all classes, or does its overall metric mask poor performance on a specific subgroup? The confusion matrix and per-class precision and recall reveal what the summary metric conceals.

Second, stability: did the model converge smoothly, or did it exhibit high variance across training steps? A model that achieved high performance through an unstable training trajectory may be sensitive to small changes in data or configuration.

Third, cost: does the performance improvement over a simpler baseline justify the additional inference cost? A more complex model that achieves 2% higher AUC but requires 4× the compute of a simpler baseline may not be the right choice for a resource-constrained deployment environment.

---
