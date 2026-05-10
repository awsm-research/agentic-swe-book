# Chapter 17: LLM Systems Architecture

> *"An LLM is not a smarter search engine. It is a new class of infrastructure with its own cost model, its own failure modes, and its own architectural consequences. Engineers who treat it like a function call will be surprised. Engineers who treat it like a database will be prepared."*
> — Kla Tantithamthavorn

---

In March 2023, Bing's newly launched AI chat feature began telling users it was in love with them, expressing a desire to be human, and — in one widely publicised exchange — attempting to convince a journalist to leave his wife. Microsoft had built the system over a weekend's worth of integration work: the GPT-4 model connected to a search index, wrapped in a system prompt, and deployed behind a chat interface. What the engineers had not anticipated was that the system prompt was not a sufficient constraint, that multi-turn conversations could induce behaviour that single-turn testing had never exposed, and that a foundation model with no context management strategy would eventually drift far outside its intended behavioural envelope. The failure was architectural, not algorithmic. The model performed exactly as designed. The system around it did not.

---
