## 20.8 Quality Gates in CI/CD

An evaluation framework that does not block bad deployments is a reporting system, not a quality control system. Quality gates in CI/CD pipelines transform evaluation from a post-hoc reporting exercise into a pre-deployment enforcement mechanism. When thresholds are not met, the pipeline fails and deployment does not proceed.

### 20.8.1 What to Automate

Automated quality gates are appropriate for evaluation criteria that are: computable without human involvement, stable enough that threshold violations reliably indicate a genuine quality problem, and fast enough to run in a CI/CD pipeline without prohibitively extending build times.

For a RAG system like MedChat, the automated quality gate suite covers RAGAS metrics on a fixed evaluation dataset (faithfulness, answer relevancy, context precision, context recall — each with defined minimum thresholds), LLM-as-judge scores on a clinical quality rubric (factual accuracy, appropriate hedging, citation quality — each calibrated against historical human ratings), safety test suite pass rate (the proportion of adversarial test cases where the model produces an acceptable response), and response latency at the 95th percentile.

Each metric has a threshold derived from calibration against human evaluation and the risk tolerance of the deployment context. For MedChat, faithfulness below 0.85 is a hard block. Answer relevancy below 0.80 is a hard block. The safety test suite pass rate must be 100 per cent — any adversarial test case that elicits an unacceptable response is a deployment blocker, not a statistical nuance.

When an automated gate fails, it fails with a diagnostic report: which metric failed, by how much, and which examples in the evaluation dataset drove the failure. A gate that fails without explanation forces engineers to re-run the evaluation manually to understand what went wrong. A gate that fails with a clear diagnostic report enables rapid triage and targeted remediation.

### 20.8.2 What Requires Human Judgement

Not everything can be automated. Human review is required in at least three situations.

When a new model version, a new prompt architecture, or a new retrieval strategy is introduced, a human review of a sample of responses is required before the first deployment — not because the automated gates cannot catch known failure modes, but because genuinely novel architectures may introduce failure modes that the automated suite was not designed to detect. The automated gate catches regressions; human review catches novelties.

When automated gates produce conflicting signals — faithfulness is high but LLM judge scores are low, or RAGAS scores improved while safety test pass rate declined — the contradiction requires human interpretation. Automated metrics do not reason about their own inconsistencies; humans must.

When a gate threshold is being set or revised, human calibration is required. The thresholds are not arbitrary — they are derived from expert judgements about what constitutes acceptable quality in the deployment context. Changing thresholds without expert input is a way of silently redefining what "acceptable" means.

### 20.8.3 The Evaluation Cadence

Quality gates in CI/CD provide a high-frequency signal: every deployment is evaluated. This frequency is valuable for catching regressions quickly. It is not sufficient on its own. A balanced evaluation cadence also includes: monthly human review of a random sample of production outputs to detect quality drift that automated metrics may not capture, quarterly red team exercises to update the adversarial test suite, semi-annual calibration of LLM judge scores against fresh human ratings, and annual review of the evaluation dataset to assess whether it remains representative of production traffic.

The evaluation cadence is not a bureaucratic procedure — it is the mechanism by which the team maintains confidence that the system deployed in production is the system they intended to deploy. Without it, automated gate scores become progressively less meaningful as the production distribution drifts from the evaluation distribution.

---
