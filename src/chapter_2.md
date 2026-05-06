# Chapter 2: Requirements Engineering and Specification

> *"The hardest single part of building a software system is deciding precisely what to build."*
> — Fred Brooks, *The Mythical Man-Month* (1975)

---

In 2005, the FBI cancelled its Virtual Case File system — a digital case management platform four years and $170 million in the making — without deploying it to a single agent. The contractor had built what was asked. The problem was that what was asked had changed more than 400 times during development, each change small and seemingly reasonable, until the accumulated requirements bore no relationship to the original architecture or budget ([US DOJ OIG, 2005](https://oig.justice.gov/sites/default/files/legacy/reports/FBI/a0507/final.pdf)). The FBI spent another $451 million on a replacement. The failure was not technical. It was a failure to define, manage, and hold to what the system actually needed to do. That discipline — deciding precisely what to build, and making that decision rigorous enough to build from — is requirements engineering. It is the highest-leverage work in any software project, and in an AI-assisted workflow it is the only work that a language model cannot do for you.

---

## Learning Objectives

By the end of this chapter, you will be able to:

1. Explain the purpose and phases of requirements engineering.
2. Apply multiple elicitation techniques to gather requirements from stakeholders.
3. Distinguish between functional and non-functional requirements and write both clearly.
4. Define epics, user stories, and acceptance criteria, and construct each for a realistic system.
5. Write a Definition of Done for a software team.
6. Use an LLM to generate and critique requirements, and explain how specification quality determines the quality of AI-generated outputs.

---

## 2.1 What Is Requirements Engineering?

Requirements engineering (RE) is the process of defining, documenting, and maintaining the requirements for a software system. It sits at the beginning of every software project, and its quality has an outsized effect on everything that follows: design decisions, implementation choices, testing strategies, and ultimately whether the system delivers value to its users.

The cost of fixing a requirements defect grows dramatically as development progresses. Research by Boehm, B. W., & Papaccio, P. N. ([1988](https://acolleoni.wordpress.com/wp-content/uploads/2012/02/boehm-papaccio-understanding-software-costs.pdf)) found that defects discovered during requirements cost roughly 1–2 units to fix; the same defect discovered during testing costs 10–100 units; discovered in production, it can cost 100–1000 units. Getting requirements right early is one of the highest-return investments in software engineering.

Requirements engineering comprises four main activities:

1. **Elicitation**: Discovering what stakeholders need
2. **Analysis**: Resolving conflicts, prioritising, and checking feasibility
3. **Specification**: Documenting requirements in a clear, agreed form
4. **Validation**: Confirming that documented requirements reflect actual stakeholder needs

These activities are not strictly sequential. In practice, they iterate: elicitation reveals conflicts that require analysis; analysis raises new questions that require further elicitation; validation reveals gaps that require re-specification.

---

## 2.2 Eliciting Requirements

Elicitation is the most people-intensive phase of requirements engineering. Requirements do not simply exist waiting to be discovered — they must be actively constructed through dialogue between engineers and stakeholders.

Stakeholders include anyone with a stake in the system:

- **Users**: People who interact with the system directly
- **Clients / customers**: People or organisations paying for or commissioning the system
- **Domain experts**: People with specialist knowledge the system must encode
- **Regulators**: Bodies whose rules constrain the system
- **Developers and operators**: People who build and run the system

### 2.2.1 Interviews

One-on-one or small group interviews are the most common elicitation technique. They allow engineers to explore individual stakeholders' perspectives in depth, ask follow-up questions, and observe non-verbal cues.

**Structured interviews** use a fixed set of questions, making responses comparable across stakeholders. **Semi-structured interviews** use a prepared guide but allow the interviewer to follow interesting threads. **Unstructured interviews** are open-ended conversations — useful early in a project when the problem space is poorly understood.

Effective interview questions:
- "Walk me through a typical day in your role. Where does [the system] fit in?"
- "What is the most frustrating part of the current process?"
- "What would success look like for you, six months after this system goes live?"
- "What happens when [edge case]? How do you handle that today?"

### 2.2.2 Workshops

Requirements workshops bring multiple stakeholders together in a structured session facilitated by a trained requirements engineer. They are particularly effective for resolving conflicts between stakeholder groups and building shared understanding quickly.

Joint Application Development (JAD) sessions ([Wood & Silver, 1995](https://www.wiley.com/en-us/Joint+Application+Development-p-9780471042075)) are a formalised workshop technique in which developers and users jointly define system requirements over 1–5 days. The intensity accelerates decision-making and builds stakeholder buy-in.

### 2.2.3 Observation and Ethnography

Sometimes the best way to understand requirements is to watch people do their work. *Contextual inquiry* ([Beyer & Holtzblatt, 1998](https://www.elsevier.com/books/contextual-design/beyer/978-0-08-050612-3)) involves working alongside users in their natural environment, observing what they actually do rather than what they say they do. This often surfaces tacit knowledge — practices and workarounds that users perform automatically and would never think to mention in an interview.

### 2.2.4 Personas

Once raw data has been gathered through interviews, workshops, and observation, engineers need a way to synthesise what they have learned into a shared understanding of who the system's users actually are. [*Personas*](https://uxpressia.com/blog/how-to-create-persona-guide-examples) are fictitious but research-grounded archetypes that represent the goals, behaviours, and frustrations of distinct user groups.

A persona is not a demographic profile — it is a behavioural model. A well-formed persona captures:

- **Goals**: what the user is trying to achieve (end goals, not task goals)
- **Behaviours**: how the user currently works, including workarounds and habits
- **Pain points**: where existing systems or processes fail them
- **Context**: environment, skill level, constraints (time pressure, device, connectivity)

**Example persona for a task management system:**

> **Jordan, the Overwhelmed Project Manager** — manages 3 concurrent projects across distributed teams. Switches between a laptop and phone throughout the day. Needs to reassign tasks quickly when team members go on leave. Frustrated by notification overload and by systems that require too many clicks to complete routine actions.

Personas serve two practical functions in requirements engineering. First, they act as a *reality check* during elicitation: "would Jordan actually use this feature?" surfaces requirements that look good on paper but serve no real user. Second, they anchor user stories — each story can be written from the perspective of a named persona, keeping abstract requirements grounded in observable behaviour.

**Limitation**: personas are only as good as the research behind them. Personas invented without observational or interview data tend to reflect developer assumptions rather than user reality, and can actively mislead the team.

### 2.2.5 Document Analysis

Existing documents — process manuals, legacy system specifications, regulatory guidelines, error logs, support tickets — are a rich source of requirements for systems that replace or augment existing functionality. Analysing support tickets reveals the most common failure modes of a current system; regulatory guidelines reveal mandatory constraints.

### 2.2.6 Prototyping

Showing stakeholders a low-fidelity prototype (wireframes, paper mockups, a clickable UI mockup) is often more effective than describing a system in words. Prototypes make abstract requirements concrete and frequently reveal misunderstandings that would otherwise persist until late in development.

---

## 2.3 Functional and Non-Functional Requirements

All requirements can be classified as either functional or non-functional.

### 2.3.1 Functional Requirements

Functional requirements describe *what* the system must do — specific behaviours, functions, or features. They define the interactions between the system and its environment.

**Format**: Functional requirements are often written as:
> The system shall [action] [object] [condition/qualifier].

**Examples for a task management system:**

- The system shall allow authenticated users to create tasks with a title, description, due date, and priority level.
- The system shall allow project managers to assign tasks to one or more team members.
- The system shall send an email notification to an assignee within 5 minutes of being assigned a task.
- The system shall allow users to filter tasks by status (open, in progress, completed, cancelled).

### 2.3.2 Non-Functional Requirements

Non-functional requirements (NFRs) describe *how* the system must behave — quality attributes that constrain the system's operation. They are sometimes called quality attributes or system properties.

NFRs are consistently under-specified in practice and disproportionately responsible for system failures. A system that does the right thing slowly, insecurely, or unreliably has failed on its NFRs — and those failures are often invisible until they manifest as outages, breaches, or regulatory penalties.

Key categories of non-functional requirements ([ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html)):

| Category | Description | Example |
|---|---|---|
| **Performance** | Speed and throughput | The API shall respond to 95% of requests within 200ms under a load of 1,000 concurrent users. |
| **Reliability** | Uptime and fault tolerance | The system shall achieve 99.9% uptime (≤8.7 hours downtime per year). |
| **Security** | Protection from threats | All data at rest shall be encrypted using AES-256. |
| **Scalability** | Ability to handle growth | The system shall support up to 100,000 active users without architectural changes. |
| **Usability** | Ease of use | A new user shall be able to create their first task within 3 minutes of registering. |
| **Maintainability** | Ease of change | All modules shall have unit test coverage of at least 80%. |
| **Portability** | Ability to run in different environments | The system shall run on any Linux environment with Python 3.11+. |
| **Compliance** | Adherence to regulations | The system shall comply with GDPR requirements for personal data storage and processing. |

**The danger of vague NFRs**: Non-functional requirements must be *measurable* to be useful. "The system should be fast" is not a requirement — it is a wish. "The API shall respond to 95% of requests within 200ms under a load of 1,000 concurrent users" is testable.

### 2.3.3 The FURPS+ Model

The FURPS+ model ([Grady, 1992](https://dl.acm.org/doi/10.1145/155360.155361)) provides a checklist for ensuring requirements coverage:

- **F**unctionality: Features and capabilities
- **U**sability: User interface and user experience
- **R**eliability: Availability, fault tolerance, recoverability
- **P**erformance: Speed, throughput, capacity
- **S**upportability: Testability, maintainability, portability
- **+**: Constraints (design, implementation, interface, physical)

---

## 2.4 Quality Attributes of Good Requirements

Individual requirements should satisfy the following quality criteria. The IEEE 830 standard ([IEEE, 1998](https://standards.ieee.org/ieee/830/1222/)) and its successor ISO/IEC/IEEE 29148 ([2018](https://www.iso.org/standard/72052.html)) are the canonical references.

| Attribute | Description | Bad Example | Good Example |
|---|---|---|---|
| **Correct** | Accurately represents stakeholder needs | — | Validated with stakeholders |
| **Unambiguous** | Has only one possible interpretation | "The system shall be user-friendly" | "A new user shall create their first task in under 3 minutes" |
| **Complete** | Covers all necessary conditions | "Users can log in" | "Users can log in with email/password; failed attempts are logged; accounts lock after 5 failures" |
| **Consistent** | Does not conflict with other requirements | Two requirements with contradictory session expiry rules | All session management requirements align |
| **Verifiable** | Can be tested or inspected | "The system shall be reliable" | "The system shall achieve 99.9% uptime" |
| **Traceable** | Can be linked to its source | Requirement with no stakeholder owner | Requirement tagged to specific stakeholder interview |
| **Prioritised** | Ranked by importance | No priority information | MoSCoW category assigned |

---

## 2.5 Epics, User Stories, and Work Items

In Agile teams, requirements are typically captured as a hierarchy of work items:

```
Epic
 └── Feature / Capability
      └── User Story
           └── Task (implementation subtask)
```

### 2.5.1 Epics

An *epic* is a large body of work that can be broken down into smaller stories. Epics represent significant chunks of functionality — typically too large to complete in a single sprint.

**Example epics for a task management system:**

- User Authentication and Authorisation
- Task Lifecycle Management (create, assign, update, complete)
- Notifications and Alerts
- Reporting and Analytics

### 2.5.2 User Stories

Each epic decomposes into user stories — small, independently deliverable increments of value.

**Epic: Task Lifecycle Management**

| ID | User Story |
|---|---|
| US-01 | As a user, I want to create a task with a title and description so that I can record work that needs to be done. |
| US-02 | As a user, I want to assign a due date to a task so that I can track deadlines. |
| US-03 | As a project manager, I want to assign a task to a team member so that responsibilities are clear. |
| US-04 | As a user, I want to mark a task as complete so that the team can see progress. |
| US-05 | As a user, I want to add comments to a task so that I can communicate context without leaving the tool. |

### 2.5.3 Story Points

*Story points* are a unit of measure for estimating the relative effort or complexity of user stories. They are intentionally abstract — they do not map directly to hours or days — encouraging teams to think about relative complexity rather than precise time estimates.

Teams typically use a modified Fibonacci sequence: **1, 2, 3, 5, 8, 13, 21**. The increasing gaps reflect growing uncertainty in estimating large, complex work.

**Planning Poker** is a common estimation technique ([Grenning, 2002](https://wingman-sw.com/articles/planning-poker)): each team member privately selects a card with their estimate; all cards are revealed simultaneously; significant discrepancies prompt discussion until the team reaches consensus.

Story points enable **velocity tracking** — the total points completed per sprint gives the team's *velocity*, which predicts future throughput and informs release planning.

### 2.5.4 Tasks

Each user story is implemented through one or more *tasks* — specific technical actions. Tasks are not user-visible; they are engineering sub-steps.

**Example tasks for US-03 (assign a task to a team member):**

- Design the `POST /tasks/{id}/assign` API endpoint
- Implement the assignment logic and database update
- Write unit tests for the assignment service
- Write integration tests for the assignment endpoint
- Update API documentation

---

## 2.6 Prioritisation: The MoSCoW Framework

Once user stories are written, the team must decide which to build first. The **MoSCoW framework** ([Clegg & Barker, 1994](https://www.dsdm.org/)) provides a shared vocabulary for this:

| Category | Meaning | Guideline |
|---|---|---|
| **M**ust Have | Non-negotiable; the system cannot launch without these | ~60% of effort |
| **S**hould Have | Important but not vital; workarounds exist if omitted | ~20% of effort |
| **C**ould Have | Nice to have; included only if time permits | ~20% of effort |
| **W**on't Have | Explicitly excluded from this release | Documented, not built |

The "Won't Have" category is often the most valuable: it makes explicit what is being deliberately deferred, turning unspoken assumptions into shared agreements.

**Example — a task management application:**

| Feature | MoSCoW |
|---|---|
| Create, read, update, delete tasks | Must Have |
| Assign tasks to team members | Must Have |
| Email notifications on task assignment | Should Have |
| Drag-and-drop task reordering | Could Have |
| Integration with Slack | Won't Have (this release) |

---

## 2.7 Scope Creep

Even with user stories and prioritisation in place, projects face a persistent risk: *scope creep* — the gradual, uncontrolled expansion of scope beyond its original boundaries. It is one of the most common causes of project failure ([PMI, 2021](https://www.pmi.org/learning/library/scope-creep-causes-effects-solutions-6181)).

Scope creep happens when:

- Stakeholders request new features after the project has started
- Requirements are poorly defined, leaving room for interpretation
- The team adds features without formal approval
- External factors force new work mid-project

MoSCoW directly addresses this: by explicitly documenting what is *Won't Have*, teams create a shared boundary that makes adding new scope a visible, deliberate decision rather than a gradual drift.

---

## 2.8 Acceptance Criteria

*Acceptance criteria* define the specific conditions that must be satisfied for a user story to be considered done. They bridge requirements and testing: each acceptance criterion should be directly testable.

The most common format is **Gherkin** — a structured natural language syntax used by the Cucumber testing framework ([Wynne & Hellesøy, 2012](https://pragprog.com/titles/hwcuc/the-cucumber-book/)):

```gherkin
Given [some initial context]
When  [an action occurs]
Then  [an observable outcome]
```

**Example — US-03: Assign a task to a team member**

```gherkin
Scenario: Successfully assigning a task
  Given I am logged in as a project manager
  And a task with ID "123" exists in my project
  And a team member "alice@example.com" exists in my project
  When I send POST /tasks/123/assign with body {"assignee": "alice@example.com"}
  Then the response status code is 200
  And the task's assignee field is updated to "alice@example.com"
  And alice receives an email notification within 5 minutes

Scenario: Attempting to assign to a non-member
  Given I am logged in as a project manager
  And a task with ID "123" exists in my project
  When I send POST /tasks/123/assign with body {"assignee": "nonmember@example.com"}
  Then the response status code is 400
  And the response body contains {"error": "User is not a member of this project"}

Scenario: Attempting to assign without permission
  Given I am logged in as a regular user (not a project manager)
  When I send POST /tasks/123/assign with body {"assignee": "alice@example.com"}
  Then the response status code is 403
  And the response body contains {"error": "Insufficient permissions"}
```

Well-written acceptance criteria cover:
- The **happy path** (the successful scenario)
- **Error cases** (invalid input, unauthorised access)
- **Edge cases** (boundary conditions, concurrent operations)

---

## 2.9 Definition of Done

The *Definition of Done* (DoD) is a shared agreement about what "complete" means for any piece of work. It is a quality gate: a story is not done until it satisfies every item on the DoD checklist ([Schwaber & Sutherland, 2020](https://scrumguides.org/scrum-guide.html)).

**Example Definition of Done for the course project:**

- [ ] All acceptance criteria pass
- [ ] Unit tests written and passing (minimum 80% coverage for new code)
- [ ] Integration tests written and passing
- [ ] Code reviewed by at least one other team member
- [ ] Linter and type checker pass with no errors
- [ ] API documentation updated (if applicable)
- [ ] No new security vulnerabilities introduced (verified by automated scan)
- [ ] Deployed to the staging environment and manually tested

A DoD prevents "almost done" from becoming a permanent state and makes quality expectations explicit and consistent across the team.

---

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

## Review Questions

1. A hospital is replacing its paper-based ward scheduling system with a digital one. The ward manager says: "We just need something that works like the paper system, but on a computer." Identify two elicitation techniques from §2.2 that you would use and explain what each would reveal that the ward manager's statement does not.

2. A development team has documented the following requirements for a healthcare appointment system: "The system shall allow patients to book appointments" and "The system shall be secure and fast." Classify each as functional or non-functional, identify which quality attributes from §2.4 each violates, and rewrite the deficient ones so they are verifiable.

3. Write three user stories and at least two Gherkin acceptance criteria scenarios for the following epic: *"As a student, I want to track my assignment deadlines so that I do not miss submissions."* Your scenarios must include one happy path and one error or edge case.

4. A fintech startup building a mobile payment app has produced a backlog of 47 user stories but cannot agree on what to build first. Apply MoSCoW to the following features and justify each classification: (a) user registration and login; (b) payment confirmation notifications; (c) transaction history export to CSV; (d) cryptocurrency wallet integration; (e) dark mode. Then identify which item most commonly triggers conflict in prioritisation sessions and explain why.

5. A developer is given the requirement "the system shall respond quickly" and uses an LLM to generate the corresponding API endpoint. Explain two ways this requirement causes problems in an AI-assisted workflow, rewrite it to meet the quality attributes in §2.4, and describe what changes in the LLM's output when the improved requirement is used.
