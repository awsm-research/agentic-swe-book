## Learning Objectives

By the end of this chapter, you will be able to:

1. Explain why deploying a registered model to production is an engineering challenge distinct from training, and identify the structural gaps between a trained artefact and a reliable serving system.
2. Compare batch and online inference patterns, and identify the criteria that determine which is appropriate for a given application.
3. Define train/serve skew, describe its root cause, and explain the architectural pattern that prevents it.
4. Describe the specific requirements that distinguish ML serving infrastructure from standard web application infrastructure.
5. Explain the three-tier serving architecture — frontend, backend API, and model server — and articulate the separation of concerns each tier enforces.
6. Explain how the `@champion` alias pattern in a model registry enables zero-downtime model updates.
7. Define data drift and concept drift, describe how each manifests in a production ML system, and distinguish between the conditions that cause each.
8. Explain the Population Stability Index as a drift detection metric, interpret its threshold values, and describe its limitations.
9. Identify the three categories of retraining trigger and explain the production conditions that activate each.
10. Describe how serving, containerisation, and monitoring principles apply specifically to the ChestScan pneumonia detection system.

---
