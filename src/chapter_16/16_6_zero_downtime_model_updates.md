## 16.6 Zero-Downtime Model Updates

---

The production lifecycle of an ML application involves periodic model updates: a new training run has produced a better model, a new dataset version has been incorporated, or a drift event has triggered retraining. The engineering challenge is delivering these updates without service interruption.

### 16.6.1 The Alias Pattern

The mechanism that enables zero-downtime model updates in MLflow-based systems is the alias: a named reference to a model version in the registry. Rather than referencing a specific version number — `models:/chestscan-detector/12` — the serving code references an alias — `models:/chestscan-detector@champion`. The alias is a level of indirection between the serving code and the specific model version in use.

Promoting a new model to production involves two registry operations: assigning the `@champion` alias to the new version, and optionally downgrading the previous version to `@challenger` or removing its alias. The serving code is not changed. The container is not rebuilt. The change takes effect when the serving code next loads the model — either on the next container restart or, in a system with dynamic model reloading, on the next scheduled refresh.

The alias pattern also enables staged rollouts. A new model version can be assigned a `@challenger` alias and routed a fraction of production traffic alongside the existing `@champion`. The traffic split allows the challenger to be evaluated against live production data before being promoted. If the challenger underperforms — lower confidence, more drift, worse user feedback — it is removed from the registry without ever having been the champion.

### 16.6.2 The Champion/Challenger Framework

The champion/challenger framework is the standard pattern for managing model version transitions in production. The champion is the currently deployed model — the one serving all or most production traffic. A challenger is a candidate replacement that has passed the evaluation gate but has not yet been promoted to champion.

A well-governed champion/challenger process includes: a minimum evaluation period before promotion (the challenger must serve a minimum number of requests or run for a minimum duration); a comparison of performance metrics on a held-out slice of production traffic; a rollback plan that can return to the champion within minutes if the challenger exhibits unexpected behaviour; and a record of the promotion decision, including who authorised it, what metrics justified it, and when it occurred.

This governance is not bureaucratic overhead. It is the mechanism by which the organisation maintains confidence in the model serving its users. A model registry that allows any trained model to be assigned the `@champion` alias without evaluation and approval is not a safety mechanism — it is an unmanaged artefact store.

---
