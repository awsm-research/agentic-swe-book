## 17.4 Token Economics

---

LLM API providers charge per token. This is not primarily an accounting detail — it is an engineering constraint that shapes system design in ways that parallel how memory constraints shaped systems design in earlier computing eras. The engineer who does not have a clear mental model of token costs will build systems that are technically correct and economically unsustainable.

### 17.4.1 Input Tokens and Output Tokens

Providers charge separately for input tokens — the text sent to the model — and output tokens — the text the model generates. Output tokens are consistently priced higher than input tokens, typically by a factor of three to five, because generation is computationally more expensive than processing. This asymmetry has architectural implications that are not obvious at first.

The first implication is that making the model produce shorter outputs is more cost-effective than making it produce shorter inputs. A prompt that instructs the model to be concise, to omit explanatory preamble, and to produce a structured answer rather than a prose essay can reduce output token costs significantly — often by 40–60% — without reducing the informativeness of the response. Prompt design that optimises for output length is a legitimate architectural lever.

The second implication is that input token costs, while lower per token, accumulate at scale. A system prompt that grows over iterations — as new constraints and behaviours are added — becomes increasingly expensive at production query volumes. A system prompt that costs 500 tokens per query at $2.50 per million input tokens costs $0.00125 per query. At 100,000 queries per day, that is $125 per day for the system prompt alone. Every 100 tokens added to the system prompt adds $25 per day at that volume. These numbers are small individually but illustrate why token efficiency in prompt design is an engineering concern, not an aesthetic one.

### 17.4.2 Architectural Choices and Their Cost Implications

Every architectural choice has a token cost signature. More retrieved passages mean more input tokens but potentially higher answer quality. Longer conversation history means more input tokens but better multi-turn coherence. More sophisticated output formats — structured JSON with metadata fields — may mean more output tokens but enable better downstream processing. Chain-of-thought prompting — instructing the model to reason step by step before answering — produces longer outputs but frequently improves accuracy on complex tasks.

The engineer's job is to understand which of these tradeoffs are worth making for the application's domain. For a low-stakes FAQ bot, minimal retrieved context, concise prompts, and aggressive history truncation are appropriate. For a clinical decision support system where an incorrect answer could affect patient safety, the calculus shifts: additional retrieved context that increases confidence in the answer, longer prompts that enforce careful reasoning, and more generous output limits that allow the model to hedge appropriately are worth their cost.

Token economics also determine the feasibility of caching. Semantic caching — storing the output of queries similar to ones already answered and serving the cached output to similar new queries — can dramatically reduce costs for applications with predictable query patterns. A clinical FAQ system where the same fifty questions are asked repeatedly by different users is an ideal candidate for semantic caching. An open-ended clinical consultation tool where every query is genuinely novel is not.

---
