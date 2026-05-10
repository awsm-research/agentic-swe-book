## 20.5 Human Evaluation

Human evaluation is the ground truth that all other evaluation methods approximate. It is also the most expensive, slowest, and most difficult to scale. These constraints mean human evaluation must be designed carefully to extract maximum signal from the effort invested.

### 20.5.1 When Human Evaluation Is Necessary

Human evaluation is required in at least three situations.

The first is calibration. Automated metrics and LLM judges must be calibrated against human judgements before they can be trusted. Without calibration, you do not know whether a RAGAS faithfulness score of 0.85 corresponds to the quality level your clinicians would rate as acceptable, or whether your LLM judge's rubric scores track expert judgements of clinical accuracy. Calibration requires running human evaluators on the same responses that automated systems have already evaluated and computing the correspondence. This is not optional if you are making deployment decisions based on automated scores.

The second is domain expertise coverage. LLM judges may lack the specialised knowledge to catch errors in narrow domains. A judge evaluating MedChat's response to a question about drug dosing in paediatric patients with renal impairment may produce a confident, plausible-sounding score on a response that a paediatric clinical pharmacist would immediately recognise as incorrect. For safety-critical domains with specialised correctness criteria, human expert evaluation is not optional — it is the only reliable quality signal.

The third is novel failure mode detection. Automated systems evaluate what they are designed to measure. Human evaluators notice things they were not looking for. The incidental finding omission described in this chapter's opening was not caught by any automated metric — it was caught by a radiologist conducting a qualitative audit who was not expecting to find it. Periodic open-ended human review of production outputs is the mechanism by which new categories of failure are discovered and added to the automated evaluation suite.

### 20.5.2 Designing Annotation Rubrics

A rubric specifies the dimensions of quality that evaluators should assess, defines what each score level means, and provides examples that anchor each level. Without a rubric, different evaluators apply their own implicit criteria and produce ratings that cannot be compared or aggregated.

For MedChat, a clinical evaluation rubric might assess: factual accuracy (are the clinical facts stated correct?), completeness (are all relevant aspects of the question addressed?), appropriate hedging (does the response distinguish between established facts and areas of clinical uncertainty?), citation quality (are sources correctly attributed?), and clarity (is the response understandable to the intended clinical audience?). Each dimension is rated on a defined scale — typically a three-point or five-point ordinal scale — with behavioural anchors that define what a score of 1, 3, and 5 looks like for that dimension.

Rubric design is an empirical exercise. The first version will not be right. Run a pilot evaluation with two or three annotators, compute disagreement, identify the dimensions where disagreement is highest, and revise the rubric to provide clearer anchors and examples for those dimensions. Repeat until agreement stabilises.

### 20.5.3 Inter-Annotator Agreement

Inter-annotator agreement (IAA) measures how consistently different evaluators apply the same rubric to the same examples. Low IAA indicates that the rubric is ambiguous, the task is intrinsically subjective in ways the rubric cannot resolve, or the annotators lack the domain knowledge to apply the rubric reliably.

Cohen's Kappa is the standard IAA metric for categorical ratings. It adjusts for the agreement that would occur by chance, which is particularly important for tasks where most responses are rated highly (which creates inflated raw agreement). A Kappa below 0.6 is generally considered insufficient for evaluation data to be used as ground truth — it means annotators are not applying the same criteria. A Kappa above 0.8 indicates strong agreement and suggests the rubric is well-defined and the annotators share consistent expertise.

IAA should be computed and reported for any human evaluation that is used to make deployment decisions or to calibrate automated metrics. An evaluation study that does not report IAA is an evaluation study that does not know whether its human raters agreed with each other. The quality of the human evaluation is unknown, and anything derived from it — including calibration of automated systems — should be treated with appropriate scepticism.

---
