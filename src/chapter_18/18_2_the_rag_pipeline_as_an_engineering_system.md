## 18.2 The RAG Pipeline as an Engineering System

---

RAG is not a single technique — it is a pipeline of engineering stages, each of which introduces its own failure modes and quality tradeoffs. The pipeline has two phases: an offline ingestion phase that processes documents into a searchable index, and an online query phase that retrieves from that index at inference time.

The ingestion phase runs once at setup and is re-run whenever the document corpus changes. The query phase runs for every user request. The quality of every query response is bounded by decisions made during ingestion.

Understanding the pipeline as an engineering system — with clearly defined stages, quality metrics, and failure modes — is the foundation of RAG engineering. Engineers who treat RAG as a simple "add documents to a database and query it" operation consistently produce systems that fail in production in predictable ways.

### 18.2.1 The Ingestion Phase

The ingestion phase has three stages: chunking, embedding, and indexing.

**Chunking** divides source documents into segments of manageable size. The output is a set of text chunks, each with associated metadata identifying its source document, position, and any structural context.

**Embedding** transforms each chunk into a vector representation — a point in a high-dimensional space — using an embedding model. Two chunks that are semantically similar will produce vectors that are close to each other in that space. The output is a set of (chunk, vector) pairs.

**Indexing** stores the vectors in a data structure that enables efficient similarity search. The output is a vector index from which the nearest neighbours of any query vector can be retrieved quickly.

### 18.2.2 The Query Phase

The query phase has four stages: query embedding, retrieval, reranking, and generation.

**Query embedding** transforms the user's question into a vector using the same embedding model used during ingestion. This is critical: the query and the chunks must be embedded in the same vector space for similarity to be meaningful.

**Retrieval** finds the chunks whose vectors are most similar to the query vector. The output is an ordered list of candidate chunks, ranked by similarity score.

**Reranking** applies a more powerful relevance model to the candidate chunks to re-order them. The output is a refined list of top-k chunks, where k is typically small (three to ten chunks).

**Generation** formats the top-k chunks into a context string, which is injected into the prompt alongside the user's question. The language model generates an answer grounded in that context.

### 18.2.3 What Can Go Wrong at Each Stage

Every stage is a potential point of failure. Understanding where failures originate is essential for diagnosing and improving a RAG system.

At the **chunking** stage, chunks that are too small lose surrounding context and produce retrieval signals that are too weak to surface the right document. Chunks that are too large dilute the relevance signal and consume context window budget without adding proportional value. Chunks that straddle semantic boundaries — where a single chunk contains both the question and the answer from a FAQ, or both the dose and the contraindication from a drug guideline — may retrieve correctly but mislead the model.

At the **embedding** stage, the choice of embedding model determines the geometry of the vector space. A model trained on general web text may not represent clinical terminology, legal language, or technical specifications as accurately as a domain-adapted model. Two phrases that are synonymous in clinical practice may be far apart in a general embedding space, causing retrieval to miss the relevant chunk.

At the **indexing** stage, the choice of index structure determines the accuracy and speed of retrieval. An index that has been poorly configured — wrong distance metric, wrong number of neighbours — will return plausible-looking results that are subtly wrong. An index that has not been updated after new documents were added will miss those documents entirely.

At the **retrieval** stage, the nearest-neighbour results may not be the most relevant results. Similarity in vector space captures semantic overlap, but relevance to a question requires more than semantic overlap — it requires that the retrieved passage actually answers the question, not merely shares vocabulary with it.

At the **reranking** stage, errors compound. If retrieval has already missed the relevant chunk, reranking cannot recover it — you can only reorder what was already retrieved. A reranker applied to a poor initial retrieval set is rearranging the wrong documents.

At the **generation** stage, the model may fail to follow the retrieved context even when retrieval was correct — preferring its parametric knowledge to the explicitly provided passages. This is hallucination despite retrieval, and it is a failure mode that is easy to miss because the answer may sound correct.

---
