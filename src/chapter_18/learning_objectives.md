## Learning Objectives

By the end of this chapter, you will be able to:

1. Explain the knowledge currency problem in static foundation models and articulate why RAG is architecturally superior to fine-tuning for knowledge-grounded applications.
2. Describe the full RAG pipeline — chunk, embed, index, retrieve, rerank, generate — and identify what can fail at each stage.
3. Compare chunking strategies — fixed-size, sentence-boundary, semantic, and hierarchical — and select the appropriate strategy for a given document type.
4. Explain what embedding models produce, how approximate nearest-neighbour search works, and why semantic similarity is not the same as relevance.
5. Distinguish retrieval precision, recall, and relevance, and explain why they conflict in practice.
6. Explain what cross-encoder reranking adds to the pipeline and why retrieval alone is insufficient.
7. Identify and reason about the four primary RAG failure modes: retrieval miss, retrieval wrong, hallucination despite retrieval, and context overflow.
8. Compare naive RAG with advanced patterns — iterative retrieval, query decomposition, and HyDE — and identify when each pattern is warranted.
9. Reason about why retrieval precision is more important than recall in a clinical context such as MedChat.

---
