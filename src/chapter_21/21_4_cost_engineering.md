## 21.4 Cost Engineering

---

Cost engineering for LLM applications is a discipline in its own right. It encompasses everything from how you write prompts to how you schedule batch workloads — all with the goal of reducing token expenditure without eroding output quality. The firms that build commercially viable AI products treat cost engineering with the same seriousness they apply to database query optimisation or network egress reduction.

### 21.4.1 Token Budgeting

Every prompt has an implicit cost: the number of tokens consumed by the system prompt, the conversation history, the user query, and the model's response. In a long conversation, context accumulates rapidly. A chatbot with a 2,000-token system prompt and a conversation that has run for twenty turns may be sending 8,000–10,000 input tokens with every new query — even if the user's latest message is six words long.

Token budgeting means actively managing context size. Common techniques include truncating conversation history beyond a fixed window, summarising older turns into compressed representations, and selectively including only the most relevant prior context rather than everything. The right strategy depends on whether conversation continuity matters — a customer support bot needs recent context more than it needs the opening pleasantries from twelve turns ago.

Output token budgets are equally important. Many models can be instructed to limit response length through system-prompt directives, and most APIs accept a `max_tokens` parameter. Setting an appropriate output budget prevents runaway responses where the model interprets an open-ended question as an invitation to write an essay.

### 21.4.2 Prompt Compression

System prompts in production applications frequently balloon over time. The initial version is concise. Then a bug is fixed by adding a clarifying sentence. Then a new capability is added with its own instructions. Then an edge case is patched with an exception. After six months, a system prompt that started at 300 tokens has grown to 2,000. Every request now carries this overhead.

Prompt compression audits treat the system prompt as a first-class engineering artefact. The audit removes redundant instructions, consolidates overlapping directives, and tests whether the compressed version produces equivalent outputs on a regression test suite. In practice, well-audited prompts can often be reduced by 30–50% with no measurable degradation in output quality.

Beyond manual compression, there are automated approaches: prompt distillation techniques can reduce natural-language instructions to shorter representations that encode the same semantic content. These techniques are an active research area; the tooling is maturing but not yet standardised.

### 21.4.3 Caching

Caching is the single highest-leverage cost-reduction technique available for most production LLM applications.

**Exact-match caching** stores the complete response for a given request and returns the cached response when an identical request arrives again. It is highly effective for queries with deterministic inputs: status checks, FAQ responses, templated reports. It is less effective for conversational applications where queries are unique even when they express the same underlying intent.

**Semantic caching** extends exact-match caching by treating queries as semantically equivalent if their embedding representations are sufficiently similar. A semantic cache stores query embeddings alongside their responses and returns a cached response when a new query falls within a configurable similarity threshold of a cached query. This dramatically increases cache hit rates for natural-language interfaces where users phrase the same question in different ways. The challenge is threshold calibration: too generous a threshold and semantically different queries receive the same cached response, degrading quality; too strict and the hit rate collapses to that of exact-match caching.

Both caching strategies must account for time-sensitivity. A cached response to "What is today's clinic schedule?" is only valid for the day it was generated. Cache invalidation for LLM applications follows the same principles as cache invalidation for any system — and remains equally hard to get right.

Provider-level prompt caching, now offered by several major providers including Anthropic and OpenAI, caches the key-value computation for repeated prompt prefixes at the inference layer. When the same system prompt prefix is reused across many requests — as it is in almost every production deployment — provider-level caching reduces input token costs for that prefix by 50–90%. This is one of the most impactful and underused cost-reduction techniques available in 2025.

### 21.4.4 Batching

Not all LLM workloads are interactive. Document analysis pipelines, overnight report generation, data enrichment workflows, and evaluation harnesses all involve processing large volumes of inputs where latency is not the primary concern.

For these workloads, batching dramatically reduces cost. Most providers offer batch APIs that process requests asynchronously and return results within a defined window — typically 24 hours. Batch pricing is typically 50% of synchronous pricing for the same model. A nightly pipeline that processes 10,000 documents pays half the price of the same pipeline run interactively.

The engineering implication is that workload classification matters. Before routing a workload to the standard synchronous API, ask whether the consumer of the result actually needs it in real time. If the result feeds a report that runs at midnight, a batch job is both cheaper and architecturally simpler.

---
