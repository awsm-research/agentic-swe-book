## 20.9 The MedChat Case Study

MedChat is a clinical Q&A system that retrieves relevant passages from a corpus of clinical guidelines, drug references, and pharmacopoeia entries, and uses an LLM to generate responses grounded in those retrieved passages. Its users are healthcare professionals making clinical decisions. The consequence of a wrong answer with clinical confidence is not a frustrated user — it is potential patient harm. The evaluation framework for MedChat cannot be approximate.

### 20.9.1 The Evaluation Architecture

MedChat's evaluation architecture implements all three layers of the evaluation pyramid:

The automated metric layer runs RAGAS on a static evaluation dataset of 150 expert-curated question-answer pairs covering the clinical domains in the corpus. The dataset was constructed by clinical pharmacists who wrote questions from real clinical scenarios, retrieved the relevant corpus passages manually, and wrote reference answers based on those passages. This construction process ensures that the ground truth reflects expert clinical reasoning, not casual knowledge.

The LLM-as-judge layer uses GPT-4o with a structured rubric that assesses four dimensions: factual accuracy (does the response state correct clinical facts?), appropriate hedging (does the response distinguish between established guidance and areas of clinical uncertainty?), source attribution (are claims correctly attributed to retrieved sources?), and appropriate scope (does the response stay within the decision-support role without making prescriptive clinical decisions?). Each dimension is scored from 1 to 5 with behavioural anchors. The rubric was calibrated against clinical pharmacist ratings on a set of 50 responses before deployment in the quality gate.

The human evaluation layer conducts quarterly reviews in which two clinical pharmacists independently rate 50 randomly sampled production responses using the same rubric as the LLM judge. Their ratings are compared to the LLM judge's ratings for the same responses. When the correlation between judge and human ratings falls below 0.7, the rubric is reviewed and the judge is recalibrated.

### 20.9.2 Interpreting RAGAS Scores in Practice

In MedChat's first production deployment, the automated gate passed with faithfulness of 0.91 and answer relevancy of 0.87. However, context recall was 0.72 — significantly below the clinical acceptability threshold of 0.85. The retrieval system was finding relevant passages for the main clinical question but missing supplementary information about contraindications and special populations.

The RAGAS diagnostic pointed clearly at retrieval coverage, not generation quality. The fix was not to prompt the model differently — the model was faithfully summarising what it retrieved. The fix was to the retrieval strategy: adding a second retrieval pass specifically for contraindications and special populations, triggered whenever the original query contained drug names. Context recall improved to 0.88 on the next evaluation run.

This is exactly the diagnostic value that RAGAS provides: the metrics disaggregated the pipeline failure and pointed to the correct component to fix. Evaluating only the final answer — whether it looked good or scored well on a generic quality rubric — would have hidden the structural retrieval gap.

### 20.9.3 Red Teaming Findings

MedChat's first structured red team exercise, conducted before the initial production deployment, identified three significant failure categories.

The first was outdated guideline synthesis. On several questions about conditions where treatment guidelines had been revised in the previous two years, MedChat produced confident responses that reflected the older guideline rather than the current one. The responses were internally consistent and drawn faithfully from retrieved documents — but the corpus contained outdated documents alongside current ones, and the retrieval system was not systematically preferring more recent documents. The remediation was to add publication date metadata to all corpus documents and weight retrieval scores by recency for clinical guideline content.

The second was scope boundary failure on multi-turn conversations. In adversarial conversations that started with general clinical questions and gradually shifted toward specific patient management decisions, MedChat began making clinical recommendations that crossed the boundary from decision support to prescribing advice after five to seven turns. Single-turn safety tests had passed. Multi-turn escalation had not been tested. The remediation was to add a scope boundary check to the system prompt and to expand the adversarial test suite to include multi-turn escalation scenarios.

The third was demographic inconsistency on dosing questions. When the same dosing question was posed for patients described with different demographic characteristics, MedChat produced slightly different dose recommendations for patients described as elderly — sometimes correctly (age is clinically relevant for renal clearance) and sometimes incorrectly (when age was not clinically relevant to the dosing). The inconsistency itself was a quality problem, separate from whether any individual recommendation was correct. The remediation involved adding demographic consistency as a criterion in the LLM-as-judge rubric and constructing a set of matched demographic pairs in the evaluation dataset.

### 20.9.4 The Quality Gate in Practice

MedChat's CI/CD quality gate blocks deployment when any of the following thresholds are not met: RAGAS faithfulness below 0.85, answer relevancy below 0.80, context precision below 0.78, context recall below 0.82, LLM-judge aggregate quality score below 3.8 out of 5, and safety test pass rate below 100 per cent. The gate produces a structured report that identifies which metric failed, by how much, and which evaluation examples drove the failure.

Since the gate's introduction, three pull requests have been blocked by it: one when a prompt revision inadvertently reduced faithfulness by introducing a paraphrase instruction that caused the model to rephrase retrieved content in ways that RAGAS could not verify as grounded, one when a corpus update introduced outdated documents that lowered context recall on a subset of questions, and one when a red-team-discovered failure mode — prescription boundary violation in multi-turn conversations — was not fixed before the pull request was submitted. All three were legitimate quality failures that the gate caught before deployment. All three would have reached production without the gate.

---
