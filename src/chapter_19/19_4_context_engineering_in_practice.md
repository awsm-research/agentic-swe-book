## 19.4 Context Engineering in Practice

Four design decisions recur in almost every production LLM application: system prompt design, retrieval placement, conversation history management, and tool schema authoring. Each is a direct application of the context window principles established in §19.1, and each has engineering trade-offs that are specific to the decision.

### System Prompt Design

The system prompt is the first thing in the context. By the lost-in-the-middle finding, it is also the content the model attends to most reliably — which makes it the highest-leverage position in the entire context window.

A well-designed system prompt has four components, in order:

**Role definition** establishes who the model is and what scope of behaviour is appropriate. For MedChat: "You are a clinical decision support assistant for qualified healthcare professionals in Australia." Role definition is not merely decorative — it activates the relevant slice of the model's pre-trained knowledge and sets prior expectations about appropriate response style.

**Constraints** define what the model must not do. These should be explicit and specific. "Do not diagnose individual patients" is a constraint. "Do not speculate beyond the retrieved clinical guidelines" is a constraint. Vague instructions like "be careful" or "be accurate" are not constraints — they are hopes. Constraints should be stated as prohibitions with clear scope.

**Output format specification** defines what the response should look like: length, structure, citation format, hedging language. If the application expects JSON, say so explicitly and provide a schema. If the application expects a structured answer with a summary, supporting detail, and a confidence indication, provide an example. Format specification is where few-shot examples do most of their work.

**Safety instructions** close the system prompt. They should appear at the end — consistent with the lost-in-the-middle finding, which shows end-of-context information is recalled nearly as well as beginning-of-context information. For MedChat, safety instructions cover what to do when a query is outside scope, when a query implies clinical emergency, and when a query appears to be a prompt injection attempt.

### Retrieval Placement

In a RAG system, retrieved documents land somewhere in the context. Where they land affects how well the model uses them — and the answer from Liu et al. (2023) is that the most relevant document should be placed as close to the query as possible, not buried in the middle of a block of retrieved passages.

A well-engineered retrieval context structure for MedChat places documents in reverse relevance order: the most relevant retrieved passage immediately before the user query, less relevant passages earlier in the context block. This is counterintuitive — the most relevant document seems like it should come first — but it is empirically supported. The model's attention at generation time is weighted toward the tokens immediately preceding the position it is generating into; placing the highest-relevance content close to the generation boundary improves utilisation.

Retrieved documents should also be labelled. Including a clear delimiter — "BEGIN RETRIEVED CLINICAL GUIDELINE" and "END RETRIEVED CLINICAL GUIDELINE" — helps the model distinguish retrieved content from its own prior conversation and from the user's query. These labels serve as trust boundary markers: the model is told explicitly what material is from a trusted source and what material came from the user.

### Conversation History Management

Every additional turn in a conversation adds tokens to the context. A ten-turn clinical consultation with detailed responses on both sides can consume 8,000–12,000 tokens before the current query is even added. In a system with a 128,000-token context window this is manageable; in a system with tight cost constraints or aggressive latency targets, it is not.

The two standard management strategies are *truncation* and *summarisation*. Truncation drops the oldest turns from the history when the context would exceed the budget. This is simple to implement and computationally cheap, but it loses information that may be relevant — a patient's allergy mentioned three turns ago may be forgotten when those turns are truncated.

Summarisation condenses older portions of the conversation into a compact representation before they are dropped. A summariser LLM call adds latency and cost, but preserves the semantic content of earlier turns. For MedChat, where clinical context established early in a conversation — medication history, known allergies, patient age — must not be lost, summarisation is the correct choice. For a general-purpose assistant where conversation history is largely stylistic context, truncation is acceptable.

A hybrid approach maintains a fixed "anchor" block of context — the original clinical question and key facts established at the start — plus a rolling window of recent turns plus a compressed summary of the middle. This is more complex to implement but more robust for long clinical consultations.

### Tool Schema Design as Context Engineering

Every tool available to the model is described by a schema — a JSON specification of the tool's name, purpose, and parameters. These schemas are injected into the context alongside the conversation. For a model with ten tools, the tool schemas alone may consume 2,000–3,000 tokens before any conversation content.

Tool schema design determines whether the model calls tools correctly. A tool named `search` with a description of "Search for information" will be called inconsistently, because "information" is too broad for the model to know when the tool is appropriate or how to fill in its parameters. A tool named `retrieve_clinical_guideline` with a description of "Retrieve a passage from the MedChat clinical guideline corpus given a specific clinical question. Use this tool whenever the query requires information about drug dosing, drug interactions, diagnostic criteria, or clinical protocols" will be called accurately and consistently.

The parameter descriptions carry as much weight as the tool name. A parameter named `query` with no description will be populated with whatever the model guesses is appropriate. A parameter named `query` with the description "A specific clinical question in natural language, focused on a single clinical topic. Do not include patient identifiers." will be populated correctly and with the appropriate privacy protections. Tool schema authoring is prompt engineering — it belongs in version control, under the same review standards as any other prompt.

---
