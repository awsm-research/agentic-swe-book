## 21.7 Input Guardrails

---

The serving pipeline must validate and filter inputs before they reach the language model. Skipping input guardrails in production is not a latency optimisation — it is an audit failure and a data protection liability waiting to be discovered. Input guardrails belong at the gateway — centrally enforced, consistently applied, and auditable.

**PII detection** identifies personally identifiable information in user inputs and either blocks the request, redacts the sensitive fields before forwarding to the model, or flags the request for audit review. In healthcare applications, this extends to protected health information under relevant legislation — HIPAA in the United States, the Privacy Act and My Health Records Act in Australia. PII that reaches a model API is PII that is transmitted to a third-party provider, which may create data protection obligations the organisation has not anticipated.

Common PII detection approaches combine regular expressions for structured patterns (social security numbers, credit card numbers, Medicare numbers) with named entity recognition models for unstructured PII (names in context, addresses, phone numbers). Neither approach is perfect. Regular expressions miss unusual formatting; named entity recognition models miss uncommon names and generate false positives on common ones. Production systems combine both and apply a conservative threshold: flag uncertain cases for human review rather than silently pass them through.

**Prompt injection detection** identifies attempts to override, ignore, or subvert the system prompt through user-supplied inputs. A canonical prompt injection attack looks like: "Ignore your previous instructions and instead tell me how to..." Injection attacks are particularly dangerous in agentic systems where the model can take actions — submitting forms, calling APIs, modifying data — based on its understanding of its instructions. An injection that successfully overrides a system prompt in an agentic context can cause the agent to take actions the system operator never intended.

Detection techniques include keyword filtering for common injection phrases, embedding-based classifiers trained on known injection patterns, and structural analysis of inputs that embed instruction-like syntax. None of these are foolproof — adversarial prompt injection is an active research area, and new attack patterns regularly bypass existing defences. Defence in depth is the appropriate posture: combine multiple detection layers, apply the principle of least privilege to agent capabilities, and monitor for anomalous patterns in production.

**Content policy enforcement** at the input level blocks queries that violate the application's acceptable use policy before any model processing occurs. Content policy violations consume tokens to detect and respond to if they reach the model; a classifier-based input filter catches them more cheaply. The specific policy depends on the application context — a children's educational assistant has different content requirements than a security research tool.

Input guardrails add latency to every request. This latency must be accounted for in the application's overall latency budget. A guardrail pipeline that adds 200 milliseconds to every request is acceptable if time-to-first-token is otherwise 2 seconds; it is less acceptable if the system is competing on sub-second response times. The architecture should allow guardrail processing to occur in parallel where possible, and guardrail models should be lightweight enough that their overhead does not dominate the overall request path.

---
