## 21.8 Output Guardrails

---

Input guardrails protect the model from malicious or inappropriate inputs. Output guardrails protect users and the organisation from problematic model outputs. Both are necessary; neither substitutes for the other.

**Hallucination detection** is the most technically challenging output guardrail to implement reliably. Language models generate plausible-sounding text that may be factually incorrect — and they do not reliably flag their own uncertainties. Hallucination is not a bug that can be patched; it is a structural property of how these models generate text. Guardrails can only reduce its impact, not eliminate it.

Practical hallucination detection heuristics include:

- Grounding checks that compare assertions in the model's response against a retrieved knowledge base. If the response makes a claim that cannot be supported by the retrieved context, the claim is flagged.
- Consistency checks that query the model multiple times with the same question and flag responses that are inconsistent with each other. High variance across runs indicates low confidence.
- Cross-reference verification that checks specific factual claims — drug names, dosages, regulatory thresholds — against structured knowledge sources.

None of these approaches are comprehensive. Grounding checks only work when relevant grounding documents exist; many queries have no ground truth to check against. Consistency checks add latency and cost proportional to the number of verification runs. Cross-reference verification requires carefully curated knowledge sources and cannot generalise beyond their coverage.

In clinical applications like MedChat, hallucination risk is managed through a combination of Retrieval-Augmented Generation to ground responses in verified clinical content, structured response formats that separate factual claims from reasoning, mandatory source citation, and human-in-the-loop review for high-stakes outputs. The guardrail architecture cannot be treated as a substitute for clinical oversight — it is a risk-reduction layer within a broader governance framework.

**Source citation verification** checks that citations provided in model responses — journal references, regulatory documents, clinical guidelines — actually exist and support the claims attributed to them. Models trained on large corpora sometimes generate plausible-sounding but nonexistent citations, a failure mode sometimes called citation hallucination. Verification requires resolving the citation against an authoritative source and checking at minimum that the document exists; more rigorous verification checks that the cited claim is supported by the document.

**Dangerous content filtering** at the output level scans model responses for content that should never be delivered to users regardless of the model's interpretation of the prompt: self-harm content, detailed instructions for violence or illegal activity, discriminatory language, or — in a paediatric application — content inappropriate for children. Output content filtering is typically implemented using a combination of classifier models and rule-based keyword detection, with the classifier catching contextual nuance that keyword matching misses.

Output guardrails face a fundamental tension with streaming. A response that is being streamed token-by-token cannot be fully evaluated for policy compliance until the complete response is available, by which time the initial tokens have already been delivered to the user. Solutions include buffering a fixed window of tokens before streaming begins (adding latency), running guardrails on completed sentences or paragraphs rather than complete responses (reducing buffer size), or accepting that early tokens carry guardrail latency and optimising subsequent token delivery. There is no perfect solution — the right choice depends on the relative importance of latency and safety for the specific application.

---
