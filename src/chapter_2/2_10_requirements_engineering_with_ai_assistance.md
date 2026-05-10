## 2.10 Requirements Engineering with AI Assistance

### 2.10.1 Using LLMs to Generate, Critique, and Refine Requirements

Large language models can accelerate requirements work at several points in the RE process, but they require precise inputs to be useful — and they fail in characteristic ways when inputs are vague.

**Where LLMs add value:**

- **Drafting initial stories**: Given a brief problem description, an LLM can generate a starting backlog of user stories faster than a requirements engineer working from a blank page. The output is rarely final, but it surfaces coverage gaps and provides a concrete artefact for stakeholder review.
- **Critiquing for quality**: An LLM prompted to review a requirements document against the quality attributes in §2.4 (unambiguous, complete, verifiable) will reliably flag vague language — "the system shall be fast," "the interface shall be intuitive," "the system shall handle errors gracefully." These are the same failures human reviewers miss because they are reading for intent rather than precision.
- **Generating acceptance criteria**: Given a user story, an LLM can generate Gherkin scenarios covering the happy path and common error cases. This is mechanical but time-consuming work that LLMs handle well — with the caveat that the generated scenarios must be reviewed against actual business rules, which the LLM does not know.

**Where LLMs fail:**

LLMs have no knowledge of your domain, your users' actual behaviour, or your regulatory environment. They will generate plausible-sounding requirements that conform to templates but miss tacit constraints. The NHS *National Programme for IT* failed in part because requirements were produced by a small group working top-down, without consulting the 18,000 clinicians who would use the system ([NAO, 2011](https://www.nao.org.uk/reports/the-national-programme-for-it-in-the-nhs-an-update/)). An LLM would have produced the same failure faster.

The workflow that works: **human-provided context** (stakeholder interviews, domain documentation, existing system behaviour) → **LLM draft** → **human review and correction** → **LLM refinement**. The human brings domain knowledge and stakeholder relationships; the LLM provides generation speed and systematic coverage checking.

### 2.10.2 Specification Quality as a Direct Determinant of LLM Output Quality

Requirements are the input to the next phase of development. In an AI-native workflow, they are also the input to code generation. This changes what is at stake when a requirement is vague.

Consider the difference between:

> *The system shall notify users when a task is assigned.*

and:

> *The system shall send an email notification to each assignee within 5 minutes of task assignment. If delivery fails, the system shall retry up to 3 times at 5-minute intervals. Notifications shall include the task title, the assigning user's name, and a direct link to the task.*

The first requirement, fed to a code-generating LLM, gives the model room to invent: it might generate a push notification instead of email, send only to the first assignee, skip retry logic, or omit the direct link. Each decision is plausible given the specification. Each might also be wrong. The engineer reviewing the generated code has no written requirement against which to check it.

This is the core of what makes requirements engineering more important in an AI-native workflow, not less. A vague requirement is always a problem — but in a manual development workflow, the developer who writes the code often attended the stakeholder meeting and absorbed the implicit intent. That tacit knowledge does not transfer to a language model. The specification is all it has.

The quality attributes in §2.4 — unambiguous, complete, verifiable — are the minimum bar for requirements that will drive AI-assisted generation. A requirement that fails any of these attributes is an invitation for the model to fill in the missing constraint with a plausible guess.

---
