# Chapter 1: Software Engineering Fundamentals and Processes

> *"Software engineering is the establishment of and use of sound engineering principles in order to obtain economically software that is reliable and works efficiently on real machines."*
> — Friedrich Bauer, 1968 NATO Conference

---

## Learning Objectives

By the end of this chapter, you will be able to:

1. Define software and explain how it differs from hardware and other engineering products.
2. Describe the key attributes of good software and the People–Process–Technology model of software engineering.
3. Describe the historical evolution of software engineering from its origins to the present day, including the contributions of Margaret Hamilton.
4. Identify real-world software engineering failures and the lessons they teach.
5. Compare Waterfall, Incremental, Agile, Scrum, Kanban, and Open Source development — explaining the strengths, weaknesses, and appropriate contexts for each.

---

## 1.1 What Is Software?

Before we can engineer software well, we need to understand what software actually is.

**Software** is more than just code. It is the combination of:

- **Programs** — the executable instructions that tell a computer what to do
- **Data** — the information that programs process, including configuration files and databases
- **Documentation** — the materials that describe how to install, use, and maintain the system

This matters because the quality of a software product depends on all three. A perfectly coded program with no documentation is hard to maintain. Poorly designed data structures can cripple an otherwise elegant program.

### Examples of Software Systems

Software underpins virtually every sector of modern life:

| Domain | Example System | Purpose |
|---|---|---|
| **Healthcare** | Electronic Health Record (EHR) | Manage patient data, clinical workflows, prescriptions |
| **Finance** | Online banking platform | Account management, transactions, fraud detection |
| **E-commerce** | Amazon, Shopify | Product catalogue, payments, fulfilment tracking |
| **Transportation** | Uber, Google Maps | Route optimisation, driver dispatch, navigation |
| **Education** | LMS (Moodle, Canvas) | Course delivery, assessment, student progress tracking |

These systems share a common characteristic: they must handle real users, real data, and real consequences when things go wrong. A bug in a spreadsheet script affects one person. A bug in a hospital's prescribing system can endanger lives.

### Generic vs. Customised Products

Software products fall into two broad categories:

- **Generic products** are developed for a broad market and sold to whoever wants them. Examples include Microsoft Office, Adobe Photoshop, and operating systems like Windows. The developer controls the specification.

- **Customised products** (also called bespoke software) are built for a specific client to meet their particular requirements. Examples include a hospital's patient management system or a bank's internal risk platform. The client controls the specification.

The distinction matters for software engineering because it affects who decides what gets built, when it is done, and what constitutes success. Customised projects carry a higher risk of requirements misalignment — the client and developer must invest heavily in understanding each other.

### Why Software Is Different

Software has unique properties that distinguish it from physical engineering products and make it uniquely challenging to build well:

- **Intangible**: You cannot see, touch, or physically measure software. Quality problems can be invisible until they manifest as failures.
- **Malleable**: Unlike a bridge or an engine, software can be changed after deployment — and users expect it to be. This is both a strength and a persistent source of cost.
- **Knowledge-intensive**: Software encodes human knowledge and decision-making. Its complexity scales with the depth of the domain it models.
- **Does not wear out — but it decays**: Hardware degrades physically over time. Software does not rust, but it *decays* as the environment around it changes: operating systems upgrade, dependencies are deprecated, user expectations evolve.

### Unique Challenges

These properties create challenges with no clean parallel in other engineering disciplines:

- **No universal theories or methods.** Civil engineers can consult structural mechanics and established load calculations. Software engineering has no equivalent universal laws — the field lacks a unified theoretical foundation that determines how complex systems should be built.
- **Extraordinarily fast evolution.** Languages, frameworks, and platforms that are standard today may be obsolete in five years. This pace of change means software engineers must be continuous learners.
- **Invisible complexity.** A large software system can contain billions of interacting states. Unlike a physical structure, you cannot visually inspect it for flaws.

These properties mean software engineering has no perfect analogy in civil or mechanical engineering. Fred Brooks captured this in 1987 when he observed that software has no "silver bullet" — no single technique that delivers an order-of-magnitude improvement in productivity, reliability, or simplicity ([Brooks, 1987](https://en.wikipedia.org/wiki/No_Silver_Bullet)).

### The Role of Software in Society

Software is not merely a technical artefact — it is an economic and social force. Technology sectors, of which software is the core, account for a growing share of GDP in developed economies. More critically, essential infrastructure — hospitals, banks, transport networks, power grids — runs on software. When that software fails, the consequences extend far beyond a frustrated user.

This is why software engineering is taken seriously as a discipline. Building software well is not just a technical aspiration; it is an ethical and economic responsibility.

---

## 1.2 What Is Software Engineering?

Software engineering is the disciplined application of engineering principles to the design, development, testing, and maintenance of software systems. Unlike informal programming, software engineering emphasises process, quality, collaboration, and long-term maintainability.

The term was deliberately chosen. In 1968, NATO convened a conference in Garmisch, Germany, to address what organisers called the "software crisis" — a widespread recognition that software projects were routinely over budget, delivered late, and unreliable ([Naur & Randell, 1969](http://homepages.cs.ncl.ac.uk/brian.randell/NATO/nato1968.PDF)). The goal of using the word *engineering* was aspirational: to bring to software the same rigour, predictability, and professionalism that civil or mechanical engineers brought to bridges and engines.

That aspiration has guided the field ever since — and it remains relevant today, even as the tools, languages, and collaborators (including AI systems) have changed dramatically.

![Attendees at the 1968 NATO Software Engineering Conference in Garmisch, Germany](images/nato-conference-photo.png)
*Photograph from 1968 NATO Software Engineering Conference (University of Newcastle photo)*

### Core Definitions

| Term | Definition |
|---|---|
| **Software** | Programs, data, and documentation that together form a usable system |
| **Software Engineering** | The disciplined application of engineering principles to software development |
| **Software Process** | The structured set of activities required to develop a software system |
| **Software Product** | The artefact produced by the software process — the deployed system and its documentation |

### Computer Science vs. Software Engineering

Computer Science and Software Engineering are related but distinct disciplines — a distinction that was itself a product of the 1960s software crisis:

- **Computer Science** focuses on the theoretical foundations of computation — algorithms, data structures, complexity theory, and the mathematical underpinnings of computing. It asks: *what can be computed, and how efficiently?*

- **Software Engineering** focuses on the practical construction of software systems — how to manage complexity, collaborate in teams, ensure quality, and deliver systems that work reliably in the real world. It asks: *how do we build software that is dependable, efficient, and maintainable at scale?*

Both are valuable. A software engineer who understands computer science makes better architectural decisions. A computer scientist who understands software engineering can take theoretical ideas into production.

### The People–Process–Technology Model

Software engineering is often described using the **People–Process–Technology (PPT)** model — sometimes called the "golden triangle" of software development.

```
         People
           △
          / \
         /   \
        /     \
Process ——————— Technology
```

- **People**: Developers, architects, testers, product owners, and end users. Technology can amplify people's capabilities, but it cannot replace their judgement, creativity, or communication.
- **Process**: The structured activities through which software is built — requirements gathering, design, implementation, testing, deployment, and maintenance.
- **Technology**: The programming languages, frameworks, tools, and platforms used to build the system.

All three must work together. The best technology cannot compensate for poor processes. Excellent processes cannot succeed without skilled people. And talented people working without structure tend to create systems that only they understand.

### Attributes of Good Software

What does it mean for software to be *good*? Sommerville (2016) identifies four essential attributes that characterise high-quality software:

| Attribute | Description |
|---|---|
| **Maintainability** | The software can be evolved to meet changing needs. Since requirements always change, maintainability is fundamental to long-term value. |
| **Dependability and Security** | The software is reliable (fails rarely), safe (does not cause damage), and secure (resists malicious attacks). |
| **Efficiency** | The software does not waste computational resources — memory, processing, energy, or network bandwidth. |
| **Acceptability** | The software is usable by its intended users. It must be understandable, meet their needs, and comply with relevant standards. |

These attributes are not independent. A highly efficient system that users cannot figure out how to operate fails on acceptability. A secure system that crashes daily fails on dependability. Good software engineering requires balancing all four throughout development — not optimising one at the expense of the others.

### The Central Motivation

The central question of software engineering is: **How do we build high-quality software in a cost-effective way?**

This sounds simple. In practice, it is extraordinarily difficult. Quality and speed are often in tension. Security and simplicity conflict. New features compete with maintenance. Every chapter of this book addresses a different dimension of this challenge.

---

## 1.3 A Brief History of Software Engineering

Understanding where software engineering came from helps explain why its practices exist — and why they are changing again now.

### 1.3.1 The Early Years (1940s–1960s)

The first programmers wrote machine code directly — sequences of binary instructions hand-crafted for specific hardware. Programming was considered a clerical task; the real intellectual work was thought to be mathematics and system design.

As software grew more complex through the 1950s, assembly languages and early high-level languages like FORTRAN (1957) and COBOL (1959) emerged. Programs grew from hundreds of lines to hundreds of thousands. Managing this complexity became a serious problem.

One pioneer who changed the field's self-understanding was **Margaret Hamilton**. In the early 1960s, Hamilton joined MIT's Instrumentation Laboratory, where she led the team responsible for developing the in-flight software for NASA's Apollo program. Her team's software had to be extraordinarily reliable — a failure mid-mission could be fatal. Hamilton introduced rigorous software development practices, including priority-based scheduling, error detection and recovery, and human-in-the-loop design. Her team's software famously helped save the Apollo 11 mission when a computer alarm triggered during the lunar descent.

Hamilton is widely credited with coining the term *software engineering*, arguing that software development deserved the same rigour and professional recognition as other engineering disciplines. Her work demonstrated — before the field had a name — that software could be, and had to be, an engineering endeavour.

### 1.3.2 The Software Crisis and Structured Programming (1968–1980s)

The 1968 NATO conference crystallised the software crisis. Projects like the IBM OS/360 operating system — documented famously by Fred Brooks in *The Mythical Man-Month* ([Brooks, 1975](https://en.wikipedia.org/wiki/The_Mythical_Man-Month)) — demonstrated that adding more programmers to a late project often made it later. Software complexity was not a resource problem; it was a conceptual one.

The response was *structured programming*, championed by Dijkstra, Hoare, and Wirth. Programs should be built from clear, hierarchical control structures — sequences, selections, and iterations — rather than the chaos of `GOTO` statements. This was the beginning of thinking about software as something that could be reasoned about formally.

### 1.3.3 Object-Oriented Programming and Software Patterns (1980s–1990s)

The 1980s and 1990s saw the rise of object-oriented programming (OOP) — a paradigm in which software is modelled as interacting objects with state and behaviour. Languages like C++, Smalltalk, and later Java brought OOP to mainstream development.

In 1994, the "Gang of Four" — Gamma, Helm, Johnson, and Vlissides — published *Design Patterns: Elements of Reusable Object-Oriented Software* ([Gamma et al., 1994](https://en.wikipedia.org/wiki/Design_Patterns)), cataloguing 23 reusable solutions to common software design problems. These patterns are covered in depth in Chapter 3.

### 1.3.4 The Internet Era and Agile Methods (1990s–2000s)

The World Wide Web transformed software from shrink-wrapped products shipped on disks to continuously evolving services. Release cycles had to shrink from years to weeks. Traditional plan-driven methods struggled to keep pace.

In 2001, seventeen software practitioners gathered in Snowbird, Utah, and published the [Agile Manifesto](https://agilemanifesto.org/) — a short document that valued:

> *Individuals and interactions over processes and tools*
> *Working software over comprehensive documentation*
> *Customer collaboration over contract negotiation*
> *Responding to change over following a plan*

Agile methods — including Scrum, Extreme Programming (XP), and Kanban — spread rapidly through the industry. They emphasised short iterations, continuous feedback, and adaptive planning rather than upfront specification.

### 1.3.5 DevOps and Continuous Delivery (2010s)

As agile teams delivered software faster, operations teams struggled to deploy and maintain it. The DevOps movement ([Kim et al., 2016](https://itrevolution.com/product/the-devops-handbook/)) broke down the wall between development and operations, promoting:

- Continuous integration (CI): merging code frequently, building and testing automatically
- Continuous delivery (CD): keeping software always in a deployable state
- Infrastructure as code: managing servers and environments through version-controlled scripts

This shift made the pipeline from code commit to production deployment a first-class engineering concern — covered in depth in Chapter 4.

### 1.3.6 The AI Era (2020s–Present)

In 2021, GitHub released Copilot, powered by OpenAI Codex — a large language model trained on billions of lines of public code. For the first time, AI could generate syntactically correct, contextually relevant code at the level of individual functions and files.

By 2023, models like GPT-4 and Claude could engage in multi-turn conversations about software design, debug complex issues, write test suites, and generate entire application scaffolds from natural language descriptions. 

By 2024–2025, *AI coding agents*, powered by agentic AI architecture, that can plan, use tools, and execute code autonomously — began to handle multi-step engineering tasks with minimal human intervention.

This is where this book begins.

![From Copilot to autonomous agents: AI has evolved from completing code to planning, building, testing, and delivering software end to end.](images/the-rise-of-ai-in-se.png)
*From Copilot to autonomous agents: AI has evolved from completing code to planning, building, testing, and delivering software end to end. (Illustrated by AI)*

---

## 1.4 When Software Fails

Software failures are not merely inconveniences. They cost money, erode trust, and — in safety-critical domains — cost lives. Understanding real failures is one of the most important things a software engineer can do. Every practice introduced in this book exists because its absence has caused failures like the ones below.

### Case Study 1: The MYKI Ticketing System

[In 2005, the Victorian Government contracted a consortium to build MYKI — a smartcard-based ticketing system for Melbourne's public transport network.](https://www.audit.vic.gov.au/report/operational-effectiveness-myki-ticketing-system?section=) The project was plagued by problems from the start.

Originally estimated at around AUD$494 million and targeted for full deployment by 2007, MYKI eventually cost over AUD$1.35 billion and was years behind schedule. The Victorian Auditor-General's Office (VAGO) produced multiple critical reports on the project, finding inadequate requirements management, poor contractor oversight, and testing failures that allowed defects to reach passengers (Victorian Auditor-General's Office, 2011).

The MYKI case illustrates several recurring failure patterns:

- **Unclear and unstable requirements**: Scope changed repeatedly, leading to costly rework and disputes
- **Insufficient testing**: Defects were discovered after deployment, when they were most expensive to fix
- **Weak governance**: Problems were not escalated or addressed early enough

### Case Study 2: Commonwealth Bank and Transaction Monitoring

(In 2017, Australia's financial intelligence agency AUSTRAC commenced legal proceedings against the Commonwealth Bank of Australia (CBA), alleging more than 53,000 breaches of anti-money laundering and counter-terrorism financing laws.)[https://www.austrac.gov.au/news-and-media/media-release/austrac-and-cba-agree-700m-penalty] At the centre of the case was a software defect.

CBA's Intelligent Deposit Machines (IDMs) — automated cash deposit ATMs — included software required to send threshold transaction reports (TTRs) to AUSTRAC whenever a cash deposit exceeded AUD$10,000. A coding error introduced during a software update in 2012 caused these reports to stop being generated. The defect went undetected for nearly three years, during which time criminals used the machines to launder money. In 2018, CBA settled with AUSTRAC for AUD$700 million — the largest civil penalty in Australian corporate history at the time (AUSTRAC, 2017)[https://www.austrac.gov.au/news-and-media/media-release/austrac-and-cba-agree-700m-penalty].

The CBA case illustrates a different but equally important class of failure:

- **A single coding error**, undetected in testing, had catastrophic legal and financial consequences
- **No monitoring**: The system provided no alerting when report volumes dropped to zero
- **Compliance requirements** were not adequately translated into verifiable software behaviour

### Lessons from Failures

| Lesson | What It Means |
|---|---|
| **Requirements must be clear and stable** | Ambiguous or moving requirements lead to software that does not meet needs |
| **Testing is not optional** | Defects found in production cost an order of magnitude more than defects found early |
| **Monitor your systems** | Silent failures are dangerous; systems should report on their own health |
| **Cost of failure exceeds cost of quality** | Investing in good engineering is almost always cheaper than recovering from failure |

---

## 1.5 The Software Development Lifecycle (SDLC)

The Software Development Lifecycle (SDLC) is a structured process for planning, creating, testing, and deploying software.

### 1.5.1 Core Activities

While specific SDLC models differ in their structure and emphasis, most share a common set of core activities:

| Activity | Description |
|---|---|
| **Requirements** | Understand what the system should do — from the perspective of users, stakeholders, and regulators |
| **Design and Implementation** | Decide how the system will be structured, then write and integrate the code |
| **Verification and Validation** | *Verification*: Are we building the system right? (testing, reviews) *Validation*: Are we building the right system? (stakeholder review) |
| **Maintenance** | Fix bugs, adapt to new environments, and extend functionality after deployment |

A key insight from decades of software engineering research is that **maintenance dominates cost**. Studies consistently show that 60–80% of total software cost is incurred after initial deployment (Sommerville, 2016). This has profound implications: the decisions made during requirements and design — naming conventions, modularity, documentation — echo through the entire lifetime of a system.

### 1.5.2 The Cost of Change

Another well-established finding is that **the cost of fixing a defect rises dramatically the later it is found**. A requirement error caught in a design review costs relatively little. The same error discovered after deployment may require changes to a live system, database migrations, user retraining, and regulatory notification.

```
Relative Cost to Fix a Defect
│
│                                          ×100+
│                                    ╔══════╗
│                              ×10   ║      ║
│                        ╔═════╗     ║      ║
│                 ×5     ║     ║     ║      ║
│          ×1   ╔════╗   ║     ║     ║      ║
│          ╔═╗  ║    ║   ║     ║     ║      ║
│          ║ ║  ║    ║   ║     ║     ║      ║
└──────────╨─╨──╨────╨───╨─────╨─────╨──────╨──▶
       Requirem. Design  Code   Test  Production
```

This cost curve is the economic argument for investing in requirements, design, and testing — and for short feedback cycles. The sooner a problem is discovered, the cheaper it is to fix.

From an economic perspective, software and hardware have also swapped their relative costs. In the early days of computing, hardware was the dominant expense. Today, software development and maintenance far exceed hardware costs in most systems — which is why software engineering as a discipline commands serious investment.

### 1.5.3 SDLC Models Overview

No single development process fits every project. The right choice depends on how well requirements are understood upfront, how stable they are likely to remain, team size, risk tolerance, and regulatory context.

| Model | Approach | Best For |
|---|---|---|
| **Plan-driven (Waterfall)** | Sequential phases; each complete before the next | Stable, well-understood requirements |
| **Incremental** | Deliver in functional slices | Partial requirements; early delivery needed |
| **Agile** | Iterative; embrace change | Evolving requirements; fast feedback |
| **Open Source** | Community-driven; distributed contributions | Widely used tools and libraries |

### 1.5.4 Waterfall

The Waterfall model, introduced by Winston Royce in 1970 (though Royce actually presented it as a flawed approach in the same paper ([Royce, 1970](http://www-scf.usc.edu/~csci201/lectures/Lecture11/royce1970.pdf))), organises development as a strict sequence of phases. Each phase must be completed before the next begins. The model assumes requirements can be fully and correctly specified at the start.

![A Waterfall Software Development Process.](images/waterfall.png)
*A Waterfall Software Development Process (Illustrated by AI)*

**Strengths:**
- Clear milestones and deliverables
- Easy to manage and document
- Works well for projects with stable, well-understood requirements (e.g., certain embedded systems, regulated government contracts)

**Weaknesses:**
- Requirements almost never remain stable
- Errors discovered late are expensive to fix
- Users see no working software until the end
- Poor fit for projects with high uncertainty

### 1.5.5 The Moving Target Problem

One of the most persistent challenges in software development is that **requirements change**. This is sometimes called the *moving target problem*.

Requirements change for many legitimate reasons:

- Users discover new needs once they see early versions of the system
- The business environment shifts — market conditions, regulations, or competition
- Technology changes make new approaches possible
- Stakeholders disagree and compromise positions evolve over time

The moving target problem has two dangerous manifestations in practice:

**Feature creep** occurs when new requirements are added to a project incrementally — each one seemingly small and reasonable — until the scope has grown far beyond what was originally planned. Feature creep is among the leading causes of project overruns.

**Regression risk** arises when adding new features or fixing bugs inadvertently breaks existing functionality. Every change to a system is a potential source of new defects. Without systematic testing, regressions go undetected until they reach users. The CBA case above illustrates exactly this: a software update broke existing behaviour, and no one noticed.

Managing the moving target requires processes that can embrace change while also protecting existing functionality — through automated testing, disciplined change management, and short feedback cycles.

### 1.5.6 Limitations of Documentation-Driven Development

A natural response to the moving target problem is to write more comprehensive documentation upfront — detailed specifications that clients sign off on before development begins. This approach, common in Waterfall projects, has well-documented limitations.

**For clients:** Requirements documents are technical artefacts that many non-technical stakeholders cannot meaningfully evaluate. A client may sign off on a 200-page specification without truly understanding what system it describes — only to be disappointed when the software is delivered.

**For developers:** Written requirements are inevitably ambiguous. Natural language is imprecise. Two developers reading the same requirement will often build two different things.

**For the project:** Documentation becomes outdated as soon as implementation begins. A specification written at the start of an 18-month project rarely matches the reality of the system built at the end.

This does not mean documentation is bad — it means documentation alone is insufficient. This insight drove the Agile movement's preference for *working software* and *customer collaboration* over *comprehensive documentation*.

### 1.5.7 Rapid Prototyping

One way to address the limitations of documentation is **rapid prototyping** — building a quick, rough version of the system (or a key part of it) to get feedback before committing to full implementation.

A prototype is not a finished product. It is a communication and learning tool:

- **Throwaway prototypes** are built quickly, shown to stakeholders for feedback, and then discarded. The code is not production-quality; its purpose is to validate understanding.
- **Evolutionary prototypes** are built incrementally and progressively refined into the final system.

Rapid prototyping helps because users can react to something they can *see and use* far more effectively than to something they can only *read about*. It surfaces misunderstandings early — when they are cheap to correct — rather than late, when they are expensive.

### 1.5.8 Incremental Development

**Incremental development** is a strategy in which the system is built and delivered in functional pieces called *increments*, rather than all at once. Each increment is a working, usable subset of the final system.

```
Increment 1: Core functionality  ──▶  Delivered to users
Increment 2: Extended features   ──▶  Delivered to users
Increment 3: Full feature set    ──▶  Delivered to users
```

**Benefits:**
- Users get working software early and can provide meaningful feedback
- High-priority features are available sooner
- Risk is distributed: if an increment fails, only partial investment is lost
- Teams learn from early increments before building the more complex later ones

**Drawbacks:**
- System architecture can degrade if increments are not designed with the full picture in mind
- Contracts and project governance are harder when the full scope is not fixed upfront
- Integration between increments can be complex if interfaces were not anticipated

Incremental development is the conceptual foundation of Agile methods, but it can also be applied alongside a more structured, plan-driven approach.

### 1.5.9 Agile Software Development

Agile is not a single methodology but a family of approaches united by the values in the [Agile Manifesto](https://agilemanifesto.org/). The core insight is that software requirements and solutions evolve through collaboration — and that the ability to respond to change is more valuable than adherence to a plan.

Agile teams work in short cycles called *iterations* or *sprints*, typically 1–4 weeks long. Each iteration produces a working, tested increment of software. Stakeholders review the increment and provide feedback that informs the next iteration.

Key Agile principles include:

- Deliver working software frequently (weeks, not months)
- Welcome changing requirements, even late in development
- Business people and developers work together daily
- Simplicity — the art of maximising the amount of work *not* done — is essential

### 1.5.10 Scrum

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

```
┌─────────────────────────────────────────────────────────┐
│                    Product Backlog                       │
│  (ordered list of features, bugs, improvements)         │
└───────────────────────┬─────────────────────────────────┘
                        │ Sprint Planning
                        ▼
┌─────────────────────────────────────────────────────────┐
│                    Sprint (1–4 weeks)                    │
│                                                          │
│  Sprint Backlog → Daily Scrum → Working Increment        │
└───────────────────────┬─────────────────────────────────┘
                        │ Sprint Review + Retrospective
                        ▼
                  Next Sprint...
```

### 1.5.11 Kanban

Kanban, adapted from Toyota's manufacturing system by David Anderson ([Anderson, 2010](https://kanbanbooks.com/)), is a flow-based method that focuses on visualising work, limiting work in progress (WIP), and continuously improving flow.

A Kanban board visualises work as cards moving through columns:

```
┌──────────┬──────────────┬──────────────┬──────────┐
│ Backlog  │  In Progress │   In Review  │   Done   │
│          │   (WIP: 3)   │   (WIP: 2)   │          │
├──────────┼──────────────┼──────────────┼──────────┤
│ Task E   │ Task B       │ Task A       │ Task D   │
│ Task F   │ Task C       │              │          │
│ Task G   │              │              │          │
└──────────┴──────────────┴──────────────┴──────────┘
```

**Key Kanban practices:**
- **Visualise the workflow**: Make all work and its status visible
- **Limit WIP**: Prevent overloading; finish before starting more
- **Manage flow**: Track cycle time and throughput; identify bottlenecks
- **Improve collaboratively**: Use data to drive continuous improvement

Kanban suits teams with highly variable incoming work (e.g., support and maintenance teams) or those who want a lighter-weight alternative to Scrum's ceremonies.

### 1.5.12 Open Source Development

Open source development is a model in which source code is made publicly available and developed collaboratively by a distributed community of contributors. Anyone can inspect, use, modify, and distribute the software, subject to the terms of its licence.

The modern open source movement traces its roots to the GNU project (Richard Stallman, 1983) and gained enormous momentum with the creation of the Linux kernel by Linus Torvalds in 1991. Today, open source software powers much of the internet's infrastructure — from web servers (Apache, Nginx) to programming languages (Python, Ruby) to mobile operating systems (Android, which is built on the Linux kernel).

Key characteristics of open source development:

- **Community-driven**: Contributions come from individuals and organisations with diverse motivations — learning, reputation, commercial interest, and ideology
- **Distributed**: Contributors may be scattered across the world, working asynchronously
- **Transparent**: Code, issues, and discussions are publicly visible — anyone can review
- **Release early, release often**: Rapid iteration and public feedback replace formal specification

Open source raises interesting software engineering challenges: how do you maintain quality when anyone can contribute? How do you make architectural decisions by committee? These challenges have driven the development of code review workflows, continuous integration, and community governance models — many of which are now standard practice in commercial software development as well.

---

## 1.6 Key Takeaways

Software engineering is a young discipline that is still evolving — but it has accumulated hard-won wisdom from decades of successes and failures. The key ideas from this chapter:

1. **Software is not just code.** It is programs, data, and documentation — all of which must be engineered carefully.

2. **Software is different from other engineering products.** It is intangible, malleable, and knowledge-intensive. There are no universal theories, the field evolves rapidly, and strategies from civil engineering do not map cleanly onto software development.

3. **Good software has four essential attributes**: maintainability, dependability and security, efficiency, and acceptability. These must be balanced throughout development.

4. **People, Process, and Technology must work together.** No single tool or framework saves a project on its own. The human and organisational dimensions of software engineering are as important as the technical ones.

5. **Software engineering has a history worth knowing.** From the 1968 NATO conference to Margaret Hamilton's Apollo software to the Agile Manifesto, the field's practices are responses to real and costly problems.

6. **Failures are expensive and instructive.** The MYKI and CBA cases show that software failures carry serious financial, social, and regulatory consequences — and that they are preventable with disciplined engineering.

7. **Process choice matters.** Waterfall, Incremental, Agile, and Open Source each fit different contexts. Choosing the wrong model for a project is itself an engineering mistake.

8. **Change is inevitable.** Requirements move, technology evolves, and organisations change. Good software engineering practices — version control, testing, modular design, short iterations — are responses to this reality.