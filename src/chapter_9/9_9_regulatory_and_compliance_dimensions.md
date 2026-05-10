## 9.9 Regulatory and Compliance Dimensions

As AI coding agents become part of production engineering workflows, they intersect with regulatory frameworks that were designed for human engineers.

### 9.9.1 Attribution and Accountability

When an agent writes code that introduces a security vulnerability, who is responsible? The developer who invoked the agent? The team that configured it? The vendor who built the underlying model?

Current regulatory frameworks — SOC 2, ISO 27001, PCI DSS, GDPR — do not address AI-generated code directly. But the underlying principle is consistent: *the organisation that deploys the system is responsible for its outputs*. A vulnerability introduced by an AI agent is treated identically to a vulnerability introduced by a human engineer.

This has an important implication: the verification and review processes an organisation applies to agent-generated code must be at least as rigorous as those applied to human-generated code. Saying "the AI generated it" is not a defence.

### 9.9.2 Data Handling in Agentic Workflows

Agents that are given access to production databases, customer data, or personally identifiable information (PII) for the purpose of a coding task may inadvertently:

- Include PII in their reasoning trace (which may be logged)
- Commit test data containing real customer records to the repository
- Write PII to temporary files that are not subsequently deleted
- Pass sensitive data as arguments to external tool calls (where it appears in logs)

Best practice: agents should never have access to production data for development tasks. Use anonymised or synthetically generated data for testing. Apply data minimisation at the access control layer — the agent should not be *able* to access production PII, not merely *instructed* not to.

---
