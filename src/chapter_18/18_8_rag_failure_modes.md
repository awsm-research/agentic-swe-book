## 18.8 RAG Failure Modes

---

Understanding what can go wrong in a RAG system — and precisely where in the pipeline each failure originates — is the foundation of RAG quality engineering. There are four primary failure modes. Each is distinct in its cause, its symptom, and its appropriate mitigation.

### 18.8.1 Retrieval Miss

A retrieval miss occurs when the relevant passage exists in the corpus but is not retrieved. The query phase returns a candidate set that does not include the chunk needed to answer the question.

Retrieval misses can be caused by a mismatch between the query's vocabulary and the chunk's vocabulary in the embedding space (the query uses different terminology than the document), by a chunking strategy that has buried the relevant information inside a chunk whose overall embedding is dominated by other content, by an incomplete corpus (the document was never ingested), or by ANN approximation error (the relevant vector was in the index but not returned in the approximate search).

The symptom of a retrieval miss is characteristically subtle: the model will answer the question using its parametric knowledge rather than retrieved context, producing an answer that may sound plausible but is not grounded in the authoritative source. In a clinical system, this may be indistinguishable from a correct answer in the model's phrasing while being factually wrong for the specific patient population.

Retrieval misses are the most damaging failure mode in high-stakes applications because they are silent. The pipeline does not signal that retrieval failed — it proceeds to generation with whatever was retrieved.

### 18.8.2 Retrieval Wrong

A retrieval wrong occurs when the retrieved passages are from the correct domain and appear topically related but do not answer the specific question. The most common cause is the precision-relevance distinction described in the previous section: vector retrieval optimises for semantic similarity, which can return passages that are about the same topic without addressing the specific aspect the question requires.

A retrieval wrong is more likely than a retrieval miss to be detectable, because the generated answer will often be inconsistent with the specific details of the question — the wrong patient population, the wrong drug class, the wrong severity of condition. But in complex questions, the inconsistency may be subtle enough to pass unnoticed.

The primary mitigation is reranking, which promotes answer-relevant passages over merely topically-relevant ones. Secondary mitigations include query refinement techniques (query decomposition, HyDE) that improve the specificity of the retrieval signal.

### 18.8.3 Hallucination Despite Retrieval

Hallucination despite retrieval is the failure mode where retrieval succeeds — the correct passages are retrieved and injected into the context — but the model generates an answer that departs from the retrieved context. The model substitutes its parametric knowledge for the explicitly provided evidence, producing an answer that contradicts or ignores the retrieved passages.

This failure mode is particularly concerning because it is invisible to the retrieval pipeline. Retrieval quality metrics will show the retrieval was correct; the failure occurs entirely in the generation step.

The causes include insufficiently clear prompting that does not explicitly instruct the model to base its answer on the provided context, retrieved passages that are long or complex enough that the model loses track of their content, and model training that has instilled strong parametric biases for certain types of answers. The mitigations are prompt engineering (explicit instructions to ground the answer in the context and attribute claims to sources), faithfulness evaluation (automated metrics that score whether the generated answer is supported by the retrieved passages), and human review pipelines for high-stakes outputs.

### 18.8.4 Context Overflow

Context overflow occurs when the retrieved chunks, combined with the system prompt and the user query, exceed the model's context window. Modern large language models have substantial context windows — many support 128,000 tokens or more — but this does not make context overflow irrelevant. The failure mode is more subtle than a hard truncation error.

Research consistently shows that large language models attend unevenly to content within their context window. Content at the beginning and end of the context is attended to more reliably than content in the middle — a phenomenon described by Liu et al. (2023) as the "lost in the middle" effect. A RAG system that retrieves fifteen chunks and concatenates them into a long context may effectively hide the most relevant passage in the middle, where the model is least likely to attend to it.

The mitigation is to retrieve fewer, better chunks rather than more chunks. The reranking stage should be calibrated to select three to five high-quality chunks rather than ten lower-confidence ones. Context window capacity is not a license to retrieve indiscriminately — it is a budget to be managed with the same discipline as any other resource.

---
