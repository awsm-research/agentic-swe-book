## 21.2 The Unified LLM Gateway Pattern

---

In the early period of LLM adoption — roughly 2022 through 2024 — most engineering teams built direct integrations to a single model provider. A startup would pick OpenAI, wire its application to the OpenAI API, and ship. This approach works until it does not. And when it stops working, it stops working in ways that are expensive to fix.

Vendor lock-in with LLMs is more severe than it appears at first. It is not just about changing a base URL and an API key. Each provider uses different request schemas, different streaming protocols, different token-counting methods, different error codes, and different rate-limit headers. An application that has been built to assume OpenAI's conventions requires non-trivial re-engineering to switch to Anthropic, Google, or any open-weight model served on AWS Bedrock or Azure AI Foundry.

The **unified LLM gateway** pattern resolves this by introducing a single abstraction layer that sits between your application code and every model provider. Your application sends requests to the gateway in a normalised format. The gateway translates those requests into whatever format each provider requires, handles authentication, manages retries and fallbacks, and returns responses in a consistent schema.

LiteLLM is the most widely deployed open-source implementation of this pattern. It presents a single OpenAI-compatible interface that proxies to over 100 model providers, including Anthropic Claude, Google Gemini, AWS Bedrock, Azure OpenAI, Cohere, Mistral, Ollama for local models, and many others. An application configured to use LiteLLM can switch the underlying model by changing a single configuration parameter, without touching application code.

The gateway pattern delivers three production-critical capabilities beyond mere API normalisation.

**Fallback routing** allows the gateway to automatically reroute a request to a secondary provider when the primary is unavailable, rate-limited, or returning errors. For a production chatbot serving thousands of users, an outage at a single provider does not have to mean service downtime. The gateway detects the failure and transparently falls back to a configured alternative — potentially a different model from a different provider — within the same request lifecycle.

**Cost attribution** means that every token consumed, every request made, and every model invoked can be tagged with metadata — the user, the feature, the team, the experiment — so that cost can be understood and controlled at a granular level. Without this, you know your monthly bill but have no idea which feature, user cohort, or prompt template is responsible. With it, you can make intelligent decisions about where to invest in optimisation.

**Audit logging** at the gateway level captures a complete record of every interaction — request, response, latency, model used, and cost — without requiring every application component to implement its own logging. In regulated industries, this centralised audit trail is often a compliance requirement, not merely a nice-to-have.

The gateway also serves as the natural location for cross-cutting concerns: rate limiting, quota enforcement, authentication, and guardrail integration. Placing these concerns at the gateway rather than scattering them across application code ensures that they are consistently applied regardless of which part of the system issues a model request.

Teams that adopt the gateway pattern from the beginning — before they need it — find that switching providers, running A/B experiments across models, and controlling costs are all straightforward operational activities. Teams that skip the gateway pattern and build direct integrations almost always regret it when circumstances force a provider change.

---
