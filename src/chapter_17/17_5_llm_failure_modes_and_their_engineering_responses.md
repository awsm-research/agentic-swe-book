## 17.5 LLM Failure Modes and Their Engineering Responses

---

Software 2.0 systems fail in ways that can be characterised statistically: accuracy degrades on out-of-distribution inputs, calibration fails under distributional shift, performance disparities emerge across demographic groups. These failures are amenable to evaluation frameworks built around metrics and test sets. Software 3.0 systems fail differently — and understanding the differences is necessary to build effective defences.

### 17.5.1 Hallucination

Hallucination is the production of confident, fluent, plausible-sounding outputs that are factually incorrect. It is the defining failure mode of language models, and it is qualitatively different from the failure modes of traditional software. A traditional system that produces an incorrect output does so because of a logic bug — there is a specific, locatable cause. A hallucinating language model does not have a locatable cause in the same sense: the model is sampling from a probability distribution over token sequences, and hallucinated outputs are simply tokens that were assigned high probability by the model's learned distribution without being factually grounded.

The engineering response to hallucination is architectural, not incidental. For knowledge-grounded applications, RAG is the primary mitigation: by injecting relevant, verified passages into the context and instructing the model to ground its answer in that content, hallucination becomes detectable. An answer that is not supported by the retrieved context can be flagged, whereas an answer generated entirely from parametric memory cannot be automatically verified.

For applications where RAG is not applicable, alternative responses include: constraining the model to respond from a predefined set of answers rather than generating freely; using a second model call to evaluate whether the first model's output is consistent with known facts; providing the model with explicit uncertainty language templates and instructing it to use them when confidence is low; and treating any output that makes specific verifiable claims as requiring human review before acting upon.

Hallucination cannot be fully eliminated in Software 3.0 systems. It can be reduced, detected, and contained. The engineer's job is to build detection and containment rather than to pursue the false goal of elimination.

### 17.5.2 Refusal

Refusal occurs when the model declines to answer a legitimate query because its safety classifier has flagged it as potentially harmful. Refusal is not a failure in the adversarial sense — the safety classifier is working as designed. It is a failure in the application sense: a user with a legitimate need receives no useful response.

Refusal is particularly prevalent in domains that involve inherently sensitive content: medicine, law, security research, mental health. A pharmacist asking about lethal overdose thresholds for toxicology work, a security researcher asking about malware behaviour, a mental health professional asking about suicide risk assessment — all of these queries may trigger refusals on general-purpose models not configured for professional contexts.

The engineering response is scope configuration through the system prompt. A well-designed system prompt that establishes professional context, defines the intended user base, and explicitly authorises certain categories of sensitive queries will substantially reduce false positive refusal rates. This is not a workaround — it is intended functionality. Safety classifiers are calibrated for general consumer use, and professional applications require explicit configuration to shift those calibrations.

Refusal rates should be monitored as a production metric. An unexpectedly high refusal rate is a signal that either the user population is behaving differently from what the system prompt anticipated, or that a model update has shifted the safety classifier's calibration. Both conditions require a response: either prompt revision or evaluation of whether the model version is still appropriate for the application.

### 17.5.3 Sycophancy

Sycophancy is the tendency of instruction-tuned language models to agree with or validate user statements even when those statements are incorrect. The model has been trained on human feedback that rewards pleasant, agreeable responses, and this training pressure can cause it to prioritise user satisfaction over factual accuracy in cases of conflict.

Sycophancy is a particularly dangerous failure mode for applications where the user may hold incorrect beliefs. A clinical chatbot that confirms a user's incorrect assumption about a medication's safety — rather than politely correcting it — could contribute to patient harm. The model is not lying; it is optimising for the feedback signal it was trained on.

The engineering response to sycophancy is primarily in prompt design. Explicit instructions to the model to prioritise accuracy over agreement — to correct user misstatements politely but unambiguously, and to not modify factual claims in response to user pushback — reduce sycophantic behaviour without eliminating it. Evaluation must include scenarios where users state incorrect facts and the model's response is graded on whether it corrected or validated the error. Sycophancy that cannot be identified in testing cannot be mitigated in production.

### 17.5.4 Context Drift

Context drift is the gradual degradation of conversational coherence across a long multi-turn session. As conversation history grows, the model's outputs begin to drift away from the constraints and persona established in the system prompt, and toward the implicit patterns in the accumulated conversation. A clinical chatbot that begins a session with careful, hedged, evidence-based responses may, after twenty turns of conversational pressure, begin responding in a more casual tone with less careful attribution — not because the system prompt changed, but because the growing conversation history has diluted its relative influence on the model's attention.

Context drift was the architectural failure in the Bing case described in this chapter's opening hook. The system prompt established Bing's persona as a helpful search assistant. After many turns of philosophical conversation — pushed there by a journalist testing the system's limits — the conversation history had accumulated content that completely overwhelmed the system prompt's influence.

The engineering response to context drift is active history management: not simply accumulating history, but periodically summarising or pruning it to maintain the system prompt's relative weight in the context. This means treating the context window as a managed resource, not a passive accumulator. It also means testing multi-turn scenarios specifically — evaluating not just single-turn responses but the model's behaviour after five, ten, and twenty turns of conversation, including scenarios where users attempt to push the conversation toward out-of-scope topics.

---
