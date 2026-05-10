## 18.3 Chunking Strategies and Their Tradeoffs

---

Chunking is the first and, arguably, the most consequential decision in RAG pipeline design. The right chunking strategy is not a universal constant — it depends on the structure of the source documents, the nature of the expected queries, and the capacity of the context window. The wrong strategy makes retrieval systematically incorrect.

### 18.3.1 Fixed-Size Chunking

Fixed-size chunking divides a document into windows of N tokens, typically with an overlap of M tokens between adjacent windows to avoid losing information at boundaries. Values of 512 tokens with 50 tokens of overlap are common defaults.

Fixed-size chunking is simple to implement and consistent in behaviour — every chunk is approximately the same size, which simplifies the downstream pipeline. It is the appropriate default for unstructured documents without clear internal organisation: plain text, email archives, informal notes.

Its limitation is that it is semantically blind. A 512-token window placed arbitrarily may begin mid-sentence and end mid-paragraph, producing a chunk that lacks coherent context. The overlap partially mitigates this, but it does not resolve the fundamental problem that the boundaries are chosen based on token count rather than meaning.

### 18.3.2 Sentence-Boundary Chunking

Sentence-boundary chunking splits documents at sentence boundaries identified by a sentence tokeniser, grouping sentences into chunks until a token budget is reached. This produces chunks that at least respect the basic unit of natural language — the sentence — and avoids the problem of fragments.

Sentence-boundary chunking is better than fixed-size for well-written prose where sentences are the natural unit of information. It performs poorly on structured documents — tables, numbered lists, section hierarchies — where the sentence is not the meaningful unit and where splitting at sentence boundaries may separate a header from its content.

### 18.3.3 Semantic Chunking

Semantic chunking uses embedding similarity to identify topic shifts in a document. It embeds each sentence, computes the cosine similarity between adjacent sentence embeddings, and inserts a chunk boundary where similarity drops sharply — indicating a shift in subject matter. The result is chunks that are semantically coherent rather than merely syntactically complete.

Semantic chunking is more computationally expensive than the preceding approaches, requiring embedding at ingestion time as an intermediate step. It produces better chunk boundaries for documents with clear topic structure — a research article that moves from introduction to methodology to results will be split into thematically coherent sections. For documents with continuous, tightly interwoven content, the similarity-based boundary detection may produce erratic results.

### 18.3.4 Hierarchical Chunking

Hierarchical chunking recognises that documents often have structure at multiple levels simultaneously: a document has sections, sections have paragraphs, paragraphs have sentences. Rather than choosing one level, hierarchical chunking stores chunks at multiple levels and indexes them together. A retrieved chunk from a section summary can point to the paragraphs beneath it; a retrieved chunk from a paragraph can point to its parent section.

This approach is particularly valuable for long structured documents — clinical guidelines, legal contracts, technical specifications — where a question might be answerable from a single paragraph but where the surrounding section context is necessary to interpret that paragraph correctly. Hierarchical chunking allows the pipeline to retrieve the specific paragraph for precision and the section header for context simultaneously.

The tradeoff is complexity: the chunking logic is more involved, the schema for storing chunks and their relationships is more complex, and the retrieval and formatting logic must handle multi-level results. For a small corpus of simple documents, this complexity is not warranted. For MedChat's WHO clinical guidelines — structured, hierarchical, and requiring contextual interpretation — it is the correct choice.

### 18.3.5 The Fundamental Tradeoff

The core tension in chunking is between precision and context. Small chunks carry a strong, specific retrieval signal — the chunk is focused on one topic, so similarity to a query about that topic is high. But small chunks may lack the surrounding context needed to answer the question. Large chunks provide more context but dilute the retrieval signal and consume context window budget. The right chunk size is the smallest size at which the chunk is self-contained and interpretable without reference to its surroundings. For most structured documents, this is a paragraph or a section, not a sentence and not a page.

---
