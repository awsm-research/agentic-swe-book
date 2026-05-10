## 21.11 Key Takeaways

1. **The latency–cost–quality triangle is a structural constraint, not a temporary limitation.** Every serving architecture makes explicit or implicit trade-offs across these three dimensions. The job of the AI-native engineer is to make those trade-offs deliberately and in alignment with product requirements.

2. **The unified LLM gateway pattern is non-negotiable for production systems.** Direct provider integrations create vendor lock-in, fragment observability, and scatter cross-cutting concerns across application code. LiteLLM and equivalent gateways provide fallback routing, cost attribution, and audit logging at a single centralised point.

3. **Model cascades reduce cost without sacrificing quality where it matters.** Routing simple queries to cheap models and escalating complex queries to capable ones is the primary lever for operating an LLM application economically at scale. Cascade design requires measurement: escalation rates, quality metrics, and cost per tier must be tracked continuously.

4. **Cost engineering is a first-class discipline.** Token budgeting, prompt compression, semantic caching, provider-level prompt caching, and batch processing are not premature optimisation — they are the practices that determine whether an AI product is commercially viable.

5. **Streaming is the correct default for interactive applications.** Users experience time-to-first-token as the system's responsiveness. Streaming optimises the metric that users perceive, even when total generation time is unchanged. Streaming requires always-on deployment and changes the architecture of guardrail pipelines.

6. **Rate limiting and quota management prevent existential cost events.** Every production LLM application needs both provider-level back-off logic and application-level per-user quotas. Without them, a single heavy user or runaway process can exhaust a budget planned for thousands of users.

7. **Input guardrails belong at the gateway.** PII detection, prompt injection classification, and content policy enforcement are cross-cutting concerns that should be enforced once, centrally, rather than replicated across every application component.

8. **Output guardrails require contextual calibration.** Hallucination detection, citation verification, and dangerous content filtering reduce risk but cannot eliminate it. In high-stakes domains, guardrails are one layer within a governance framework that includes human oversight, not a substitute for it.

9. **Serverless deployment is inappropriate for latency-sensitive, streaming LLM applications.** Cold-start latency and streaming timeout constraints make always-on container infrastructure the correct default for interactive serving. Serverless remains appropriate for asynchronous batch workloads.

10. **Serving architecture is an economic and governance problem, not merely a technical one.** The right design is determined by who bears the cost of failure, what regulatory obligations apply, and what the product's actual latency and quality requirements are — not by what is technically most sophisticated.

---

### Review Questions

1. A health insurance company is launching an AI assistant that answers member queries about coverage and claims. Their engineering team proposes sending all queries to the most capable available model to maximise response quality. Using the latency–cost–quality triangle, critique this proposal and describe an alternative architecture that achieves adequate quality at a sustainable cost.

2. A startup has built its chatbot with a direct integration to the OpenAI API. Six months into production, the CEO learns that Anthropic has released a model that would reduce inference costs by 40% for their primary use case. The engineering lead estimates a two-week migration. Identify the specific engineering decisions that created this migration cost and describe how a unified gateway architecture would have changed the situation.

3. MedChat's input guardrail pipeline adds an average of 180 milliseconds of overhead to every request. The clinical informatics director argues this overhead is unacceptable and wants to remove PII detection to improve response time. As the lead engineer, construct an argument for retaining PII detection that addresses both the technical and governance dimensions of the decision.

4. A team is designing the output guardrail pipeline for a financial services chatbot that streams responses to advisers. They need to screen every response for regulatory compliance violations, but their compliance classifier requires the complete response text to operate. Describe at least two architectural approaches to this problem and analyse the trade-offs each involves.

5. A company's nightly document summarisation pipeline processes 15,000 contract documents and currently costs approximately AUD$3,200 per month using a synchronous frontier model API. Identify at least three cost engineering interventions that could reduce this cost, and estimate the likely impact of each.

6. After deploying its LLM gateway with per-user monthly token quotas, a B2B SaaS company discovers that five enterprise accounts are consistently exhausting their quotas by the second week of every month, generating support complaints. Using the rate limiting and quota management principles from this chapter, describe how you would redesign the quota system to address this pattern without degrading experience for heavy but legitimate users.

---
