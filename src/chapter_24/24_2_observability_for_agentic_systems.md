## 24.2 Observability for Agentic Systems

---

Observability is the property of a system that allows its internal state to be inferred from its external outputs. For traditional software, the three pillars of observability — logs, metrics, and traces — are well understood. A structured log captures the what. A metric captures the how much and how often. A distributed trace captures the where: the causal path through multiple services that produced a given outcome. These tools were designed for systems with deterministic execution paths and structured outputs.

Agentic systems violate both assumptions. An agent's execution path is a function of the LLM's non-deterministic reasoning — the same input can produce a different sequence of tool calls on different runs. An agent's output is a natural language string, or a chain of tool calls, that cannot be validated by schema alone. The observability tooling must be correspondingly richer, and the signal hierarchy is different from traditional applications.

### 24.2.1 Distributed Tracing: Every Tool Call Is a Span

In a traditional distributed system, a trace follows a request through multiple services, recording latency and errors at each service boundary. In an agentic system, the trace follows a session through multiple reasoning steps, recording at each decision point: which tool was selected and why, what arguments were passed, what the tool returned, and how the agent's reasoning changed in response. Every tool call is a span. Every LLM reasoning step is a span. Every subagent invocation in a multi-agent system is a nested trace.

The instrumentation standard for this is OpenTelemetry — an open, vendor-neutral framework for generating, collecting, and exporting traces, metrics, and logs. Applied to an agent, OpenTelemetry spans capture the full causal chain from session initiation through tool execution to final response. The trace is the ground truth of what the agent did. It is what allows an investigator, weeks after an incident, to reconstruct the exact sequence of decisions that led to a specific action.

What makes agentic tracing different from service tracing is the need to capture the agent's reasoning, not just its inputs and outputs. The intermediate outputs of the LLM — the chain-of-thought reasoning, the tool call arguments, the confidence expressions — are the diagnosis layer. They are what distinguishes a correctly reasoning agent that encountered bad data from a confused agent that should have been interrupted. Without capturing this layer, post-incident investigation is limited to observing what happened rather than understanding why.

### 24.2.2 Structured Logging

Structured logging means emitting machine-parseable log records — typically JSON — that carry typed fields rather than free-text strings. For an agent, the critical events that must be logged in structured form are: session start and end (with session identifier, user identifier, and initial task description), every tool call (tool name, input arguments, output preview, latency, and success status), every approval request and decision (action details, requesting session, approver identifier, and decision timestamp), and every security alert (alert type, session context, and the content that triggered the alert).

The discipline of structured logging serves two purposes that are equally important. First, it makes logs queryable at scale: an operator can ask "show me all sessions in the last thirty days where the drug interaction tool was called with warfarin as one of the drugs and the result indicated a contraindicated interaction" and receive an answer in seconds rather than grepping through free text. Second, it provides the foundation for anomaly detection: machine-parseable logs can be aggregated into metrics and fed into statistical models that detect unusual patterns — a session that called forty tools in ten minutes, or a session whose approval request was submitted and approved by the same user identifier.

### 24.2.3 Session Replay

Session replay is the capability to reconstruct an agent session exactly as it occurred: the initial state, each message appended to the context, each tool call and its result, each state transition, and the final output. It is the most important observability capability for post-incident investigation, and it is the one most often omitted by teams that start with logs and metrics and discover their need for replay only after an incident.

The technical foundation for session replay is a persistent checkpointer: a mechanism that serialises the agent's state to durable storage at every step, rather than maintaining it only in memory. When replay is needed, the checkpointer provides a complete snapshot of every state the session passed through, in chronological order. The session can be stepped through in sequence, or fast-forwarded to a specific point, or run forward from an intermediate state to test whether a different tool choice would have produced a different outcome.

The Air Canada case illustrates why replay matters even for non-agentic systems. The chatbot's incorrect response was logged, but reconstructing the session context that produced it — which conversation history led to that particular claim about bereavement fare policy — required significant forensic effort. For an agent that takes irreversible actions across dozens of steps, the forensic effort without replay capability is prohibitive. The system that lacks replay capability is not just hard to debug; it is impossible to defend in a regulatory inquiry that asks for a step-by-step account of what the system did and why.

### 24.2.4 Anomaly Detection and Alerting

Tracing and logging capture what happened. Anomaly detection raises an alert when what is happening deviates from what should be happening. For agentic systems, the most important anomaly signals are: session cost anomalies (a session that consumes significantly more tokens than the population average may be stuck in a reasoning loop or processing maliciously large content), turn count anomalies (a session that runs for many more steps than average may have encountered a compounding error or a misspecified goal), tool call rate anomalies (a session that calls a particular tool at an unusual frequency may be in a retry loop or executing a scripted attack), and approval rate anomalies (a system whose approval rate drops significantly below baseline may have lost its approval workflow or be routing actions through an untested path).

These anomalies must be defined as metrics, computed continuously from the structured log stream, and evaluated against thresholds that trigger alerts when crossed. The statistical technique of Z-score comparison against historical distributions provides a simple and effective baseline: an alert fires when a session's metric exceeds three standard deviations from the historical mean. More sophisticated approaches — time-series anomaly detection, clustering, and isolation forests — become warranted as the production volume of sessions grows.

---
