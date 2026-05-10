# Chapter 22: Agent Fundamentals — The ReAct Loop, Tools, and Memory

> *"The question of whether machines can think is about as interesting as the question of whether submarines can swim."*
> — Edsger W. Dijkstra

---

In March 2023, a lawyer named Steven Schwartz submitted a legal brief to a federal court in New York. The brief cited more than six cases in support of his client's position. Every one of those cases was fictitious — hallucinated, in detail, by ChatGPT. Schwartz had asked the model to find supporting case law. The model obliged. It invented plausible-sounding citations with real-seeming docket numbers, convincing judicial language, and entirely fabricated outcomes. Schwartz did not verify a single one. He later told the court he had been unaware that ChatGPT could fabricate cases that did not exist. The court was not sympathetic. He was fined and faced professional sanctions. The failure was not a curiosity — it was a preview of what happens when a language model is treated as an autonomous agent without the architecture required to make autonomous agency safe. A real agent, properly designed, would have verified each citation against an authoritative legal database before including it in the brief. The tool call would either have returned a confirmed record or returned nothing. The hallucination would have been stopped cold.

---
