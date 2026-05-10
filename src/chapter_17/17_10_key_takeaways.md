## 17.10 Key Takeaways

---

1. **Software 3.0 shifts engineering focus from training to prompting.** The engineer no longer owns the model's weights. Engineering responsibility concentrates on the application layer: the prompt, retrieval, orchestration, and guardrail layers that wrap a foundation model the team does not control.

2. **The LLM application stack has four distinct layers, each with a distinct engineering responsibility.** The prompt layer defines the model's behaviour; the retrieval layer provides factual grounding; the orchestration layer manages the flow and state of interactions; the guardrail layer enforces safety and quality constraints on outputs. Omitting any layer creates a specific class of production failure.

3. **Context windows are finite budgets, not free storage.** Context length drives both cost and latency. The lost-in-the-middle problem (Liu et al., 2023) means that information placement within the context affects model attention and response quality. Context allocation must be deliberate and token-budgeted before any application code is written.

4. **Token economics shape architecture.** Output tokens cost more than input tokens. Token costs at production scale motivate model cascades, semantic caching, prompt efficiency, and concise output formatting. Engineers who do not model token costs at design time will face unsustainable economics in production.

5. **LLM failure modes are qualitatively different from traditional software failures.** Hallucination, refusal, sycophancy, and context drift require application-layer engineering responses — not debugging in the traditional sense. Each failure mode has a specific engineering mitigation that must be designed into the system from the outset.

6. **The latency–cost–quality tradeoff must be managed per query type, not set once globally.** Applying the same model, prompt, and context allocation to all queries is neither the most economical nor the highest-quality approach. Model cascade routing, tiered context strategies, and differential evaluation are the tools for managing this tradeoff at scale.

7. **Statelessness is the LLM API's default; statefulness is the application's responsibility.** Session management, conversation history, and history management strategies are engineering artefacts, not conveniences. The design of the history management strategy — sliding window, summarisation, or selective pruning — affects both quality and cost in ways that must be tested empirically.

8. **API-first design redistributes engineering responsibility but does not reduce it.** The team building on a foundation model API cannot inspect the model's internals, cannot change its training, and cannot prevent silent model updates from affecting application behaviour. These constraints require operational practices — version pinning, continuous evaluation, fallback routing, and resilience engineering — that have no equivalent in traditional software deployments.

9. **MedChat's architecture is a direct expression of its domain's risk profile.** Clinical safety requirements make RAG non-negotiable, hallucination mitigation the primary engineering priority, and deliberate context window allocation a safety concern, not a performance optimisation. Domain-specific risk analysis should precede every architectural decision in LLM system design.

---

### Review Questions

---

1. A development team has built a clinical chatbot that performs well in testing but begins producing unreliable answers after users have been in a session for more than fifteen turns. The system prompt has not changed. No code has been deployed. Diagnose the most likely architectural cause and propose a specific remediation, explaining which layer of the LLM application stack is implicated and why.

2. Your team is designing a legal document review system that must answer questions about specific contracts using only information from those contracts. The team proposes two architectures: Architecture A uses a very large context window to include all contracts directly in every prompt; Architecture B uses a retrieval layer to fetch relevant contract passages on demand. Using the concepts from this chapter — context window constraints, the lost-in-the-middle problem, and token economics — argue which architecture is preferable for a corpus of one hundred contracts averaging 50,000 words each, and identify the failure mode you would expect from the rejected architecture at scale.

3. A product manager asks why the MedChat system prompt should ever need to change after initial deployment, since "the instructions are already written." Construct a technical response that explains three specific scenarios under which the prompt layer must be revised even when the underlying codebase is stable, and explain what organisational process should govern those changes.

4. A colleague argues that sycophancy is a minor concern that does not justify engineering effort, because "users can always verify important information themselves." The application in question is a chatbot for junior resident physicians in emergency departments, responding to queries during acute care episodes. Identify the specific failure scenario where sycophancy becomes a patient safety risk in this context, and propose a testable evaluation strategy that would detect sycophantic responses before the system reaches production.

5. Your LLM application is processing 10,000 clinical queries per day at an average cost of $0.018 per query. The product team proposes adding chain-of-thought reasoning to improve answer quality on complex queries, which a pilot suggests increases average output token count by 60%. Calculate the daily cost impact of applying chain-of-thought reasoning to all queries versus applying it only to the 20% of queries classified as complex by a lightweight routing model. What additional engineering investment does the selective approach require, and how would you evaluate whether that investment is justified?

6. A hospital IT team is evaluating whether to build their clinical Q&A system on a foundation model API or to fine-tune and self-host an open-source model. They argue that self-hosting gives them full control and avoids the risk of the model provider changing the model under them. Critically evaluate this argument: what risks does self-hosting genuinely mitigate, what engineering responsibilities does it introduce that API-first design does not, and for which class of clinical application would you recommend each approach?

---
