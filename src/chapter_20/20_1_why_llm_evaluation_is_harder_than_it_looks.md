## 20.1 Why LLM Evaluation Is Harder Than It Looks

Traditional machine learning evaluation has a clean structure. You hold out a test set. The model produces predictions. You compare predictions to labels. Accuracy, precision, recall, F1 — the metrics are computed automatically, objectively, and reproducibly. Two engineers running the same evaluation against the same model on the same test set will get exactly the same number. The hardness of ML evaluation lies in choosing the right metric and constructing a representative test set. Given those choices, computation is mechanical.

LLM evaluation breaks this structure at every step, for reasons built into what language models are.

### 20.1.1 Non-Determinism

The first challenge is non-determinism. A classification model with fixed weights produces the same output for the same input, every time. A language model with a non-zero temperature samples from a probability distribution over tokens at each step. Run the same query twice and you will get two different responses. Both may be correct. Both may be wrong. Both may be correct in different ways. This means that a single evaluation run does not characterise a model's quality — it characterises one draw from the model's output distribution. Reproducible evaluation requires either fixing temperature to zero (which changes the model's behaviour and may not reflect production conditions) or running multiple samples and averaging results.

Non-determinism has a deeper consequence: evaluation scores become distributions, not scalars. Reporting a single RAGAS faithfulness score for a model as if it were a fixed property of that model is a misrepresentation — the score will vary across evaluation runs, and the variance matters.

### 20.1.2 No Single Correct Answer

The second challenge is the absence of a single correct answer. A classifier has a ground-truth label: the image is either a cat or it is not. An LLM generating a clinical summary of a patient record can produce a correct summary in hundreds of different ways — different structures, different levels of detail, different terminology, different emphasis. All of them may be equally appropriate. Most of them will differ from any particular reference answer. Evaluation that penalises deviation from a reference answer will systematically underestimate quality, because the space of correct answers is vast and the reference is one point in it.

This is not a limitation that can be overcome by collecting more reference answers. Even with ten human-written reference summaries, a model that produces an eleventh valid summary will score poorly. The fundamental issue is that correctness for open-ended generation is not a function of surface similarity to a reference — it is a function of meaning, completeness, and appropriateness in context.

### 20.1.3 Subjectivity

The third challenge is subjectivity. Different evaluators, applying their own expertise and priorities, will reach different quality judgements on the same LLM output. A clinician reading a drug interaction summary may prioritise completeness; a patient advocate may prioritise accessibility; a regulatory reviewer may prioritise citation accuracy. These are not all measuring the same thing. Evaluation rubrics impose structure, but they cannot eliminate the value judgements embedded in the criteria. An LLM system that scores well on one evaluator's rubric may score poorly on another's, not because of error but because the rubrics encode different views of what good looks like.

Subjectivity is not a problem to be eliminated — it is a property to be measured and managed. When human evaluators disagree substantially on quality ratings, the rubric is underspecified, the task is intrinsically ambiguous, or the evaluators do not share the same domain knowledge. All three cases are problems. All three require diagnosis before any quality number from those evaluations can be trusted.

### 20.1.4 The Evaluation Paradox

These three properties — non-determinism, multiple correct answers, and subjectivity — create an evaluation paradox. The systems most in need of rigorous evaluation are the systems where rigorous evaluation is hardest to do. A clinical LLM that summarises complex patient records, answers differential diagnosis questions, and explains drug interactions operates in exactly the domain where evaluation is most difficult: open-ended, domain-specific, safety-critical, and dependent on expert judgement. The temptation is to use what is easy to compute rather than what actually matters.

---
