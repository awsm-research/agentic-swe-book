## 1.2 What Is Software Engineering?

Software engineering is the disciplined application of engineering principles to the design, development, testing, and maintenance of software systems. Unlike informal programming, software engineering emphasises process, quality, collaboration, and long-term maintainability.

The term was deliberately chosen. In 1968, NATO convened a conference in Garmisch, Germany, to address what organisers called the "software crisis" — a widespread recognition that software projects were routinely over budget, delivered late, and unreliable ([Naur & Randell, 1969](http://homepages.cs.ncl.ac.uk/brian.randell/NATO/nato1968.PDF)). The goal of using the word *engineering* was aspirational: to bring to software the same rigour, predictability, and professionalism that civil or mechanical engineers brought to bridges and engines.

That aspiration has guided the field ever since — and it remains relevant today, even as the tools, languages, and collaborators (including AI systems) have changed dramatically. Margaret Hamilton, who led the software team for NASA's Apollo programme in the 1960s, exemplified what this aspiration meant in practice: her team developed the discipline of rigorous, fault-tolerant software engineering at a time when a single defect could mean mission failure or loss of life.

![Attendees at the 1968 NATO Software Engineering Conference in Garmisch, Germany](../images/nato-conference-photo.png)
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

The distinction matters. A team fluent in algorithms but unfamiliar with software process will optimise a search function while missing the release deadline. A team fluent in process but ignorant of complexity theory will ship a feature that works on ten users and falls apart on ten thousand.

### The People–Process–Technology Model

Software engineering is often described using the **People–Process–Technology (PPT)** model — sometimes called the "golden triangle" of software development. This framework suggests that for any organisational change or project to be successful, there must be a harmonious balance between these three critical components.

![The People–Process–Technology Model](../images/chapter-1-ppt-model.png)

- **People**: The most vital corner of the triangle, representing the developers, architects, testers, product owners, and end-users. This pillar focuses on human capital — the skills, experience, and cultural mindset required to collaborate. While technology can amplify a team's capabilities, it cannot replace human judgement, creativity, or the nuanced communication needed to solve complex problems.

- **Process**: The "how" of the triangle. These are the structured activities and methodologies through which software is built — including requirements gathering, design, implementation, testing, deployment, and maintenance. A strong process ensures that work is repeatable, scalable, and predictable, preventing the chaos that occurs when individuals work in silos.

- **Technology**: The tools, programming languages, frameworks, and infrastructure used to build and support the system. Technology acts as the enabler — it provides the "machinery" to execute the processes. However, without the right people to operate it or the right processes to guide it, even the most advanced tech stack becomes a liability rather than an asset.

The triangle explains a pattern that recurs in troubled projects: a team adopts a new framework or automation tool hoping it will solve their delivery problems, only to find that the new technology demands a level of process discipline or technical skill they have not yet built.

In a healthy ecosystem, these three elements are interdependent. If you move one corner of the triangle without adjusting the others, the structure collapses. Technology choices are visible and exciting, making them easy to prioritise; however, it is the often-invisible failures in people and process that quietly undermine a project until the damage has already compounded.

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

> **The central question of software engineering is: How do we build high-quality software in a cost-effective way?**

Quality and speed are in tension. Security and simplicity conflict. New features compete with maintenance. Every decision in software development is a negotiation between competing goods — which is why process, judgement, and tooling all matter.

---
