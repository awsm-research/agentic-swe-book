## 13.2 What Breaks When You Apply Traditional SE to AI Systems

The temptation when encountering a new kind of system is to apply familiar practices and assume the gaps will be small. For AI systems, the gaps are not small. This section identifies the specific points where traditional SE practice breaks down — not to argue that traditional SE is wrong, but to explain precisely why it is insufficient.

### 13.2.1 Testing Cannot Cover What You Cannot Enumerate

Traditional software testing is built on the premise that you can describe correct behaviour and write tests that verify it. Unit tests verify individual functions. Integration tests verify component interactions. End-to-end tests verify user workflows. The underlying assumption is that "correct" is a property the engineer can specify.

For a machine learning classifier, "correct" is a distribution. You can specify that the model should achieve at least 90% accuracy on the test set, at least 0.85 AUC, and no more than a 5% disparity in recall between demographic groups. But you cannot specify correct behaviour on every possible input — the input space is infinite. What you can do is sample it carefully, stratify that sample by the properties that matter, and build a test suite that is a legitimate proxy for production performance. This is a fundamentally different kind of quality assurance.

For a language model application, the challenge is sharper: the model's output is a natural language string. There is no single correct answer to "What antibiotics should I consider for a patient with a penicillin allergy?" The output must be clinically reasonable, appropriately hedged, correctly sourced, and safe — none of which can be reduced to a simple equality check. Evaluating LLM outputs requires evaluation frameworks (reference-based metrics, LLM-as-judge, human review) that have no equivalent in traditional software testing.

### 13.2.2 Version Control Does Not Capture the Full System

Git captures the code. For Software 1.0 systems, code is the system — version the code and you have versioned the system. For Software 2.0 systems, the system is the combination of code, data, and model weights. The same code trained on different data produces a different system. The same code and data trained with a different random seed produces a slightly different system. Without versioning all three artefacts together, reproducibility is an aspiration rather than a guarantee.

This is why the 2021 Nature Machine Intelligence review of 2,212 COVID-19 diagnostic models found none suitable for clinical use ([Roberts et al., 2021](https://doi.org/10.1038/s42256-021-00307-0)). The models existed. The papers described their architectures. But the data splits were not documented, the preprocessing was not reproducible, and the model weights were not published alongside the code. The models could not be reproduced, audited, or deployed safely — not because of poor engineering, but because the engineering practices used did not extend to all the artefacts that defined the system.

### 13.2.3 Requirements Engineering Assumes Stable Specifications

The requirements engineering process described in Chapter 2 assumes that specifications can be elicited, documented, and validated before development begins. This assumption holds for most Software 1.0 systems: the bank needs a payment processing system that meets specific regulatory requirements, and those requirements can be written down.

AI system requirements are inherently unstable in ways that traditional requirements engineering is not designed to handle. Model performance on training data does not predict performance on production data after distribution shift. A clinical AI system trained on 2019 patient data may degrade significantly when deployed into a 2022 patient population affected by long COVID. The requirements for that system — "detect pneumonia accurately" — are unchanged, but the system's ability to meet them has eroded. Traditional SE has no systematic practice for detecting this erosion and triggering a requirements re-evaluation.

### 13.2.4 Deployment Is Not a One-Time Event

In traditional SE, a software release is a discrete event: code passes testing, is promoted to production, and runs until the next planned release. Defects are addressed through hotfixes or new releases. The system's behaviour between releases is stable.

An AI system in production is not stable. Its inputs change as user behaviour evolves. Its outputs may degrade as the world it was trained on diverges from the world it is operating in. A fraud detection model trained before a new fraud vector becomes active will begin to miss fraud without any change to its code. Identifying this degradation, diagnosing its cause, and triggering a retraining cycle are operational responsibilities with no direct equivalent in traditional software maintenance.

---
