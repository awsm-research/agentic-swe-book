## 18.9 Naive RAG vs. Advanced RAG Patterns

---

The pipeline described so far — chunk, embed, index, retrieve, rerank, generate — is often called naive RAG. It is naive not in the pejorative sense but in the sense of being a single, linear pass: one retrieval step, one generation step, no iteration. For many applications, naive RAG is sufficient and should be the starting point. For complex queries, multi-hop reasoning, and ambiguous questions, it fails in predictable ways that motivate more sophisticated patterns.

### 18.9.1 When Naive RAG Fails

Naive RAG fails on three classes of questions.

The first is multi-hop questions that require synthesising information from multiple documents. "What is the recommended antibiotic for community-acquired pneumonia, and how should the dose be adjusted for a patient with a creatinine clearance below 30ml/min?" requires retrieving both the antibiotic recommendation and the renal dose adjustment protocol, from potentially different parts of the corpus. A single retrieval step may surface one but not both.

The second is questions where the user's query is ambiguous or poorly formulated. A query phrased vaguely will produce a vague retrieval signal, and the resulting chunks may not address what the user actually needed. Users asking clinical questions at 2am are not always formulating precise, well-structured queries.

The third is questions about topics that are distributed across the corpus without any single chunk that directly addresses the question. A question about a policy that is discussed in fragments across multiple documents will retrieve fragments, not a coherent answer.

### 18.9.2 Iterative Retrieval

Iterative retrieval runs the retrieval and generation steps in a loop. After the first retrieval and generation pass, the system evaluates whether the answer is complete and uses any identified gaps to formulate a second retrieval query. This continues until the answer is judged complete or a maximum number of iterations is reached.

Iterative retrieval handles multi-hop questions well: the first pass retrieves the antibiotic recommendation; the generation step identifies that dose adjustment information is needed; the second pass retrieves the renal adjustment protocol; the final generation step synthesises both. The cost is latency — each iteration adds a retrieval and a generation step, which can be significant in real-time applications.

### 18.9.3 Query Decomposition

Query decomposition addresses ambiguous and complex queries by breaking the original question into a set of simpler sub-questions before retrieval. Each sub-question is answered independently through its own retrieval and generation pass, and the sub-answers are then synthesised into a final answer.

This pattern is most effective when the original question has clear, separable components. It adds latency proportional to the number of sub-questions but tends to produce more accurate and more complete answers on complex queries than naive single-pass retrieval. The decomposition step itself can be performed by the language model, using a prompt that instructs it to identify the sub-questions.

### 18.9.4 HyDE: Hypothetical Document Embeddings

HyDE (Gao et al., 2022) addresses the vocabulary mismatch problem from a different direction. Rather than embedding the user's query and retrieving similar chunks, HyDE first generates a hypothetical document that would answer the question — using the language model in generation mode before retrieval — and then embeds that hypothetical document as the retrieval query.

The reasoning is that the hypothetical answer, generated in the model's domain language, may be a better match to the embedding space of the corpus than the user's original question. A clinical question phrased in lay terms ("what should I give someone with a chest infection and a penicillin allergy?") may retrieve less effectively than a hypothetically generated clinical document phrased in clinical terminology ("Management of community-acquired pneumonia in penicillin-allergic patients: doxycycline 200mg loading dose...").

HyDE is most valuable when the user's vocabulary differs significantly from the document corpus's vocabulary, and when the corpus is large enough that vocabulary mismatch is a primary source of retrieval misses. Its risk is that the hypothetical document may contain errors from the model's parametric knowledge, which could bias retrieval toward wrong passages. This risk can be partially mitigated by generating multiple hypothetical documents and averaging their embeddings, but the fundamental limitation remains.

### 18.9.5 Choosing the Right Pattern

The decision of whether to use naive RAG or an advanced pattern should be driven by measurement rather than assumption. Start with naive RAG, measure its retrieval and generation quality using the evaluation frameworks described in Chapter 20, and then identify the failure modes it exhibits. If retrieval misses are the primary failure, investigate HyDE or query decomposition. If multi-hop reasoning failures are dominant, investigate iterative retrieval. Adding complexity that addresses a failure mode you have not measured is a common and costly mistake in RAG engineering.

Advanced patterns add latency, operational complexity, and additional points of failure. They are warranted when naive RAG's measured failure rate on important query types exceeds an acceptable threshold. They are not warranted simply because the queries seem complex in principle.

---
