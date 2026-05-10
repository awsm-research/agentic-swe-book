# Chapter 21: LLM Serving, Cost Engineering, and Deployment

> *"The art of progress is to preserve order amid change, and to preserve change amid order."*
> — Alfred North Whitehead

---

In November 2023, a European financial services firm (a composite illustrative case representative of a failure pattern that recurs across deployments) deployed a customer-facing chatbot built on a frontier language model. Within seventy-two hours, the monthly API budget — allocated for an entire quarter — was exhausted. The culprit was not malicious use or a runaway loop. It was a combination of verbose system prompts, no caching layer, and a user population that treated the chatbot as a general-purpose search engine rather than a scoped assistant. The model returned detailed, multi-paragraph responses to every query, including trivial ones like "What are your opening hours?" The firm's engineers had focused almost entirely on response quality during development and had given almost no thought to the economics of operating at scale. They had built something that worked beautifully in a demo and nearly bankrupted its own pilot.

---
