## 19.1 What a Prompt Actually Is

The word "prompt" has been compressed, by popular usage, into meaning the text a user types into a chat interface. That definition is useful for consumers. For engineers, it is actively misleading.

A *prompt* is not just the user's message. It is the entire input that the model receives and reasons over: the system message establishing role and constraints, the conversation history from prior turns, documents retrieved from external sources, tool schemas describing what functions the model can invoke, worked examples demonstrating desired output format, and finally the user's actual query. The model has no privileged window into any of these components. It sees one long string of tokens — everything concatenated together — and generates the next token based on everything that precedes it.

This matters because it reframes what prompt engineering actually controls. When you write a system prompt, you are not writing a label on a box. You are writing the first several hundred tokens of a reasoning trace that will influence every subsequent token the model produces. When you choose how much conversation history to include, you are deciding what context the model can draw on when it formulates its response. When you write a tool description, you are determining whether the model calls that tool at all, and how accurately it fills in the tool's parameters. Every one of these decisions is prompt engineering, whether or not it looks like "writing a prompt."

### The Context Window as a Resource

A language model has a *context window* — the maximum number of tokens it can attend to at once. GPT-4o supports 128,000 tokens. Claude 3.5 Sonnet supports 200,000. Gemini 1.5 Pro supports one million. These are large numbers, but they are finite, and they carry costs: inference time scales with context length, and API pricing is typically per-token on both input and output.

*Context engineering* is the discipline of deliberately deciding what goes into the context window, in what order, and in what form — given the constraints of token budget, retrieval quality, and downstream task requirements. It is, at its core, a resource allocation problem with semantic consequences.

### The Lost-in-the-Middle Problem

Not all positions in the context window are equal. Liu et al. (2023) demonstrated empirically that language models exhibit a U-shaped recall curve over their context: information near the beginning and near the end of the context is recalled significantly better than information placed in the middle. The study tested models ranging from 3B to 70B parameters on multi-document question answering tasks where the position of the relevant document was varied. Performance dropped by as much as 20 percentage points when the relevant document was placed in the middle of a long context rather than at the start or end.

The implication for system design is direct. If you retrieve five documents for a RAG query and place the most relevant document third, the model may under-utilise it. If you structure a long system prompt so that the critical safety instructions appear in the middle, after a lengthy role description and before a set of formatting rules, the model is less likely to follow those safety instructions consistently. Treat the lost-in-the-middle finding as a layout specification.

The engineering response is to treat position as a first-class design decision. Highly salient content — safety constraints, task-critical retrieved passages, the most representative few-shot examples — should anchor the beginning or end of the context. Less critical content — general background, supplementary examples, conversational filler — belongs in the middle, where recall is poorest.

---
