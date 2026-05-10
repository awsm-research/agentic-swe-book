## Learning Objectives

By the end of this chapter, you will be able to:

1. Explain why LLM evaluation is fundamentally harder than traditional ML model evaluation, and identify the specific properties of LLM outputs that make standard evaluation approaches insufficient.
2. Describe why reference-based metrics such as BLEU and ROUGE are inadequate for evaluating open-ended generation, and explain what they measure versus what they miss.
3. Explain the four core RAGAS metrics — faithfulness, answer relevancy, context precision, and context recall — including what each measures, what each misses, and how to interpret them together for a RAG pipeline.
4. Describe the LLM-as-judge approach: its strengths, its systematic biases, and the conditions under which it can and cannot be trusted.
5. Explain when human evaluation is necessary, how to design annotation rubrics, and why inter-annotator agreement is an essential quality check on human judgements.
6. Distinguish between static and dynamic evaluation datasets and explain why contamination risk is a first-order concern in LLM evaluation.
7. Define red teaming as a systematic engineering practice and explain how to design adversarial test cases for a safety-critical LLM application.
8. Determine which quality checks belong in automated CI/CD quality gates and which require human judgement before deployment.

---
