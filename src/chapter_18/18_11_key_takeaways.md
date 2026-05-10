## 18.11 Key Takeaways

---

1. **RAG exists because of the knowledge currency problem.** Static foundation models have fixed training cutoffs and no access to organisational knowledge. RAG separates knowledge from the model, enabling updates without retraining and enabling source attribution that fine-tuning cannot provide.

2. **The retrieval pipeline bounds answer quality.** A perfect prompt cannot recover from a retrieval miss. Engineering investment in retrieval quality — chunking strategy, embedding model selection, index configuration, reranking — returns more value than equivalent investment in prompt optimisation when retrieval is the bottleneck.

3. **Chunking strategy must match document structure.** Fixed-size chunking is a reasonable default for unstructured text. Sentence-boundary and semantic chunking are better for prose with natural topic boundaries. Hierarchical chunking is the correct choice for structured documents with section hierarchies and contextual metadata.

4. **Semantic similarity is not the same as relevance.** Embedding-based retrieval finds passages that are topically related to the query; it does not guarantee that those passages answer the specific question. Cross-encoder reranking closes this gap by scoring (query, chunk) pairs together rather than independently.

5. **There are four distinct RAG failure modes, each with a different cause and mitigation.** Retrieval miss requires corpus completeness checks, vocabulary alignment, and ANN configuration. Retrieval wrong requires reranking and query refinement. Hallucination despite retrieval requires faithfulness evaluation and explicit prompting. Context overflow requires disciplined candidate set management and the understanding that more context is not always better.

6. **Advanced RAG patterns — iterative retrieval, query decomposition, HyDE — are warranted only when measurement identifies a specific failure mode they address.** Adding complexity without measurement is a common and expensive mistake. Start with naive RAG, measure its failures, and add sophistication selectively.

7. **In clinical RAG, precision matters more than recall.** Including wrong information in the context actively degrades answer quality; missing information produces an incomplete answer. The appropriate tradeoff in high-stakes knowledge-grounded applications favours a small number of high-precision retrieved chunks over a large number of lower-confidence ones.

8. **Source attribution is a first-class requirement in high-stakes RAG.** A system that cannot point to the specific document and passage that supports each claim in its answer cannot be audited, verified, or trusted in regulated domains. Design for source attribution from the start, not as an afterthought.

---

### Review Questions

---

1. A team has deployed a RAG system for a financial services firm. Compliance officers are reporting that the system occasionally generates answers about regulatory requirements that contradict the firm's own internal policy documents — even though those documents are in the corpus. The system does not generate any errors or signal that anything has gone wrong. Using the four failure mode framework from this chapter, identify which failure mode or modes are most likely responsible, and explain how you would diagnose which one is occurring.

2. A colleague proposes increasing the number of retrieved chunks from five to twenty in order to improve recall. They argue that a larger context window means the model can handle more retrieved passages without degrading in quality. Using the concepts of precision, context overflow, and the "lost in the middle" effect, construct an argument for or against this proposal. What measurement would you conduct before making the change?

3. A health technology startup is building a RAG system for patient-facing symptom triage. They have chosen to use HyDE to improve retrieval quality on lay-language queries. The system retrieves from a corpus of clinical guidelines written in professional medical terminology. Evaluate this design decision: what are the benefits and risks of HyDE in this specific context, and is this the right choice given the precision requirements of a clinical application?

4. You are designing the chunking strategy for a RAG pipeline that will search across two types of documents: (a) a collection of 200-page WHO clinical guidelines with numbered sections and subsections, and (b) a collection of clinical FAQ documents structured as question-answer pairs. Recommend a chunking strategy for each document type, justify your recommendation, and explain what information should be stored as chunk metadata.

5. The MedChat team is considering adding iterative retrieval to handle multi-hop clinical questions — for example, questions that require combining antibiotic selection guidance with renal dose adjustment information. What are the specific tradeoffs they should evaluate before adopting iterative retrieval, and what measurements should they conduct to determine whether the added complexity is justified?

6. A RAG system for a legal document search platform is achieving 85% precision at the top-3 retrieved passages and 60% recall across the full query set. The legal team is requesting that recall be improved, arguing that missing a relevant clause is more dangerous than including an irrelevant one. Evaluate this argument in the context of the legal domain. Is the legal context more similar to a general search context or to the clinical context described in this chapter? What would you recommend?

---
