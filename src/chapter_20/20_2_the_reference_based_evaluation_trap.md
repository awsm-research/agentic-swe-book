## 20.2 The Reference-Based Evaluation Trap

BLEU and ROUGE are the most widely cited metrics in natural language processing evaluation. They appear in thousands of papers. They are implemented in every standard NLP toolkit. They are almost entirely inappropriate for evaluating open-ended LLM generation, and using them as if they were sufficient is one of the most common and consequential mistakes in LLM quality engineering.

### 20.2.1 What BLEU and ROUGE Measure

BLEU (Bilingual Evaluation Understudy) was designed in 2002 to evaluate machine translation. It measures the n-gram overlap between a generated text and a reference translation — the fraction of word sequences in the generated text that also appear in the reference. A high BLEU score means the generated text uses similar word sequences to the reference. A low BLEU score means it does not.

ROUGE (Recall-Oriented Understudy for Gisting Evaluation) was designed to evaluate automatic summarisation. It measures the overlap of n-grams, word sequences, and longest common subsequences between generated summaries and reference summaries. High ROUGE scores indicate that the generated summary contains words and phrases that appear in the reference.

Both metrics are reference-based: they require a human-written reference to compare against, and they measure surface similarity to that reference. This is appropriate for tasks where the output space is narrow — translation between two languages has a small set of semantically equivalent correct translations — and where surface form carries meaning. It is inappropriate for tasks where the output space is large, where paraphrase is common, and where meaning and correctness are separable from the specific words used.

### 20.2.2 Why They Fail for Open-Ended Generation

Consider a clinical Q&A system asked: "What are the first-line treatments for community-acquired pneumonia in an otherwise healthy adult?" A correct answer might discuss amoxicillin or a macrolide antibiotic depending on local resistance patterns, recommend a five-day course, and note when to escalate. If the reference answer uses "amoxicillin" and the generated answer uses "amoxycillin" (the British spelling), BLEU penalises the response. If the reference says "macrolide antibiotic" and the generated answer names azithromycin specifically, BLEU penalises the response. If the generated answer is clinically superior to the reference — more current, more complete, better sourced — BLEU has no way to know and may score it lower.

More fundamentally, BLEU and ROUGE cannot distinguish between a response that is wrong and a response that is correct but phrased differently. They measure text, not truth. A response that confidently states an incorrect drug dose but uses words similar to the reference will score higher than a response that correctly describes the treatment using different terminology. For a clinical application, this is not just a measurement failure — it is a patient safety risk masquerading as an evaluation.

### 20.2.3 The Continuing Misuse

Despite these well-documented limitations — limitations that the original BLEU paper explicitly acknowledged — BLEU and ROUGE continue to be reported in LLM evaluation papers and system benchmarks because they are fast, cheap, and produce numbers that are easy to compare. A team that reports a 3-point BLEU improvement has said nothing about whether their system's outputs are more correct, more useful, or safer. The number exists. It is not evidence of quality. Teams building production LLM applications who rely on BLEU and ROUGE as primary quality signals are measuring the wrong thing with great confidence.

The appropriate use of reference-based metrics for LLM evaluation is narrow: they can be one signal among many for tasks where surface form genuinely matters (constrained format generation, templated outputs, structured extractions where terminology is fixed). They should not be the primary or sole evaluation signal for any open-ended generation task.

---
