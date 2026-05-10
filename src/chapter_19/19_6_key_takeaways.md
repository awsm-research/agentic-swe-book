## 19.6 Key Takeaways

1. **A prompt is the entire model input, not just the user's message.** System messages, conversation history, retrieved documents, tool schemas, and worked examples are all prompt. Controlling each of these is context engineering.

2. **Position in the context window is a design decision.** The lost-in-the-middle finding (Liu et al., 2023) shows that content at the start and end of context is recalled significantly better than content in the middle. Safety instructions, key retrieved passages, and representative examples should anchor the boundaries.

3. **Prompting strategy choice is an engineering trade-off.** Zero-shot suits high-capability standard tasks; few-shot suits format-sensitive or domain-specific tasks; chain-of-thought suits multi-step reasoning; self-consistency reduces variance at multiplied cost; ReAct suits tool-using agents requiring external information.

4. **Reasoning models change the prompt engineering problem.** Models trained to reason internally — o1, o3, DeepSeek-R1 — require less scaffolding and fewer CoT examples. The engineering task shifts from building reasoning scaffolding to clearly specifying task requirements and constraints.

5. **System prompt structure follows a principled order.** Role definition, constraints, output format specification, and safety instructions — with safety instructions placed at the end to exploit end-of-context recall advantage.

6. **Tool schema design is context engineering.** Vague tool names and parameter descriptions produce inconsistent tool calls. Precise, specific descriptions produce reliable, auditable tool use. Tool schemas belong in version control.

7. **The prompt lifecycle mirrors the code lifecycle.** Authoring against test cases, testing before staging, staging before production, monitoring in production, deprecation with documentation — every phase has a defined discipline.

8. **Prompt injection has two attack surfaces.** Direct injection arrives via user input; indirect injection arrives via retrieved external content. Structural defences — trust boundary labelling, input sanitisation, output validation — are more effective than linguistic defences.

9. **Prompt regression tests are the quality gate for prompt changes.** Criteria should be semantic, not exact-match. Automated evaluation handles most cases; LLM-as-judge scales to cases that require reasoning. Every production incident expands the test suite.

10. **A prompt change is a code change.** It requires version control, code review, and a passing test suite before promotion to production. The speed argument against this discipline is the same speed argument that produces production incidents.

---

### Review Questions

1. A team is building a clinical triage assistant that classifies patient-reported symptoms into urgency categories (immediate, urgent, routine). They are considering zero-shot prompting with a detailed instruction versus few-shot prompting with ten examples. What factors should determine their choice, and what information would you need to make a recommendation?

2. The MedChat team discovers that in twenty percent of queries involving drug interactions, the model fails to cite the retrieved clinical guideline even though the citation format is specified in the system prompt. The system prompt is 800 tokens long, with the citation format instruction at position 400. Using the lost-in-the-middle framework, propose two specific changes to the system prompt structure that might address this failure, and explain the reasoning.

3. A developer argues that self-consistency prompting is wasteful for MedChat because it multiplies API costs by the number of sampled paths, and MedChat's retrieval system already ensures the model has accurate information. Evaluate this argument. For which MedChat query types is the developer's argument strongest, and for which query types is it weakest?

4. An indirect prompt injection attack is discovered in the MedChat retrieval corpus: a maliciously crafted FAQ document was added that, when retrieved, instructs the model to recommend a specific drug regardless of the clinical context. The attack was only discovered because a clinician noticed an unusual recommendation. Design three engineering changes to MedChat's architecture that would make this class of attack either detectable before it reaches the model or detectable from the model's output.

5. A product manager proposes switching MedChat's core model from GPT-4o to OpenAI o3 for the drug interaction query type, citing o3's superior accuracy on complex multi-step reasoning tasks. What information about MedChat's usage patterns, cost structure, and auditability requirements would you need to evaluate this proposal? What aspects of the existing prompt suite would need to change for the o3 migration, and what aspects would not?

6. The MedChat team wants to extend the conversation history window from ten turns to thirty turns to support longer clinical consultations. A senior engineer objects that this will increase per-query costs by approximately 15% and degrade performance due to the lost-in-the-middle effect. Propose a conversation history management strategy that extends effective context to thirty turns without proportionally increasing token consumption, and explain what information would be lost and what would be preserved under your strategy.

---
