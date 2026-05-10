## 18.10 The MedChat Case Study: Retrieval Precision in a Clinical Context

---

MedChat is a clinical question-answering system that retrieves information from a corpus of clinical guidelines, drug reference documents, and hospital protocols. Its RAG pipeline illustrates a set of design decisions that differ from those appropriate for a general-purpose enterprise knowledge base, because the tradeoffs in a clinical context are different from those in most other applications.

### 18.10.1 Why Precision Matters More Than Recall

The conventional wisdom in information retrieval is that recall is more important than precision in most applications: it is better to show users ten results and let them find the relevant one than to show three results and miss the relevant one. This wisdom does not apply to clinical question-answering.

A clinician asking about antibiotic selection at 2am will read the retrieved passages and the generated answer, not a list of ten results of varying quality. The presence of irrelevant or misleading passages in the context actively degrades answer quality, because the language model may incorporate information from those passages into the answer. A retrieved chunk about the adult dose of an antibiotic, placed alongside a question about a paediatric patient, may cause the model to output the adult dose — not despite having retrieved the right information, but because it also retrieved the wrong information.

In clinical RAG, the correct retrieved passages must be the ones that actually reach the context window. Precision at the top of the reranked list is the primary retrieval quality metric. Recall failures — missing a relevant passage — are less dangerous than precision failures — including a misleading passage — because missing information produces an incomplete answer, while including wrong information produces an actively incorrect one.

### 18.10.2 MedChat's Retrieval Design

This precision-first principle drives MedChat's specific design choices.

MedChat uses hierarchical chunking for its structured clinical guidelines, preserving section headers and document hierarchy as metadata alongside each chunk. This ensures that a retrieved chunk about antibiotic dosing is always accompanied by the section context identifying whether it applies to adult patients, paediatric patients, or a specific renal function category — context that flat chunking strategies would lose.

MedChat retrieves a moderately sized candidate set from the vector index — twenty candidates rather than the maximum the index supports — and applies a domain-adapted cross-encoder reranker to that set. The reranker is calibrated to favour specificity over topical coverage: a chunk that directly answers the specific question beats a chunk that comprehensively covers the broader topic.

MedChat limits the final context to the top three reranked chunks. Three chunks at high precision outperform five or ten chunks at lower precision, both because the model attends more reliably to a shorter context and because the lower-precision chunks at positions four through ten introduce noise. The three-chunk limit is not arbitrary — it reflects a measurement of where the quality of the reranked candidates drops below the precision threshold needed for safe clinical use.

Source attribution is mandatory in MedChat's generation template. The prompt explicitly instructs the model to attribute every factual claim to a specific retrieved passage, and the system displays the source document and section alongside every answer. A clinician can verify the source of every statement. This design choice is a direct consequence of the clinical context: when an answer cannot be attributed to a source, the clinician must treat it as uncertain and verify independently.

### 18.10.3 What MedChat Does Not Do

Understanding MedChat's design choices also requires understanding what was deliberately excluded.

MedChat does not use iterative retrieval by default. The additional latency of multiple retrieval passes is incompatible with the use case of a clinician asking a question under time pressure. For the complex multi-hop questions where iterative retrieval would add value, MedChat's approach is to detect when the retrieved context is insufficient and return an explicit "insufficient information" response rather than a synthesised guess. A correct "I don't have enough information to answer that" is safer than a plausible but incorrect synthesis.

MedChat does not use HyDE. The hypothetical document generation step introduces the risk that parametric knowledge contaminates the retrieval query, which in a clinical context is precisely the failure mode RAG is designed to prevent. The system is designed to ground answers in retrieved evidence, not to reason from the model's prior beliefs — and HyDE, by using the model's prior beliefs to generate the retrieval query, partially undermines this principle.

These exclusions are not permanent architectural decisions. They reflect the specific constraints and risk tolerances of the clinical use case at a particular point in the system's development. As evaluation data accumulates and the failure mode profile of the system becomes clearer, these decisions will be revisited.

---
