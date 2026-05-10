## 17.9 API-First Design: Shifted Engineering Responsibilities

---

Building on foundation model APIs rather than self-hosted models reorganises engineering responsibility at every layer of the stack.

When a team trains and hosts its own model, they are responsible for everything: the training data, the model architecture, the training procedure, the weights, the serving infrastructure, and the model's behaviour. When a team builds on a foundation model API, the model provider is responsible for the weights, the training procedure, and the base serving infrastructure. The team is responsible for everything that wraps the model: the prompt layer, the retrieval layer, the orchestration layer, and the guardrail layer. The team cannot inspect the model's internals, cannot change how it was trained, and cannot predict exactly how it will respond to novel inputs.

This redistribution of responsibility has five concrete consequences.

**The model can change without your code changing.** Foundation model providers update their models — improving capabilities, adjusting safety calibrations, fixing known issues. These updates can silently change your application's behaviour. A prompt that worked reliably with one model version may behave differently with the next. Pinning to specific, dated model versions — and running your evaluation suite against each new version before upgrading — is an operational necessity, not a preference.

**You cannot debug the model's internals.** When a traditional software system produces unexpected output, you can add logging, inspect intermediate state, and trace the execution path. When a foundation model produces unexpected output, you cannot inspect its internal computation. Your only tool is probing: providing more inputs, varying the context, and observing the pattern of outputs. This demands a well-designed evaluation suite that can expose model behaviour systematically.

**The model's failure modes are not fully documented.** Every production LLM application will encounter edge cases that the model's documentation did not describe. Hallucination rates, refusal thresholds, and sycophancy patterns vary across model versions and across input domains in ways that are not fully characterised in provider documentation. Red teaming — systematically attempting to elicit harmful or incorrect behaviour — must be part of the pre-deployment engineering process.

**The model is a shared resource with external failure modes.** Rate limiting, latency spikes, and service outages at the model provider directly affect your application. The engineering responses — exponential backoff, request queuing, fallback model routing, graceful degradation — are the same engineering responses applied to any external dependency. An LLM API should be treated with the same resilience engineering discipline as a third-party payment processor or a cloud database: not assumed to be always available, always within latency bounds, or always correctly priced.

**Provider economics change.** Model pricing has been on a consistent downward trajectory as providers compete and as inference efficiency improves. An architecture designed around today's pricing may need to be revisited as prices change. The model cascade strategy — routing to cheaper models for simpler queries — should be designed with the expectation that the relative economics of available models will shift over the system's operational lifetime.

API-first design shifts the engineering frontier from model development to application design. The team that builds on foundation model APIs has no control over the core intelligence of their system.

---
