## 1.5 Agile Software Development

Agile is not a single methodology but a family of approaches united by the values in the [Agile Manifesto](https://agilemanifesto.org/) — a document authored in 2001 by seventeen software practitioners who were frustrated with heavyweight, documentation-driven processes. The core insight is that software requirements and solutions evolve through collaboration, and that the ability to respond to change is more valuable than adherence to a plan.

![The Agile Manifesto](../images/chapter-1-agile-manifesto.png)

The Manifesto articulates four core **values** — each expressed as a preference, not an absolute:

| We value… | …over |
|---|---|
| **Individuals and interactions** | Processes and tools |
| **Working software** | Comprehensive documentation |
| **Customer collaboration** | Contract negotiation |
| **Responding to change** | Following a plan |

Agile teams work in short cycles called *iterations* or *sprints*, typically 1–4 weeks long. Each iteration produces a working, tested increment of software. Stakeholders review the increment and provide feedback that informs the next iteration.

Key Agile **principles** include:

- Deliver working software frequently (weeks, not months)
- Welcome changing requirements, even late in development
- Business people and developers work together daily
- Simplicity — the art of maximising the amount of work *not* done — is essential

Agile values and principles are deliberately abstract — they describe *what* to aim for, not *how* to organise teams or structure work. Specific frameworks fill that gap. The two most widely adopted are **Scrum**, which prescribes a structured sprint cycle with defined roles and ceremonies, and **Kanban**, which takes a more continuous, flow-based approach with fewer fixed rules.

### 1.5.1 Scrum

Scrum is the most widely adopted Agile framework ([Schwaber & Sutherland, 2020](https://scrumguides.org/scrum-guide.html)). It defines specific roles, events, and artefacts:

**Roles:**
- **Product Owner**: Represents stakeholders; owns and prioritises the product backlog
- **Scrum Master**: Facilitates the process; removes impediments; coaches the team
- **Development Team**: Self-organising group that delivers the increment

**Events:**
- **Sprint**: A time-boxed iteration of 1–4 weeks
- **Sprint Planning**: The team selects backlog items and plans the sprint
- **Daily Scrum**: A 15-minute daily standup to synchronise and identify blockers
- **Sprint Review**: The team demonstrates the increment to stakeholders
- **Sprint Retrospective**: The team reflects on the process and identifies improvements

**Artefacts:**
- **Product Backlog**: An ordered list of everything that might be needed in the product
- **Sprint Backlog**: The backlog items selected for the current sprint, plus the delivery plan
- **Increment**: The sum of all completed backlog items at the end of a sprint

![Scrum Framework](../images/chapter-1-scrum.png)

### 1.5.2 Kanban

Kanban, adapted from Toyota's manufacturing system by David Anderson ([Anderson, 2010](https://kanbanbooks.com/)), is a flow-based method that focuses on visualising work, limiting work in progress (WIP), and continuously improving flow.

A Kanban board visualises work as cards moving through columns:

![Kanban Board](../images/chapter-1-kanban.png)

**Key Kanban practices:**
- **Visualise the workflow**: Make all work and its status visible
- **Limit WIP**: Prevent overloading; finish before starting more
- **Manage flow**: Track cycle time and throughput; identify bottlenecks
- **Improve collaboratively**: Use data to drive continuous improvement

Kanban suits teams with highly variable incoming work (e.g., support and maintenance teams) or those who want a lighter-weight alternative to Scrum's ceremonies.


---
