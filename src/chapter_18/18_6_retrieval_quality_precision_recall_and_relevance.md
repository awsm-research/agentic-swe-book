## 18.6 Retrieval Quality: Precision, Recall, and Relevance

---

Retrieval quality is measured along three dimensions: precision, recall, and relevance. These three dimensions are distinct, they can be measured independently, and they are in tension with each other. Understanding that tension is essential for making principled tradeoffs in RAG system design.

**Precision** measures what fraction of the retrieved chunks are actually useful for answering the query. A retrieval set with high precision contains mostly relevant chunks. A retrieval set with low precision contains many chunks that are about the same topic as the query but do not contribute useful information — they add noise to the context and consume tokens.

**Recall** measures what fraction of the chunks in the corpus that would be useful for answering the query have actually been retrieved. A retrieval set with high recall misses few relevant chunks. A retrieval set with low recall may have retrieved only some of the passages needed to answer the question completely.

**Relevance** is a more nuanced dimension than precision or recall. A chunk can be topically related to the query (high similarity, high precision) without actually answering the question. The distinction between topical relevance and answer relevance is the difference between a chunk that is about paediatric antibiotic dosing and a chunk that contains the specific dose for the specific antibiotic the question asks about. Embedding-based retrieval optimises for topical relevance; answer relevance requires additional ranking.

Three retrieval-layer metrics are standard when measuring these dimensions: **Hit@k** measures whether at least one relevant chunk appears in the top-k retrieved results — a binary per-query measure of recall at a given depth; **MRR@k** (Mean Reciprocal Rank) measures the average reciprocal rank of the first relevant result across queries, rewarding pipelines that surface the correct chunk early; and **NDCG@k** (Normalised Discounted Cumulative Gain) accounts for graded relevance, giving more credit to highly relevant chunks ranked higher in the list. Chapter 20 covers these metrics in detail alongside end-to-end RAG evaluation frameworks such as RAGAS.

### 18.6.1 The Precision-Recall Tradeoff

Precision and recall trade off against each other in retrieval systems. Retrieving more chunks improves recall — you are less likely to miss a relevant passage — but reduces precision, because the additional chunks are progressively less similar to the query and progressively more likely to be noise. Retrieving fewer chunks improves precision but risks recall failures.

This tradeoff is typically managed by separating retrieval into two stages: a high-recall, lower-precision first stage (vector retrieval) that retrieves a large candidate set, and a high-precision, lower-recall second stage (reranking) that selects the best candidates from the set. The first stage casts a wide net; the second stage picks the right fish from those caught.

### 18.6.2 The Relevance-Precision Distinction in Practice

A retrieval pipeline optimised for precision can still fail on relevance. Consider a question about the recommended first-line antibiotic for community-acquired pneumonia in a patient with renal impairment. Vector retrieval may surface several chunks about community-acquired pneumonia treatment — all highly similar to the query. Reranking may correctly promote chunks about first-line antibiotics over chunks about supportive care. But if the corpus does not contain a chunk that specifically addresses the intersection of first-line choice and renal impairment, or if that chunk was not retrieved in the first stage, the pipeline will return relevant-looking chunks that do not actually answer the question. The answer generated from those chunks may be plausible but incorrect for this specific patient.

This failure mode — retrieval of topically relevant but not specifically answering passages — cannot be resolved by improving the retrieval pipeline alone. It requires either a richer corpus (more specific passages) or a generation step that correctly reasons about the gaps in the retrieved context rather than filling them with parametric knowledge.

---
