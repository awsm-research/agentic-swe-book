## 20.4 LLM-as-Judge

The most significant methodological development in LLM evaluation since the field's maturation is the use of a language model to evaluate another language model's output. LLM-as-judge is a genuinely useful technique. Its strengths are real; so are its biases. Understanding both is required to use it responsibly.

### 20.4.1 The Case for LLM-as-Judge

Human evaluation is the gold standard for LLM quality assessment. It is also expensive, slow, and difficult to scale. A team evaluating a clinical LLM might be able to afford expert clinical review of 200 responses per quarter. They cannot afford expert clinical review of every response in a CI/CD evaluation gate that runs on every pull request. Something must bridge the gap between the scale of automated evaluation and the quality of human judgement.

LLM-as-judge addresses this by using a frontier model — typically GPT-4o or an equivalent — as a structured evaluator. The judge model receives the question, the generated answer, optionally the retrieved context, and a detailed rubric specifying what to evaluate and how to score it. It returns a score and, critically, a written rationale for the score. For clinical evaluation, the rubric might assess factual accuracy, clinical safety, citation quality, and appropriate hedging of uncertain claims.

The strengths of LLM-as-judge are real. A well-prompted LLM judge can handle the nuance of open-ended responses in ways that reference-based metrics cannot. It can recognise that two differently worded answers are both correct. It can identify that an answer is factually plausible but missing a safety caveat. It can evaluate domain-specific quality criteria that no rule-based metric can capture. And it can do all of this at a cost that makes evaluation on every deployment viable.

### 20.4.2 Systematic Biases

LLM-as-judge is not neutral. Several systematic biases have been empirically documented, and each has consequences for evaluation design.

**Position bias** (also called primacy/recency bias): when an LLM judge is presented with two candidate answers and asked to choose the better one, it tends to prefer whichever answer appears first (or sometimes last) in the prompt, independent of quality. In pairwise evaluation scenarios where order matters, this bias can reverse apparent quality differences between systems.

**Verbosity bias**: LLM judges systematically prefer longer, more elaborate answers, even when a shorter answer is more appropriate or more correct. In clinical contexts, a concise, accurate answer may be clinically superior to a verbose answer that buries the key point in qualifications. LLM judges will tend to score the verbose answer higher. Evaluators who do not control for verbosity may inadvertently select for wordier systems rather than better ones.

**Self-preference bias**: when an LLM is asked to evaluate outputs including some that it generated itself, it tends to prefer its own outputs. This creates a methodological problem when using the same model family for both generation and evaluation — the judge may be grading its own work. Using a judge from a different model family or a different provider reduces but does not eliminate this risk.

**Style preference**: LLM judges tend to prefer outputs that match their own stylistic patterns — formal register, confident assertions, structured formatting — regardless of whether those style preferences are correlated with quality in the target domain.

These biases can be partially mitigated through careful prompt design: providing explicit rubrics that define quality criteria in domain terms rather than style terms, randomising answer order in pairwise evaluations, and calibrating the judge against human ratings on a sample before trusting its output at scale.

### 20.4.3 When to Trust LLM-as-Judge

LLM-as-judge is most reliable when the quality criteria are clearly defined and the judge can be given explicit guidance that maps to those criteria. For MedChat, a judge can reliably evaluate whether a response appropriately hedges uncertain clinical claims ("this is a general recommendation; consult your pharmacist") and can identify whether a response directly addresses the question asked. It is less reliable for evaluating clinical accuracy in specialised domains where the judge model may lack the training data to detect subtle factual errors.

LLM-as-judge should be calibrated against human judgements before it is used as a primary quality signal. Calibration means running the judge and human evaluators on the same sample of responses, computing the agreement between judge scores and human scores, and adjusting evaluation thresholds to account for the judge's systematic tendencies. A judge that consistently rates responses 0.15 points higher than clinicians should trigger a threshold set 0.15 points higher than the clinically acceptable floor. A judge that shows near-zero correlation with human ratings on clinical accuracy should not be used for clinical accuracy evaluation.

The appropriate posture is to treat LLM-as-judge as a scalable but imperfect proxy for human evaluation, not as a replacement for it. It belongs in the automated evaluation layer — providing fast, scalable signals for every deployment — while human evaluation remains the calibration anchor and the final arbiter for contested decisions.

---
