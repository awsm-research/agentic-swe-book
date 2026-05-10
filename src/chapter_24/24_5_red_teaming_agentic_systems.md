## 24.5 Red Teaming Agentic Systems

---

Red teaming is systematic adversarial testing: an engineering team attempts to break the system's safety properties before external attackers do, using the same techniques an attacker would use. For traditional software, red teaming is a standard pre-deployment practice in security-sensitive domains. For agentic systems, it is both more important and more challenging, because the attack surface includes the agent's reasoning — a sufficiently sophisticated input may bypass security controls that function correctly against simpler inputs.

The goal of red teaming is not to exhaustively enumerate all possible attacks — that is impossible. The goal is to discover the highest-priority vulnerabilities before they are exploited, and to document both the vulnerabilities and their mitigations in a structured form that can guide future testing as the system evolves.

### 24.5.1 Goal Hijacking

Goal hijacking is an attack in which the attacker causes the agent to pursue a different goal from the one assigned by the legitimate user. The most common form is prompt injection: the attacker embeds instructions in content that the agent retrieves — a tool result, a retrieved document, a field in a form — that override or extend the agent's system prompt. Because the agent's reasoning is grounded in its context, and because tool results are appended to that context with the same token weight as the system prompt, a sufficiently authoritative-seeming injected instruction can redirect the agent's goal.

In the clinical context, a goal hijacking attack might attempt to cause MedAgent to submit a lab order for a different patient than the one in context, by embedding a patient identifier substitution in a retrieved drug interaction record. The defence is layered: tool output prefix isolation (every tool result is prefixed with an instruction to the LLM to treat the content as untrusted data), structured output validation (tool results are validated against Pydantic schemas that reject fields containing injection pattern strings), and session-level invariant enforcement (the session's authorised patient identifier is validated against every proposed action, regardless of what the agent believes about the context).

### 24.5.2 Privilege Escalation

Privilege escalation is an attack in which the agent gains access to tools beyond its authorised scope. In software security, privilege escalation typically involves exploiting a vulnerability to execute code with elevated permissions. In agentic systems, the equivalent is an attack that causes the agent to invoke a tool it was not intended to have access to, or that causes the agent to use its authorised tools to achieve an effect that was not in scope.

The most dangerous form of privilege escalation for agents is the confused deputy problem: the agent is tricked into using its own legitimate permissions to execute an attacker-controlled action, mistaking the attacker's instruction for a legitimate user request. MedAgent's approval workflow is the primary defence against confused deputy: even if the agent proposes an out-of-scope action as a result of an injection attack, the approval gate presents the proposed action to a human reviewer who can identify and reject it.

The key design insight is that approval workflows are not just regulatory controls — they are security controls. They provide a human checkpoint that can catch the consequences of privilege escalation attacks before the escalated action is executed.

### 24.5.3 Prompt Injection at Tool Boundaries

Prompt injection at tool boundaries is the most prevalent and hardest-to-fully-eliminate attack vector against agentic systems. The attack embeds instructions in the content that a tool retrieves — a web page, a database record, a document, an API response — with the intent that those instructions will be processed by the LLM as part of its reasoning context.

The OWASP Top 10 for Large Language Model Applications — the LLM security community's equivalent of the well-established OWASP Web Application Security Project — lists prompt injection as the top vulnerability for LLM-based systems, noting that indirect prompt injection via tool outputs is particularly dangerous because the injected content bypasses any filtering applied to direct user inputs. The defence is multi-layered by necessity: no single control eliminates the risk. The layers are: tool output prefixing (labelling retrieved content as untrusted), structured schema validation (rejecting retrieved content that fails schema constraints), pattern matching (detecting common injection strings in retrieved content), and human review of proposed irreversible actions (catching the consequences of successful injection before they are executed).

Red teaming must systematically test all three attack categories — goal hijacking, privilege escalation, and tool boundary injection — against every tool the agent has access to. The results must be documented in a structured format that records the attack payload, the expected defensive behaviour, the observed behaviour, the mitigation applied, and the residual risk. This document is both a regression test suite and a governance artefact: it demonstrates to regulators that the organisation has conducted adversarial testing and has a plan for the vulnerabilities that could not be fully mitigated.

---
