## 21.5 Streaming Responses

---

For interactive applications, the most impactful user-experience improvement available in LLM serving is not faster generation — it is streaming.

Without streaming, a user submits a query and waits while the model generates its complete response. For a 500-token response from a frontier model, this may mean waiting 8–15 seconds before seeing anything. The experience is indistinguishable from a slow, broken application.

With streaming, the model's response is transmitted token by token as it is generated. The user begins reading after the first token appears — typically within 1–2 seconds — and the remainder of the response flows in continuously. Total generation time is identical, but perceived latency is radically better. Users form an impression of the system's responsiveness from time-to-first-token, not from total response time, and streaming optimises exactly that metric.

Streaming changes the serving architecture in non-trivial ways.

The connection between the client and server must remain open for the duration of the generation. This rules out traditional request–response HTTP architectures for streaming interactions and requires either server-sent events (SSE), WebSockets, or a provider-specific streaming protocol. Most LLM provider APIs use SSE; LiteLLM normalises these into a consistent streaming interface.

Middleware in the serving stack that processes responses — guardrails, logging, cost attribution — must be redesigned to handle partial responses. A guardrail that expects a complete response before scanning for harmful content cannot simply be placed at the end of the pipeline when streaming is active. Either the guardrail must operate on partial chunks, accepting that some latency is reintroduced, or it must buffer a configurable number of tokens before beginning its scan, accepting that the first characters delivered to the user have not yet been evaluated.

Error handling becomes more complex. In a standard request–response cycle, an error before the response is sent means the client receives an error response and can retry. In a streaming context, an error mid-stream means the client has already received partial content. The application must decide whether to display what was received, show an error, or attempt to complete the response through an alternate path.

State management in the serving infrastructure must account for long-lived connections. Serverless functions with short execution timeouts cannot serve streaming responses without special handling — a constraint that shapes deployment architecture, as discussed in section 21.9.

Despite these architectural complications, streaming is the correct default for any LLM application that presents responses to human users in real time. The user-experience improvement is too significant to forgo, and the architectural complexity, while real, is well-understood and manageable with the right infrastructure choices.

---
