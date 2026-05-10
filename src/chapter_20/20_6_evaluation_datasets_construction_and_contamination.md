## 20.6 Evaluation Datasets: Construction and Contamination

The evaluation dataset is the foundation of any LLM quality assurance programme. Its quality determines the reliability of every metric computed against it. A model that scores well on a poorly constructed evaluation dataset tells you almost nothing about how it will perform in production.

### 20.6.1 Static Evaluation Datasets

A static evaluation dataset is a fixed collection of question-answer-context-groundtruth tuples that does not change once constructed. Static datasets are easy to compute against — you run the model, compare outputs to ground truth, and get a score. They are also the foundation of reproducible benchmarking: two engineers using the same static dataset will get comparable results.

The limitation of static datasets is that they go stale. A dataset constructed in 2023 from clinical guidelines current at that time may not reflect guideline updates in 2025. A dataset constructed from the queries that were available when the system was first built may not cover the query types that emerge once the system is deployed to a broader user population. A static dataset that once reflected the production distribution may diverge from it as usage patterns evolve. Evaluation scores on a static dataset that has diverged from the production distribution are not estimates of production quality — they are estimates of performance on a historical sample that may no longer be representative.

### 20.6.2 Dynamic Evaluation Datasets

Dynamic evaluation datasets are updated over time to track the evolving production distribution. New examples are added from production traffic (with expert annotation to establish ground truth), outdated examples are retired, and the dataset grows to cover edge cases discovered in production. Dynamic datasets are harder to manage and make score comparison across time more complex, but they maintain alignment between the evaluation and the actual deployment context.

For MedChat, a hybrid strategy is appropriate: a stable core evaluation set for reproducible benchmarking that does not change, supplemented by a growing extension set that tracks production traffic and captures failure modes as they are discovered. Evaluation gates that block deployment use both: the stable set for reproducibility, the extension set for coverage of known failure modes.

### 20.6.3 Contamination Risk

Contamination occurs when an LLM has seen evaluation examples during training, or when evaluation examples are drawn from the same distribution as training data in ways that give the model an artificial advantage. A model that "memorised" evaluation examples during training will score well on that evaluation without the score reflecting generalisation — the model is recognising examples, not reasoning from knowledge.

Contamination risk is particularly acute for LLMs because large foundation models are trained on enormous, diverse corpora that may include benchmark datasets, public evaluation examples, and the answers to standard test questions. A benchmark that was publicly available before the model's training cutoff may have been included in training data, making high scores on that benchmark unreliable indicators of genuine generalisation.

The primary control for contamination is keeping evaluation datasets secret from the model. Evaluation examples should not be published, indexed by search engines, or included in any data pipeline that feeds model training. For organisations building on third-party foundation models, this means constructing evaluation datasets from proprietary data sources — internal clinical records, domain-expert-authored questions, real production queries — rather than publicly available benchmarks. Public benchmarks measure how well a model performs on the public benchmark. Private, proprietary evaluation datasets measure how well a model performs on your problem.

---
