## 2.11 Key Takeaways

Requirements engineering is the discipline that determines what gets built before implementation begins. Its quality has more leverage on outcomes than any other phase of development. The key ideas from this chapter:

1. **Requirements are constructed, not collected.** They emerge through dialogue, observation, and iteration between engineers and stakeholders — not from a single interview or a sign-off on a specification document.

2. **The four RE activities loop.** Elicitation, analysis, specification, and validation do not proceed in sequence. Validation uncovers gaps that require re-elicitation; analysis surfaces conflicts that require new specification.

3. **The functional/non-functional distinction matters.** Functional requirements define what the system does; non-functional requirements define how well. NFRs are consistently under-specified in practice and disproportionately responsible for system failures — a system that crashes under load or exposes user data has failed on its NFRs, regardless of how correct its functional behaviour is.

4. **Good requirements are measurable.** Unambiguous, complete, consistent, verifiable, and traceable are not style preferences — they are the minimum attributes that allow a requirement to be tested. "The system shall be reliable" is a wish. "The system shall achieve 99.9% uptime" is a requirement.

5. **Agile work items form a hierarchy.** Epics decompose into user stories; user stories decompose into tasks. Acceptance criteria in Gherkin format connect user stories directly to test cases, closing the loop between requirements and verification.

6. **MoSCoW makes trade-offs explicit.** The "Won't Have" category is as valuable as "Must Have" — it converts unspoken assumptions into shared agreements and makes adding new scope a visible decision rather than a gradual drift.

7. **In an AI-native workflow, specification quality is code quality.** Vague requirements do not just produce ambiguous documents — they produce incorrect, insecure, or hallucinated code. The quality attributes in §2.4 are the minimum bar for requirements that will drive AI-assisted generation. The more precisely a requirement is specified, the less room the model has to invent behaviour you did not intend.

---

### Review Questions

1. A hospital is replacing its paper-based ward scheduling system with a digital one. The ward manager says: "We just need something that works like the paper system, but on a computer." Identify two elicitation techniques from §2.2 that you would use and explain what each would reveal that the ward manager's statement does not.

2. A development team has documented the following requirements for a healthcare appointment system: "The system shall allow patients to book appointments" and "The system shall be secure and fast." Classify each as functional or non-functional, identify which quality attributes from §2.4 each violates, and rewrite the deficient ones so they are verifiable.

3. Write three user stories and at least two Gherkin acceptance criteria scenarios for the following epic: *"As a student, I want to track my assignment deadlines so that I do not miss submissions."* Your scenarios must include one happy path and one error or edge case.

4. A fintech startup building a mobile payment app has produced a backlog of 47 user stories but cannot agree on what to build first. Apply MoSCoW to the following features and justify each classification: (a) user registration and login; (b) payment confirmation notifications; (c) transaction history export to CSV; (d) cryptocurrency wallet integration; (e) dark mode. Then identify which item most commonly triggers conflict in prioritisation sessions and explain why.

5. A developer is given the requirement "the system shall respond quickly" and uses an LLM to generate the corresponding API endpoint. Explain two ways this requirement causes problems in an AI-assisted workflow, rewrite it to meet the quality attributes in §2.4, and describe what changes in the LLM's output when the improved requirement is used.
