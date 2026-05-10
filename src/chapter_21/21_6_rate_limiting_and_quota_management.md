## 21.6 Rate Limiting and Quota Management

---

Runaway cost is an existential risk for AI-native products. A 2024 Andreessen Horowitz analysis of early-stage AI startups found that inference costs consumed a median of 20–30% of gross revenue in products without deliberate usage controls — a proportion that makes commercial viability structurally impossible at scale. Rate limiting and quota management are the engineering controls that prevent this outcome.

**Provider-level rate limits** are imposed by the model provider and measured in requests per minute and tokens per minute. These limits are hard ceilings — requests that exceed them receive 429 errors. Engineering teams must understand their provider-level limits and design their systems to operate within them, including handling 429 errors gracefully with exponential back-off and retry logic. LiteLLM handles much of this automatically, including routing to a fallback provider when the primary provider's rate limit is exhausted.

**Application-level rate limits** are the controls you impose on your own users. These are independent of provider limits and are configured to protect your budget and ensure fair access across your user population. A clinical chatbot that allows any authenticated user to issue unlimited queries is vulnerable to accidental or intentional abuse. Sensible application-level rate limits might restrict each user to a maximum number of queries per minute and a maximum token expenditure per day, with different limits for different user tiers.

**Quota management** operates at a coarser granularity than rate limiting. Where rate limits govern the rate of consumption at any instant, quotas govern total consumption over a period — a monthly token budget per team, a maximum spend per feature, or a per-user monthly allowance. Quota management systems must track consumption in real time, provide visibility to both users and administrators, and enforce hard or soft stops when budgets are approached.

The gateway is the natural enforcement point for both rate limits and quotas. Because all model traffic passes through the gateway, it has complete visibility into consumption by user, feature, and model tier. Rate-limit and quota decisions can be made at the gateway without requiring any application-level code changes.

**Cost alerting** is a lightweight complement to hard limits. Cost alerts notify administrators when expenditure crosses configured thresholds — 50% of monthly budget consumed, an unusual spike in requests per minute, cost per user exceeding historical norms. Alerts allow human intervention before hard limits are reached, which is particularly important in contexts where hard limits would degrade user experience.

Rate limits and quotas require a clear distinction between per-user limits and system-wide limits. A system-wide limit consumed by one heavy user effectively rate-limits all other users. Per-user limits protect system resources while ensuring that one user's behaviour cannot degrade the experience for others.

---
