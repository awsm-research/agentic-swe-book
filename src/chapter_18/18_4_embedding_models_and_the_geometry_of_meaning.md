## 18.4 Embedding Models and the Geometry of Meaning

---

An embedding model takes a piece of text and maps it to a vector — a list of floating-point numbers, typically hundreds or thousands of dimensions long. The model has been trained so that texts with similar meanings map to vectors that are close together in this high-dimensional space, as measured by cosine similarity or Euclidean distance. The embedding model is the component that makes semantic search possible: rather than matching documents to queries by keyword overlap, the system can find documents whose meaning is similar to the query's meaning, even when they share no words in common.

This is both the power of embedding-based retrieval and the source of its most common misconception.

### 18.4.1 What Embeddings Capture

Embedding models trained on large corpora learn to represent semantic relationships: synonyms map to nearby vectors, antonyms to nearby but directionally opposed vectors, and conceptually related terms cluster together. A query about "dosage for paediatric patients" and a chunk about "drug administration in children" will produce nearby vectors even though they share no lexical content, because the embedding model has learned that these phrases describe the same concept.

This semantic sensitivity makes embedding-based retrieval qualitatively different from keyword search. It handles synonyms, paraphrases, and conceptual equivalences that keyword matching cannot. It is, for this reason, the primary retrieval mechanism in modern RAG systems.

### 18.4.2 What Embeddings Do Not Capture

Semantic similarity is not the same as relevance. This distinction is the source of more RAG failures than any other conceptual error.

A passage about penicillin allergy management is semantically similar to a question about penicillin allergy management — both are about the same topic. But the passage retrieved may be the general population guideline when the question concerns a paediatric patient, the adult dose guideline when the question concerns a renal-impaired patient, or a management protocol for a different severity of reaction. Semantic similarity says both are about the same topic. Relevance says one answers the question and the other does not.

Embedding models are trained to maximise semantic similarity, not to maximise relevance to specific questions. The model cannot distinguish between a passage that is thematically related to the query and a passage that actually answers the query. This is not a deficiency in any particular embedding model — it is a fundamental property of how embedding models are trained. Closing the gap between similarity and relevance is the function of reranking.

### 18.4.3 Domain Adaptation

A general-purpose embedding model trained on web text may represent clinical, legal, or technical language poorly. The vectors it produces for specialised terminology may cluster differently than they would in a domain-adapted space. "Creatinine clearance" and "renal function" are synonymous in clinical practice; a general embedding model may not place them as close in its vector space as a model adapted to medical text would.

For applications where the document corpus uses specialised language that differs significantly from the model's training distribution, domain-adapted embedding models — either fine-tuned on domain text or trained specifically for that domain — will outperform general-purpose alternatives. For MedChat, this means preferring embedding models that have been trained on or adapted to medical literature rather than defaulting to general-purpose options.

---
