## 12.8 Key Takeaways

The legal and ethical landscape for AI-generated code is unsettled and changing quickly. The key ideas from this chapter:

1. **Copyright, patents, and trade secrets are the three main IP protection mechanisms for software.** For most software, copyright is the operative form — it attaches automatically on creation, without registration, and it governs whether anyone can copy, distribute, or build on your code.

2. **Open source licences are not interchangeable.** Permissive licences (MIT, Apache 2.0) allow incorporation into proprietary software; copyleft licences (GPL, AGPL) require derivative works to remain open source. Mixing incompatible licences creates hidden legal obligations. Check compatibility before adopting a dependency.

3. **AI-generated code exists in a copyright grey zone.** Purely AI-generated output may have no copyright holder — it may effectively be in the public domain. Where a human makes meaningful creative choices in directing and refining AI output, the work may be copyrightable as human-authored; the legal threshold for this is not yet settled.

4. **You are accountable for AI-generated code you ship.** Responsibility does not transfer to the AI vendor. The engineer who reviews, accepts, and deploys the code is the responsible party — regardless of which tool produced the first draft.

5. **Privacy regulations impose concrete obligations on the code you write.** GDPR's right to erasure, data minimisation, and lawful basis requirements are not satisfied by default by AI-generated code — they must be specified in the prompt. The same applies to CCPA and the Australian Privacy Act for their respective jurisdictions.

6. **Do not send personal data to external AI APIs without a Data Processing Agreement.** Names, email addresses, and IP addresses are personal data under GDPR. Executing a DPA with the AI provider is a legal requirement before sending them, not an optional precaution.

7. **Organisational AI governance starts with a use policy that is actually enforced.** The policy must specify which tools are approved, what data may be sent, and how AI-generated code is reviewed before production use. The Samsung incident illustrates what happens in the absence of one.

8. **The EU AI Act classifies AI coding assistants as minimal risk.** If you are *building* a high-risk AI system — for medical diagnosis, hiring, or credit decisions — significantly stricter requirements apply, including conformity assessments, transparency obligations, and mandated human oversight.

---

### Review Questions

1. Your team wants to add an AGPL-licensed library to your SaaS product's backend. The product charges a monthly subscription fee and does not distribute compiled binaries. A colleague argues: "AGPL only applies when you distribute software — since we're SaaS, we don't distribute anything, so we're fine." Evaluate this argument. What obligation, if any, does the AGPL create for a network-accessible service, and what would you recommend?

2. A developer uses GitHub Copilot to generate approximately 40% of a new fintech product's codebase. The CTO wants to register the codebase as a company copyright and is confident this is straightforward. What are the obstacles to this, and what documentation practices — starting today — would strengthen the company's legal position?

3. You are implementing a user data export feature in a FastAPI application. You submit the following prompt: *"Add a GET /users/{user_id}/export endpoint that returns all user data as JSON."* The AI returns a function that serialises the `User` SQLAlchemy model directly. Identify at least two GDPR compliance gaps in the generated code, then write the revised prompt that addresses them.

4. A junior developer generates a user authentication module using an AI assistant and merges it without a security review. The module contains a timing vulnerability in the password comparison function that leaks whether a username exists. When the issue is reported, the developer says: "The AI wrote it — that's on the tool, not me." As tech lead, how do you respond, and what specific changes would you make to the team's AI code review process to prevent this class of issue?

5. Your organisation has no AI use policy. You have been asked to draft three policy clauses before next week's sprint. Using the example clauses in Section 12.5.1 as a model, write three clauses specific to a team that builds healthcare data management software, uses external AI coding assistants daily, and is subject to GDPR. For each clause, explain the specific risk it mitigates.
