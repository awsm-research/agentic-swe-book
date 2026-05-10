## 15.9 The Model Registry: Versioning and Lifecycle Management

---

The *model registry* is the authoritative catalogue of trained models that have been evaluated and approved for production consideration. Chapter 14 introduced the MLflow model registry as a component of the MLflow platform. This section addresses its engineering role more precisely: what it records, how lifecycle stages work, and why the alias pattern is the correct deployment mechanism.

Every entry in the registry corresponds to a specific trained model artefact — the weights, preprocessing configuration, and environment specification produced by a specific training run. The registry entry records the model name, the version number (auto-incremented with each new registration), the run ID of the training run that produced it, the lifecycle stage, any aliases, and the evaluation gate results that qualified it for registration.

The lifecycle stage encodes the model's current position in the deployment process. MLflow defines three stages: None (newly registered, not yet reviewed), Staging (under clinical review or in pre-production testing), and Production (approved for live deployment). Transitions between stages are explicit actions with associated metadata — the identity of who made the transition, when, and on what basis. This creates an auditable record of every deployment decision.

The **alias pattern** is the mechanism that decouples the serving infrastructure from specific version numbers. Rather than configuring a serving endpoint to load version 7 of the ChestScan model, the endpoint is configured to load the model at the alias `@champion`. When model version 8 is evaluated and approved, it is assigned the `@champion` alias, and the alias is removed from version 7. The serving endpoint loads `@champion` — which now resolves to version 8 — on its next request, without any change to deployment configuration. This enables zero-downtime model updates: the serving infrastructure is unchanged, and the model swap is controlled entirely through the registry.

The alias pattern also enables safe rollback. If version 8 is found to have a production problem — a performance regression discovered through monitoring — reassigning `@champion` to version 7 reverts the system to the previous model within minutes. No redeployment is required. No new build is needed. The registry update is the rollback mechanism.

A complementary alias — `@challenger` — can be used to manage canary deployments. The serving infrastructure can route a defined proportion of traffic to `@challenger` while the majority flows to `@champion`, enabling live performance comparison before full promotion. This is the model management equivalent of a feature flag: controlled exposure of a new version to a subset of production traffic, with the ability to expand or abort the rollout based on observed performance.

The registry's value is in recording every decision made about model weights — which run produced them, what evaluation they passed, who approved them, when they were promoted, and when they were retired — not in the storage of the weights themselves. This record is the evidence base that a clinical governance board, a regulatory auditor, or a post-incident investigation requires.

---
