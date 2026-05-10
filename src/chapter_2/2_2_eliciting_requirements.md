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
