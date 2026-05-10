## 19.2 Prompting Strategies

Each prompting strategy has a performance profile: conditions under which it outperforms alternatives, and conditions under which it adds cost without benefit. Choosing among them is an engineering decision, not an aesthetic one.

### Zero-Shot Prompting

*Zero-shot prompting* asks the model to perform a task using only a natural-language instruction, with no examples provided. It relies entirely on the instruction's clarity and the model's pre-trained capability.

Zero-shot works well when the task is within the model's strong capability distribution — summarisation, paraphrasing, answering factual questions in well-represented domains, generating boilerplate code. It fails predictably when the desired output format is unusual, when the domain is underrepresented in training data, or when the task requires multi-step reasoning that the model must execute without scaffolding.

The failure mode is not always obvious. A zero-shot model will produce output with confidence even when it is producing output that does not match the intent. The output looks fluent. It may even be partially correct. Without a defined evaluation criterion, the failure is invisible. Zero-shot demands the highest faith in alignment between model capability and task requirements — which makes it the riskiest default, not the simplest one.

### Few-Shot Prompting

*Few-shot prompting* embeds worked examples directly in the prompt. Each example demonstrates the mapping from a specific input to a specific desired output. The model generalises from these examples when processing the actual query.

The research on few-shot learning (Brown et al., 2020) established that large language models can adapt to novel tasks from very few examples — sometimes as few as one or two. But the quality of those examples matters more than the quantity. A prompt with three carefully selected, diverse examples that cover the key edge cases will outperform a prompt with ten examples that all illustrate the same easy central case.

Example selection is an engineering problem. Randomly sampling from your training data produces mediocre few-shot prompts. Deliberate selection — choosing examples that cover different output formats, different edge-case inputs, and different difficulty levels — produces prompts that generalise well. Example ordering also matters: models attend to examples near the end of the context more strongly (consistent with the lost-in-the-middle finding), so placing your most representative example closest to the query is generally more effective than placing it first.

The practical limitation of few-shot prompting is context budget. Each example consumes tokens. A detailed example might consume 200–500 tokens. In a RAG system that also needs to inject retrieved documents, adding six examples may consume as many tokens as two full retrieved passages — a trade-off that must be analysed rather than assumed.

### Chain-of-Thought Prompting

*Chain-of-thought (CoT) prompting* asks the model to produce its reasoning process explicitly before stating its final answer. Wei et al. (2022) showed that this simple modification dramatically improves performance on multi-step reasoning tasks — arithmetic, commonsense reasoning, and symbolic reasoning — with gains that were most pronounced in larger models. The paper demonstrated that standard prompting plateaued well below human performance on tasks like GSM8K (grade-school maths) whilst CoT prompting continued to improve with model scale.

The mechanism is not that the model "thinks harder." The mechanism is that generating intermediate steps creates a kind of implicit scratchpad: the model's attention at each generation step can attend to the previously generated reasoning chain, not just the original context. This effectively extends the working memory available to the model during generation.

The practical instruction is simple: appending "Let's think step by step" to a zero-shot prompt often suffices for standard models (Kojima et al., 2022). For few-shot CoT, the worked examples should include explicit reasoning traces, not just final answers. For MedChat, a few-shot CoT example for a drug interaction question might show: identifying each drug, recalling their metabolic pathways, reasoning about the interaction mechanism, and concluding with a safety recommendation.

CoT prompting has costs. It increases output token count, which increases latency and API cost. For simple tasks — classification, entity extraction, yes/no questions — CoT adds cost without meaningfully improving accuracy. Reserve CoT for tasks that genuinely require multi-step reasoning.

### Self-Consistency

*Self-consistency* is an extension of CoT prompting. Rather than generating a single reasoning chain and accepting its conclusion, you generate multiple independent reasoning chains by sampling from the model with a non-zero temperature, and take the majority-vote answer across all chains.

Wang et al. (2022) showed that self-consistency substantially outperforms single-path CoT on arithmetic and commonsense benchmarks — not because any individual chain is better, but because aggregating across multiple chains reduces the variance introduced by the model's sampling process. A single CoT path may reason correctly about the problem and still arrive at the wrong answer due to a small arithmetic slip. Across ten sampled paths, the correct answer tends to dominate.

The trade-off is direct: self-consistency multiplies inference cost by the number of samples. Generating ten paths costs ten times as much as generating one. For MedChat, self-consistency on clinical decision questions — where the consequence of an error is significant — is likely worth the cost. For routine entity extraction or summarisation tasks, it is not. The engineering decision is a cost-benefit calculation specific to each task type.

### ReAct: Reasoning and Acting

*ReAct* (Yao et al., 2022) interleaves reasoning traces with tool-use actions in a structured loop. Where standard prompting generates a response in one pass, ReAct generates a reasoning step, then an action (a tool call), then an observation (the tool's output), then another reasoning step, and so on — until it has enough information to produce a final answer.

ReAct suits any task requiring information the model cannot retrieve from its weights — a database lookup, an API query, a current stock price. Without the action loop, the model must either hallucinate the information or confess ignorance. With it, the model retrieves and reasons over live data.

Yao et al. (2022) tested ReAct on knowledge-intensive tasks requiring Wikipedia lookups and interactive decision-making tasks requiring sequential actions. On both task types, ReAct outperformed both standalone prompting (which could not access external information) and standalone tool-use without reasoning traces (which could retrieve information but could not reason about which information to retrieve or how to interpret it). The combination of reasoning and acting — not either alone — produced the improvement.

For LLM applications with tool access, ReAct is the natural structural choice. The prompt encodes the reasoning-action-observation cycle; the tool schemas define what actions are available; and the model's generated reasoning traces make the decision process auditable, which matters in regulated domains.

---
