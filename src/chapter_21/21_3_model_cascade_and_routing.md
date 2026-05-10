## 21.3 Model Cascade and Routing

---

The most cost-effective serving architectures do not send every query to the best available model. They route each query to the cheapest model capable of handling it adequately, and escalate to more capable — and more expensive — models only when necessary. This is the **model cascade** pattern.

The intuition behind cascades is that most production query traffic is dominated by routine, well-scoped requests. In a clinical chatbot, the majority of queries might be questions about appointment booking, prescription refill procedures, or clinic contact information. A small fraction will be complex clinical questions requiring genuine medical reasoning. Sending all of these to the same frontier model treats a question about opening hours with the same computational and financial weight as a question about drug interaction risks. That is not engineering — it is waste.

A cascade architecture defines multiple tiers of model capability and routes each incoming query to the appropriate tier. The routing decision is made based on signals about query complexity, and the routing logic can be implemented at several levels of sophistication.

**Rule-based routing** is the simplest approach. It classifies queries by explicit criteria: query length, keyword presence, topic category, or user tier. Queries below a token-length threshold go to a cheap model; queries above it escalate. Queries containing certain keywords — medication names, dosage questions, symptom descriptions — route directly to the capable model. Rule-based routing is fast, deterministic, and auditable, which matters in regulated environments. Its weakness is brittleness: rules require maintenance, and they miss edge cases that do not match their explicit criteria.

**Classifier-based routing** uses a lightweight machine learning model to predict query complexity. The classifier is typically a small, fast embedding-based model trained to distinguish simple queries from complex ones. It adds a few milliseconds of overhead but produces more accurate routing decisions than hand-written rules. The classifier itself must be maintained and retrained as query distributions shift — it is a model that governs other models, which introduces its own operational responsibility.

**Speculative routing** sends the query to a cheap model first and evaluates the response quality before deciding whether to escalate. If the cheap model's response meets a quality threshold — assessed by a separate evaluator model, by perplexity, or by length and coherence heuristics — the response is returned. If not, the query escalates to the capable model, which now has the cheap model's response as additional context. This approach has the advantage of actually observing output quality before committing to escalation cost, but it adds latency for the fraction of queries that escalate, because the cheap model's processing time is added to the capable model's processing time.

**Confidence-based escalation** is a variant in which the serving model itself is asked to assess its confidence in its response. This is unreliable for frontier models, which are notoriously poorly calibrated in their self-assessments — they express high confidence even when wrong. Confidence-based escalation should be treated as a supplement to other routing signals, not as a primary mechanism.

The engineering challenge in cascade design is selecting the right quality threshold for escalation. A threshold set too low causes over-escalation — too many queries reach the expensive model, costs rise, and the cascade provides no real savings. A threshold set too high causes under-escalation — complex queries receive inadequate responses from cheap models, and quality degrades. Calibrating this threshold requires measurement: you need a dataset of labelled queries with known quality expectations, and you need to track escalation rates and quality metrics in production.

The MedChat clinical chatbot described in section 21.10 uses a three-tier cascade: a small, locally hosted model handles intake and routing classification, a mid-tier cloud model handles most clinical information requests, and a frontier model handles complex cases that require multi-step medical reasoning or involve safety-critical decisions. Escalation is logged and reviewed by the clinical governance team as part of their quality assurance process.

---
