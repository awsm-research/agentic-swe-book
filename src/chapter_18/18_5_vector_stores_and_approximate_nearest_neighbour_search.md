## 18.5 Vector Stores and Approximate Nearest-Neighbour Search

---

Once chunks have been embedded, their vectors must be stored in a structure that allows efficient similarity queries. The naive approach — computing the cosine similarity between the query vector and every stored chunk vector — works for small corpora but becomes computationally prohibitive at scale. A corpus of one million chunks requires one million vector dot products per query, which translates to unacceptable latency for an interactive system.

Vector stores solve this problem by building an index that allows approximate nearest-neighbour (ANN) search: finding the vectors most similar to the query vector without exhaustively checking every stored vector.

### 18.5.1 HNSW Indexing

The most widely deployed ANN index structure is Hierarchical Navigable Small World (HNSW) graphs. HNSW builds a layered graph where each node is a vector and edges connect vectors that are close to each other in the space. The graph has multiple layers: upper layers are sparse and enable coarse navigation; lower layers are dense and enable fine-grained search. At query time, the search starts in the upper layer, navigates toward the approximate neighbourhood of the query vector, then descends to lower layers for refinement.

HNSW delivers sub-millisecond query times on corpora of millions of vectors. The tradeoff is that it is approximate — it finds vectors that are very close to the nearest neighbours, but not guaranteed to be the absolute nearest neighbours. The approximation error is configurable through index construction parameters: higher accuracy requires more memory and slower index construction but produces results closer to exact nearest-neighbour search.

### 18.5.2 What This Means for RAG Engineering

The approximation property of ANN search has a practical implication that is easy to overlook: at the edges of the similarity distribution, the index may miss the technically most similar vector in favour of one that is nearly as similar. For a retrieval pipeline where the correct chunk is the single most similar vector in the index, this can cause retrieval misses in edge cases.

The mitigation is to retrieve more candidates than you plan to use — retrieve the top twenty or fifty candidates from the index rather than the top five — and then apply a more accurate relevance model to re-order them. This is the role of reranking, covered in the next section.

The choice of vector store — pgvector for PostgreSQL, Pinecone, Weaviate, Chroma, Qdrant, and others — is a deployment concern that does not materially affect the conceptual architecture. What matters is that the index supports the distance metric used during embedding (cosine similarity or dot product), that the ANN configuration balances accuracy and latency appropriately for the application, and that the store supports metadata filtering so that retrieval can be scoped to relevant subsets of the corpus.

### 18.5.3 Hybrid Retrieval

Dense vector retrieval excels at semantic generalisation — finding passages that are conceptually related to the query even when they share no exact words. It is weaker on precise lexical lookup: a query containing a drug name, a product identifier, or a regulatory code will often be better served by a sparse retrieval method such as BM25, which scores passages by term frequency and inverse document frequency rather than vector similarity.

Production RAG systems routinely fuse both signals. A hybrid retrieval stage runs dense vector search and BM25 in parallel, then combines their ranked lists — typically using Reciprocal Rank Fusion (RRF) or a learned weighting — before passing the merged candidate set to the reranker. The dense signal covers paraphrase and synonymy; the sparse signal covers exact-match terms that the embedding model may not distinguish from semantically similar but incorrect alternatives. MedChat, for example, benefits from sparse retrieval when queries include specific drug names or ICD-10 codes that must match precisely rather than approximately.

---
