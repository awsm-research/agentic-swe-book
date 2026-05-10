## 17.6 The Three-Way Tradeoff: Latency, Cost, and Quality

---

Every LLM architecture decision sits within a three-dimensional space defined by latency, cost, and output quality. These three dimensions are not independent: optimising any one typically requires accepting degradation in at least one of the others. This tradeoff is not unique to LLM systems, but its specific shape in LLM applications differs from anything in traditional software.

**Latency** is the time between a user's query and the application's response. For interactive applications, latency directly affects user experience. Clinicians asking time-sensitive questions during patient consultations have much lower latency tolerance than researchers conducting literature reviews. Latency in LLM applications is driven primarily by model size (larger models are slower), context length (longer contexts are slower), and output length (more tokens generated means more time). The LLM API call is typically the dominant latency contributor — database queries, embedding calls, and network overhead are small by comparison.

**Cost** is the token-denominated expense of each query. At low query volumes, cost is often irrelevant to architectural decisions. At production scale — thousands or tens of thousands of queries per day — it becomes a first-order concern. Cost is driven by model choice, context length, and output length. The cost difference between the largest and smallest capable models is often an order of magnitude, which motivates model cascade strategies: routing simpler queries to smaller, cheaper models and reserving expensive models for complex or high-stakes queries.

**Quality** in LLM applications is multidimensional: factual accuracy, appropriate hedging, correct citation, adherence to scope, clinical safety in medical applications. Quality is improved by using larger models, providing more retrieved context, using lower temperature settings that reduce variance, and employing chain-of-thought prompting that improves reasoning on complex queries. All of these choices increase cost and latency.

The tradeoff is not a choice made once at system design time. It is a choice made for each query type in the application. A clinical chatbot might route straightforward drug dosage questions — where the answer is factual and well-defined — to a smaller model with a minimal prompt, while routing complex differential diagnosis questions to the largest available model with extensive retrieved context. This routing architecture requires an orchestration layer that can classify query complexity and apply different cost-quality profiles accordingly, but it may reduce overall query cost by 60–70% while preserving full quality on the queries that require it.

The important engineering discipline is to make this tradeoff deliberately, not to accept the default that all queries use the same model with the same prompt. The default is neither the cheapest option nor the highest-quality option — it is the most convenient option for a prototype, and prototypes are not production systems.

---
