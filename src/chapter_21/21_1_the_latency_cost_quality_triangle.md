## 21.1 The Latency–Cost–Quality Triangle

---

Every decision in LLM serving is a negotiation between three variables: latency, cost, and output quality. The uncomfortable truth is that you cannot optimise all three simultaneously. Improving any one of them typically requires accepting a trade-off in at least one of the others. This is not a temporary limitation of current technology — it is a structural property of how large language models are priced, sized, and served.

**Quality** in an LLM context refers to the accuracy, depth, and reliability of model outputs. Larger models with more parameters tend to produce better outputs on complex tasks. They also cost more per token and take longer to generate a response. Smaller models are faster and cheaper but perform worse on tasks that require reasoning, nuanced judgement, or specialised knowledge.

**Cost** scales primarily with token volume — both input tokens (your prompt) and output tokens (the model's response). But it also scales with model tier. A response from GPT-4o costs an order of magnitude more than the same response from GPT-4o Mini. The cost structure means that prompt design, model selection, and output length all directly affect operating expenditure, not just engineering quality.

**Latency** is driven by model size, infrastructure, and whether the serving infrastructure is pre-warmed. Frontier models on cloud APIs introduce 2–10 seconds of time-to-first-token for complex queries. For conversational applications, that latency is the difference between a user who feels heard and one who feels like they are waiting for a slow web page from 2003.

The triangle manifests in real engineering decisions:

| Decision | Wins | Loses |
|---|---|---|
| Switch to a smaller model | Cost, Latency | Quality |
| Increase output length limits | Quality | Cost |
| Cache responses aggressively | Cost, Latency | Quality (stale responses) |
| Use streaming | Perceived Latency | Architecture Complexity |
| Route simple queries to cheap models | Cost, Latency | Uniformity |

Teams that understand this triangle make deliberate trade-offs. Teams that do not end up discovering their trade-offs the expensive way, as the European bank did.

The practical implication is that LLM serving architecture is not a technology problem with a correct answer — it is an economics problem with a cost function. Your job as an AI-native engineer is to understand your application's actual requirements and build a serving stack that makes the right trade-offs for your context, not the ones that look impressive in a benchmark.

---
