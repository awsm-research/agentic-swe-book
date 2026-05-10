## 15.1 Why Software QA Does Not Transfer

---

Traditional software quality assurance is built on a foundational assumption: correct behaviour can be specified in advance, and a test suite can verify that the system meets that specification. A unit test passes or fails. An integration test either exercises the correct code path or it does not. The correctness criterion is binary, explicit, and determined by the engineer who wrote the specification.

This assumption fails for machine learning systems in three distinct ways, each requiring a different engineering response.

The first failure is that ML system quality is a distribution, not a value. A conventional function either returns the right answer or it does not. A trained classifier returns the right answer on 87.4% of test examples — and that percentage tells you almost nothing about which 12.6% it gets wrong, whether those errors cluster in a particular subgroup, or whether that performance will hold when deployment shifts the input distribution. The entire apparatus of traditional software testing — unit tests, integration tests, regression suites — verifies functional correctness. It cannot verify statistical properties.

The second failure is that the specification is itself a design choice. When a software engineer writes a unit test, they are encoding a requirement: given this input, the function must produce this output. When an ML engineer evaluates a model, they must first decide which metric to measure. That choice encodes assumptions about the relative cost of different error types, the class distribution in production, and what "good enough" means for the application. The Kaggle Chest X-Ray dataset used in ChestScan is 73% pneumonia and 27% normal. A classifier that predicts pneumonia for every single input achieves 73% accuracy — and misses every normal patient. The metric choice is not a technical detail; it is the specification.

The third failure is that the behaviour being evaluated is not fully determined by the code. Two runs of the same training script — same architecture, same data, same hyperparameters — may produce models with subtly different performance profiles due to random weight initialisation and non-deterministic GPU operations. Traditional software testing can verify that a function is correct once and conclude it will always be correct. ML evaluation must acknowledge that the artefact being evaluated is stochastic in its production, and that the evaluation result is itself a statistical estimate of performance on a sample of possible inputs.

These three differences mean that ML model evaluation requires a purpose-built methodology — not a modification of traditional QA, but a discipline built from different first principles.

---
