## 20.10 Key Takeaways

1. **LLM evaluation is structurally harder than traditional ML evaluation.** Non-determinism, the absence of a single correct answer, and the subjectivity of quality criteria mean that evaluation approaches designed for classifiers do not transfer to open-ended generation. Recognising these properties is the prerequisite for designing evaluation that actually works.

2. **BLEU and ROUGE measure surface similarity, not correctness.** Using reference-based n-gram metrics as primary quality signals for open-ended generation produces evaluation that is fast, cheap, and misleading. The appropriate use of these metrics is narrow and should not include clinical or safety-critical applications where meaning diverges from surface form.

3. **RAGAS provides diagnostic power by decomposing RAG pipeline quality.** Faithfulness detects hallucination; answer relevancy detects off-topic responses; context precision detects retrieval pollution; context recall detects retrieval gaps. The metrics are most valuable when read together — the pattern of scores indicates which component of the pipeline is failing and why.

4. **LLM-as-judge scales evaluation but carries systematic biases.** Position bias, verbosity bias, and self-preference bias are empirically documented and must be mitigated through rubric design, calibration against human judgements, and appropriate use of the judge's output. LLM-as-judge is a scalable proxy for human evaluation, not a replacement for it.

5. **Human evaluation is irreplaceable for calibration, domain expertise, and novel failure detection.** Automated systems evaluate what they are designed to measure. Human evaluators notice what they were not looking for. Periodic human review of production outputs is the mechanism by which new failure categories are discovered and added to the automated evaluation suite.

6. **Evaluation datasets must be kept secret from the model and updated to track production.** Contamination — when a model has seen evaluation examples during training — invalidates evaluation scores. Static datasets that diverge from the production distribution produce scores that do not reflect production quality. Both risks require active management.

7. **Red teaming is systematic adversarial engineering, not informal testing.** A red team exercise that produces a list of failures with no follow-up process is a demonstration, not a safety practice. Found failures should feed directly into the evaluation dataset and be addressed before deployment.

8. **Automated quality gates block deployments that do not meet thresholds; human judgement handles novelty and contradiction.** The boundary between what should be automated and what requires human review is not arbitrary — it follows from the nature of the evaluation task. Automated gates catch regressions; human review catches novel failure modes and interprets conflicting signals.

9. **Evaluation is a continuous engineering practice, not a pre-deployment ceremony.** The evaluation cadence that matters is not just the CI/CD gate — it includes periodic human review, quarterly red team exercises, semi-annual calibration, and annual dataset review. Each cadence serves a different detection purpose that the others cannot substitute for.

---

### Review Questions

1. A team building a clinical decision support tool evaluates their LLM using BLEU scores against reference answers written by clinicians. They achieve a BLEU score of 0.72 and conclude that quality is acceptable. Identify two specific clinical scenarios where a response scoring well on BLEU would nonetheless be clinically unsafe, and explain why BLEU fails to detect the problem in each case.

2. MedChat's RAGAS evaluation shows: faithfulness = 0.93, answer relevancy = 0.88, context precision = 0.91, context recall = 0.61. Diagnose the most likely failure mode in the RAG pipeline, identify which component is responsible, and propose two specific remediation strategies that would address the root cause.

3. An engineering team is building an LLM-as-judge evaluation system for a legal document summarisation tool. They propose using GPT-4o to evaluate summaries produced by GPT-4o. Identify three specific risks with this approach and propose mitigations for each.

4. A startup deploying a mental health support chatbot argues that red teaming is unnecessary before launch because "users know it is AI and understand the limitations." Using the threat model structure from Section 20.7, identify two adversarial test case categories that are specifically relevant to mental health applications, describe one concrete test case in each category, and explain what harm could result if those cases are not tested before deployment.

5. MedChat's CI/CD quality gate passes all RAGAS thresholds and the LLM-judge aggregate score on every deployment. Three months after the initial deployment, a clinical pharmacist conducting a routine audit finds that the system systematically fails to mention QT-prolongation risk when recommending certain antibiotic-antihistamine combinations. Which evaluation layer failed to detect this, why, and what changes to the evaluation programme would catch this category of failure in future?

6. A team proposes simplifying their evaluation cadence: removing the quarterly human review and relying solely on the automated CI/CD gate, on the grounds that the gate is faster and cheaper. Using the MedChat case study as evidence, construct an argument for why the quarterly human review serves a distinct purpose that the automated gate cannot substitute for, and identify the specific class of failure it would catch that the gate would miss.

---
