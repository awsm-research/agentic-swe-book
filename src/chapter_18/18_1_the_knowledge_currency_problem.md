## 18.1 The Knowledge Currency Problem

---

Every foundation model is trained on a static snapshot of the world. The training process concludes, the weights are frozen, and from that point forward the model's parametric knowledge — everything it knows from having seen the training corpus — does not change. The world continues to move. Guidelines are updated, policies are revised, products are launched and discontinued, regulations are amended, and scientific evidence accumulates. The model knows none of it.

This is the knowledge currency problem. It has two dimensions that engineers often conflate but which require different solutions.

The first dimension is temporal staleness. A model trained with a cutoff of mid-2024 has no knowledge of anything that occurred after that date. For many applications, this is tolerable. The fundamentals of software design patterns, the rules of SQL, or the principles of double-entry accounting have not changed materially since the model was trained. For others, it is intolerable. A clinical decision support system that does not know about a drug safety recall issued six months ago is dangerous.

The second dimension is organisational specificity. Even a model trained yesterday has no knowledge of your organisation's internal documents: your company's refund policy, your hospital's formulary, your legal team's contract clauses, your engineering team's architecture decisions. These documents were never in the training corpus. They will never be in any training corpus, because they are private, proprietary, or simply too specialised to appear in the kind of publicly available text that models are trained on. Temporal staleness can be addressed, in principle, by retraining. Organisational specificity cannot — the model will never have encountered your bereavement fare policy.

The instinctive engineering response to both dimensions is fine-tuning: take the pre-trained model and continue training it on your own documents, so that it internalises your specific knowledge. Fine-tuning has its place, but it is the wrong answer to the knowledge currency problem for three reasons.

First, fine-tuning trains the model to reproduce the *style* of your documents, not to recall their *facts* accurately. A fine-tuned model that has seen your refund policy documents will generate text that sounds like your refund policy. It will not reliably quote the actual terms and conditions, because the learning objective during fine-tuning rewards plausible generation, not factual recall. The result is a model that is more confidently wrong in a house style.

Second, fine-tuning does not enable source attribution. When the model answers a question about bereavement fares, you cannot point to the specific paragraph of the specific policy document that the answer came from. If the answer is disputed, there is no audit trail. In regulated domains — clinical, financial, legal — this absence of attribution is a compliance failure.

Third, fine-tuning is operationally expensive. Every update to your knowledge base requires a new training run, which takes compute time, costs money, and introduces the risk that the fine-tuning process degrades the model's other capabilities. An airline that updates its bereavement fare policy quarterly cannot afford a new fine-tuning run for each revision.

RAG resolves all three problems by separating the model from the knowledge. The model's weights do not change. The knowledge lives in an external, searchable corpus. When a question arrives, the relevant passages are retrieved from that corpus and placed directly in the model's context, alongside the question. The model's job is then not to recall facts from parametric memory but to reason over and communicate information that is explicitly present in the context. Updates to the knowledge base require only re-indexing the changed documents — a process that takes minutes, not days, and does not touch the model. Answers are attributable to specific retrieved passages. And the model's general capabilities remain intact.

The core architectural principle that follows from this is worth stating plainly: **in a RAG system, the retrieval pipeline, not the model, is the primary determinant of answer quality**. A retrieval pipeline that returns the wrong passages, or no passages, will produce wrong answers regardless of how capable the underlying model is. Engineering effort spent on model selection, prompt tuning, or inference optimisation is largely wasted if the retrieval pipeline is poor.

---
