## 24.6 The Regulatory Context

---

The engineering practices described in this chapter are not merely good practice recommendations. In an increasing number of jurisdictions, they are legal requirements for AI systems deployed in regulated domains. Understanding the regulatory context is not optional for the SE4AI engineer — it shapes the minimum viable architecture for production agentic systems.

### 24.6.1 The EU AI Act

The EU Artificial Intelligence Act, which entered into force in August 2024, is the world's first comprehensive legal framework for AI systems. It classifies AI systems into risk tiers and imposes requirements on each tier. High-risk AI systems — which include AI systems intended to be used as safety components in medical devices, AI systems used in employment decisions, and AI systems used to administer critical infrastructure — are subject to extensive pre-market requirements and post-market obligations.

For clinical decision support systems of the kind represented by MedAgent, the classification as high-risk is unambiguous. The relevant obligations include: establishing and maintaining a risk management system throughout the AI system's lifecycle; ensuring that training, validation, and testing data meet quality criteria; maintaining technical documentation that allows the system's development and capabilities to be assessed; keeping automatic logging of events for post-market monitoring; providing transparency information to deployers; designing the system to allow natural persons to oversee, intervene, and override its operation; and achieving accuracy, robustness, and cybersecurity standards appropriate to its purpose.

Article 12 of the EU AI Act specifically requires that high-risk AI systems maintain logs for post-market monitoring that enable reconstruction of the circumstances leading to any output, for a duration appropriate to the system's use-life. This is the legislative basis for the append-only audit log architecture described in Section 24.3: it is not a best practice, it is a legal requirement for any clinical AI system deployed in the EU.

### 24.6.2 Human Oversight Mandates

Human oversight is a requirement that appears across multiple regulatory frameworks, not just the EU AI Act. The reasoning is consistent: in high-stakes domains where AI system errors can cause harm, a human must remain in the decision loop with the ability to review, intervene, and override the system's proposed actions.

The engineering implication of a human oversight mandate is that approval workflows for irreversible actions are not optional features that can be deferred to a later version — they must be present at initial deployment in regulated domains. A system deployed in a regulated domain without approval workflows for irreversible actions is not compliant at launch, regardless of how sophisticated its reasoning capabilities are. Retrofitting approval workflows onto a deployed system is significantly more difficult than designing them in from the start, because the system's existing users, workflows, and integrations have been built around the assumption that the agent acts autonomously.

### 24.6.3 What Compliance Requires in Practice

Regulatory compliance for a high-risk AI system is not achieved by checking boxes on a compliance framework. It is achieved by building a system whose architecture makes the required properties demonstrable. An auditor reviewing a clinical AI system will ask to see the audit log records for a sample of sessions, the approval records for irreversible actions, the red team assessment, the model card, the evaluation results, and the monitoring configuration. These artefacts must exist, must be accurate, and must be traceable to the deployed system.

The distinction between compliance as a box-checking exercise and compliance as an engineering discipline matters because audits are not the only context in which these artefacts are examined. Incidents are. When a clinical AI system is involved in an adverse event, the regulatory investigation will request the same artefacts, and the organisation's ability to produce them determines the difference between a finding of adequate oversight and a finding of negligence. Engineering for compliance means engineering such that the organisation can tell a coherent, evidenced story about what the system did, why it was designed that way, and what controls were in place.

---
