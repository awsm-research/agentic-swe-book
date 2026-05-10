## 19.3 Reasoning Models

Standard language models — GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro — generate tokens autoregressively. Each token is a direct continuation of the preceding context. Chain-of-thought prompting coaxes these models into producing reasoning traces before answers, but the reasoning trace is just another sequence of tokens in the same output stream. The model is not "reasoning" in any distinct computational sense; it is predicting the next token in a sequence that happens to look like a reasoning trace.

*Reasoning models* are a distinct product category. OpenAI's o1 (released September 2024), o3, and o4-mini series, and DeepSeek's R1 (December 2024), are trained to produce an internal chain-of-thought before generating a visible response. The internal thinking is not shown to the user by default and may be substantially longer than the visible output. The model has been trained specifically to allocate "thinking tokens" to working through the problem before committing to an answer. The mechanism is not simply prompted reasoning — it is a distinct training objective.

### What Changes in Prompt Design

Reasoning models require less scaffolding. Appending "think step by step" to a prompt for o1 is redundant — the model will think step by step regardless, because that is what it was trained to do. The elaborate few-shot CoT examples that substantially improve standard model performance on multi-step tasks provide much smaller marginal gains for reasoning models, because the model is already conducting an internal version of that process.

This means prompts for reasoning models can be shorter and more direct. The engineering goal shifts from "scaffold the model's reasoning" to "clearly specify the task and the constraints." System prompts for o1 and o3 that reproduce the elaborate multi-step reasoning instructions useful for GPT-4 often produce no improvement and may slightly degrade performance by consuming tokens the model would otherwise use for internal thinking.

The trade-off is control. A standard model with a detailed CoT prompt produces a reasoning trace that is visible, parseable, and predictable. You can audit the intermediate steps. You can write evaluators that check whether the model identified the correct intermediate conclusions before reaching the final answer. A reasoning model's internal thinking is opaque or only partially visible. The output is more reliable on hard tasks but less controllable in its reasoning path. For regulated applications — clinical decision support, legal document analysis, financial advice — the transparency of standard CoT may outweigh the accuracy advantage of a reasoning model.

### When to Use Reasoning Models

Reasoning models are best suited to tasks that are genuinely hard: complex mathematical derivations, multi-step code generation involving architectural decisions, legal and scientific analysis requiring sustained logical inference. On these tasks, the accuracy advantage over standard models is substantial and justifies the higher cost and latency.

They are poorly suited to tasks that are high-volume and relatively simple: classification, entity extraction, summarisation, short question answering. The cost of reasoning models per query is substantially higher — o1 and o3 were priced at 5–15 times the per-token cost of GPT-4o at their launch — and the latency is longer due to the internal thinking process. Deploying a reasoning model for bulk entity extraction is a cost engineering mistake.

The practical decision framework: use a reasoning model when task difficulty is high, volume is low, and accuracy on individual queries matters more than throughput. Use a standard model with appropriate prompting strategy when volume is high, latency is constrained, or the task does not genuinely require multi-step inference.

---
