## 17.3 Context Windows: The Constraint That Shapes Everything

---

Every LLM has a context window: the maximum number of tokens it can process in a single call, encompassing both input and output. Context windows in 2025 range from 8,000 tokens for lightweight models to one million tokens for Gemini 1.5 Pro. These numbers sound large until you start filling them.

A context window is not free storage. It is a computational budget. The transformer architecture's self-attention mechanism attends every token to every other token in the context, which means that processing cost and latency scale super-linearly with context length — approaching quadratic in standard attention implementations, and meaningfully expensive in all of them. A context that is twice as long costs more than twice as much to process. A 128,000-token context window does not mean "freely include 128,000 tokens in every call" — it means "you have 128,000 tokens available if you are willing to pay the latency and cost of filling them."

### 17.3.1 The Budget Allocation Problem

The context window is a finite resource that must be allocated deliberately. In a typical RAG application, that allocation looks something like this: the system prompt uses several hundred tokens to define the model's role and constraints; retrieved context passages use one to three thousand tokens to provide factual grounding; conversation history uses a variable and potentially unbounded number of tokens as the session progresses; the current user query uses tens to hundreds of tokens; and the output generation reserve requires enough space for a complete response. Every one of these allocations interacts with the others. A longer system prompt leaves less room for retrieved context. Growing conversation history competes with retrieval capacity. Generating a longer response consumes output budget that increases cost.

This budget allocation problem is the reason context window management is not a secondary concern — it is an architectural constraint that shapes the entire system design before the first line of application code is written. Teams that approach context management as an afterthought will discover, under production load, that sessions degrade unpredictably as history accumulates, that retrieval quality drops when the context is crowded, and that costs are higher than expected because nobody measured the token budget at system design time.

### 17.3.2 The Lost-in-the-Middle Problem

A subtler constraint is what researchers Liu and colleagues identified as the lost-in-the-middle problem (Liu et al., 2023). Their finding, from a series of controlled experiments, was that language model performance degrades significantly on information that appears in the middle of a long context, even when that information is clearly present. Models attend more reliably to content at the beginning and end of the context window than to content in the middle. This is not a bug — it is a consequence of how transformer attention patterns develop during training — but it is a constraint that architecture must account for.

For RAG applications, the implication is direct: the order in which retrieved passages are placed in the context matters. The most relevant passages should appear at the beginning or end of the retrieved context block, not buried in the middle where attention may fail to fully utilise them. Reranking — sorting retrieved passages by relevance score before injecting them — addresses part of this problem, but even with perfect reranking, a context with many passages will suffer middle-degradation for the less-well-positioned passages.

For multi-turn conversation applications, the implication is that conversation history cannot be treated as an unordered accumulation. Messages that appeared many turns ago and are buried in the middle of a long context may be effectively invisible to the model. This undermines the assumption that including full conversation history provides the model with complete context of what has transpired. Summarisation strategies — compressing older history into a compact summary before it migrates to the middle of a long context — address this problem more reliably than raw history inclusion.

The lost-in-the-middle problem is one of the clearest examples of how Software 3.0 engineering requires understanding model behaviour, not just model API. Engineers who design their context layout without knowledge of this phenomenon will build systems that seem to work in short sessions and degrade mysteriously in long ones.

---
