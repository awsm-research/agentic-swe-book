## 18.7 Reranking: Why Retrieval Alone Is Insufficient

---

Vector retrieval, for all its power, has a fundamental architectural limitation: the embedding model is applied to the query and to each chunk independently, and similarity is computed post hoc from the resulting vectors. The embedding model has never seen the query and the chunk together when computing their representations. It cannot model the specific relationship between them — it can only compare their independent representations.

Reranking corrects this limitation.

### 18.7.1 Bi-Encoders vs. Cross-Encoders

The architecture used for vector retrieval is called a bi-encoder: one encoder processes the query, another (or the same) encoder processes each document chunk, and similarity is computed from the resulting independent embeddings. Bi-encoders are computationally efficient because the chunk embeddings can be computed offline and cached; only the query embedding is computed at query time.

The architecture used for reranking is called a cross-encoder: the query and the candidate chunk are concatenated and processed together by the model, which produces a single relevance score for the (query, chunk) pair. Because the model sees both the query and the chunk simultaneously, it can model their specific relationship rather than their independent similarity. Cross-encoders are substantially more accurate than bi-encoders for relevance scoring.

The tradeoff is compute time. A cross-encoder must process each (query, chunk) pair separately; you cannot pre-compute chunk representations and cache them. This makes cross-encoders too slow for first-stage retrieval — you cannot run a cross-encoder over a million chunks at query time — but feasible for reranking a small candidate set of twenty to fifty chunks that vector retrieval has already surfaced.

### 18.7.2 What Reranking Adds

Reranking adds the ability to score chunks based on their specific relevance to the query rather than their general semantic similarity to it. A cross-encoder reranker applied to twenty candidate chunks will promote the chunk that directly answers the question over the chunk that is topically related but only tangentially useful. It will recognise that a chunk about antibiotic dosing in renal impairment is more relevant to a question about renal-impaired patients than a chunk about antibiotic dosing in the general population, even if both are semantically similar to the query.

Adding reranking to a vector retrieval pipeline produces measurable precision gains at the cost of additional latency — usually tens to hundreds of milliseconds, depending on the number of candidates and the size of the reranker. For most applications, this tradeoff is clearly worthwhile. For real-time applications with strict latency budgets, the number of candidates to rerank must be tuned carefully.

The important engineering discipline here is to measure the improvement. Reranking should not be added on the assumption that it helps — it should be added after measuring baseline retrieval quality, and its contribution should be quantified. A reranker that does not improve precision at the top of the list is a latency cost with no benefit.

---
