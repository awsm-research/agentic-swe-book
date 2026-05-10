## 14.7 MLflow for ML Application Development

MLflow is the platform used in this book to implement the run management and dataset versioning practices described above. Its architecture has four components, each addressing a specific engineering need in building a production ML application.

### 14.7.1 The Tracking Server

The tracking server accepts run records from training pipelines and makes them queryable through a web UI and a REST API. It stores metadata — parameters, metrics, tags, and run status — in a backend database: SQLite for local development, PostgreSQL for production deployments that need to support concurrent access from multiple training workers. The tracking server is intentionally separated from the artifact store because metadata is small, structured, and frequently queried, while artifacts are large, binary, and accessed infrequently.

### 14.7.2 The Artifact Store

The artifact store holds binary objects produced by training pipelines. In local development, this is a directory on the filesystem. In production, it is an object store such as Amazon S3, Google Cloud Storage, or Azure Blob Storage. The tracking server stores a URI reference to each artifact rather than the artifact itself, keeping the tracking server database small regardless of how many model weight files and evaluation plots are produced.

### 14.7.3 The Model Registry

The model registry is the catalogue of trained models that have been approved for production consideration. Not every training run produces a registered model. The registry entry is created only after a run's evaluation results meet the quality threshold specified in the application's evaluation gate — a deliberate engineering checkpoint between development and deployment. Each registry entry records the model name, version, the run that produced it, the current lifecycle stage (Staging or Production), and any aliases.

The alias pattern — referencing a model by a role name such as `@champion` rather than a version number — is the mechanism that decouples the serving infrastructure from specific model versions. The serving API loads the model by its alias. Promoting a new version to `@champion` updates what the serving API loads on its next request, without any change to deployment configuration. This enables zero-downtime model updates.

### 14.7.4 Querying Runs Programmatically

The MLflow tracking API supports programmatic queries over run records: filtering by parameter value, sorting by metric, and retrieving the run that produced the best value of a specified metric. This capability is what transforms run management from a record-keeping discipline into an engineering tool. Rather than a human selecting the best model by inspecting the UI and copying a run ID, a pipeline script can query for the run that maximises test AUC subject to constraints (such as a minimum precision threshold on the underrepresented class), retrieve its artifact URI, and submit it to the model registry — all without human intervention in the selection logic.

---

### Review Questions

1. The Recht et al. (2019) ImageNet study found that model performance dropped 11–14 percentage points on a new test set collected using the same methodology as the original. Using the data engineering concepts from this chapter, identify the most plausible root cause of this gap. What practice, applied during the original benchmark's development, would have detected the problem earlier?

2. A team is building a skin lesion classification application using a dataset collected from three hospitals. Hospital A contributed 70% of the images. Describe two specific quality problems this composition might introduce, name the quality dimension each violates, and propose an engineering response for each.

3. You are asked to audit the reproducibility of a production ML application. The team provides the model weights, the training script, and the test set. What additional artefacts do you require, and why is each necessary to establish that the application can be reproduced?

4. A colleague argues for random splitting on a chest X-ray dataset because "it maximises training data and the statistics are clean." Construct a concrete scenario in which random splitting produces a reported test AUC of 0.94 while the true performance on genuinely unseen patients is closer to 0.81. Describe the precise mechanism by which the inflation occurs.

5. Three training runs have been completed for ChestScan with different learning rates. Run A has the highest test AUC. Describe three criteria beyond raw test AUC that should inform the decision about which run to register for production, and explain the consequence of ignoring each.

6. A pneumonia detection application has been in production for three months. Monitoring shows that precision on the viral pneumonia class dropped from 0.89 to 0.71, while bacterial pneumonia precision is unchanged. Using the ML data lifecycle from section 14.2, identify the two most plausible causes of this specific degradation pattern and describe what investigation each hypothesis would require.

---
