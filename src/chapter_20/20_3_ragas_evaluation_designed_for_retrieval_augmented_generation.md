## 20.3 RAGAS: Evaluation Designed for Retrieval-Augmented Generation

Retrieval-Augmented Generation (RAG) systems — systems that retrieve relevant passages from a document corpus and use them to ground an LLM's responses — introduce an evaluation challenge that generic metrics do not address. You cannot evaluate a RAG system solely on the quality of its final answers, because the quality of the answer depends on the quality of the retrieval that produced it. A perfect answer to the question asked may be grounded in retrieved documents that were retrieved incorrectly or incompletely. A poor answer may reflect a good retrieval but a poor generation. Understanding the failure mode requires evaluating both.

RAGAS (Retrieval-Augmented Generation Assessment), introduced by Es et al. in 2023, provides four metrics specifically designed to decompose RAG pipeline quality into its component parts: faithfulness, answer relevancy, context precision, and context recall. Each metric isolates a different failure mode. Together, they provide a diagnostic picture of where a RAG pipeline is failing and why.

### 20.3.1 Faithfulness

Faithfulness measures whether the claims in the generated answer are supported by the retrieved context. The metric decomposes the generated answer into atomic claims — individual factual assertions — and checks whether each claim can be inferred from the retrieved passages. A faithfulness score of 1.0 means every claim in the answer is grounded in the retrieved context. A score of 0.7 means roughly 30 percent of the claims in the answer are not supported by anything that was retrieved.

Faithfulness is the primary hallucination detection metric for RAG systems. Low faithfulness means the model is generating claims beyond what the retrieved context supports — either inventing facts, drawing on training data not present in the corpus, or confabulating. For MedChat, a faithfulness score below 0.85 on the evaluation set is grounds for blocking deployment, because it means the system is making clinical claims that its sources do not support.

What faithfulness misses: it evaluates only whether claims are supported by the retrieved context, not whether the retrieved context itself is correct. If the corpus contains an outdated clinical guideline recommending an obsolete treatment, and the model faithfully summarises that guideline, faithfulness will be high and the answer will still be clinically wrong. Faithfulness is a necessary condition for safety in a RAG system, not a sufficient one.

### 20.3.2 Answer Relevancy

Answer relevancy measures whether the generated answer is actually responsive to the question that was asked. The metric works by generating multiple hypothetical questions from the answer — questions that the answer could plausibly be responding to — and measuring the similarity between those hypothetical questions and the actual question posed. If the answer is genuinely responsive to the question, the hypothetical questions it implies should resemble the question asked. If the answer is off-topic, technically correct but irrelevant, or comprehensive but unfocused, the hypothetical questions it implies will diverge from the question asked. (Note: RAGAS implementations have evolved; later versions assess answer relevancy via direct LLM judgement rather than hypothetical question generation. The underlying principle — does the answer address the question? — is stable across versions.)

Answer relevancy catches a failure mode that faithfulness does not: an answer can be entirely grounded in retrieved context and still fail to address what the clinician asked. A clinician who asks "what is the correct dose of amoxicillin for a five-year-old with otitis media?" and receives a technically faithful but unfocused response covering the general pharmacology of penicillins has received a low-relevancy response regardless of its factual grounding.

What answer relevancy misses: it does not evaluate completeness. An answer that is perfectly responsive to the question but omits critical information will score well on relevancy. It also does not evaluate accuracy — a relevant but factually incorrect answer scores well.

### 20.3.3 Context Precision

Context precision evaluates whether the passages that were actually used to construct the context were relevant to the question. This metric requires a ground-truth answer as reference. It asks: of the passages that were retrieved and included in the context, which were actually needed to answer the question? High context precision means the retrieval system returned focused, relevant passages. Low context precision means the context window was polluted with irrelevant passages that could distract the generation model, increase cost, and dilute the signal from genuinely relevant material.

For MedChat, low context precision is a retrieval architecture problem. It typically indicates that the embedding model is not capturing clinical domain semantics accurately, that the similarity threshold is set too permissively, or that chunking strategy is creating passages that mix relevant and irrelevant content in ways that fool the retrieval system.

What context precision misses: it measures whether the retrieved passages were relevant, but not whether the most relevant passages were retrieved. A system that retrieves five moderately relevant passages when one highly relevant passage exists elsewhere in the corpus may score well on context precision while failing on context recall.

### 20.3.4 Context Recall

Context recall measures whether the retrieved context covered all the information necessary to answer the question. The metric requires a ground-truth answer and checks whether the claims in that reference answer are supported by the retrieved passages. Low context recall means the retrieval system failed to retrieve some of the information needed — there are claims in the correct answer that appear nowhere in the retrieved context.

Context recall sets a ceiling on answer quality. If the information needed to answer a question correctly is not in the retrieved context, the model cannot produce a fully correct answer without hallucinating — and hallucinating would lower faithfulness. A system with low context recall and high faithfulness is a system that is faithfully summarising incomplete information, which is precisely the failure mode of the radiology summarisation system described in this chapter's opening.

What context recall misses: it requires a ground-truth answer, which is expensive to obtain and may not be available for production traffic. It also reflects the quality of the corpus itself — if the correct answer requires information that is not in the document collection at all, context recall will be low regardless of how well the retrieval system works.

### 20.3.5 Interpreting RAGAS Metrics Together

The four RAGAS metrics are diagnostic when read together, not individually. The patterns they form indicate where the RAG pipeline is failing:

A system with low faithfulness and high context recall indicates a generation problem: the information was retrieved correctly but the model is not staying grounded in it, or is supplementing retrieved information with hallucinated content.

A system with high faithfulness and low context recall indicates a retrieval problem: the model is faithfully summarising what it retrieved, but the retrieval missed crucial information. The answers are internally consistent but incomplete.

A system with low context precision indicates a retrieval quality problem: the context is polluted with irrelevant passages. This may manifest as lower faithfulness (the model hallucinates by drawing on irrelevant retrieved content) or lower answer relevancy (the irrelevant context dilutes the model's focus).

A system with high scores on all four metrics for an evaluation dataset that is small or non-representative may still fail on production traffic that covers edge cases the evaluation dataset does not. RAGAS scores are upper bounds on production quality when the evaluation dataset is a good sample of production traffic; they are not guarantees.

---
