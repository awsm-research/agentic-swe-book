## 1.4 The Software Development Lifecycle (SDLC)

The Software Development Lifecycle (SDLC) is a structured process for planning, creating, testing, and deploying software.

### 1.4.1 Core Activities

While specific SDLC models differ in their structure and emphasis, most share a common set of core activities:

| Activity | Description |
|---|---|
| **Requirements** | Understand what the system should do — from the perspective of users, stakeholders, and regulators |
| **Design and Implementation** | Decide how the system will be structured, then write and integrate the code |
| **Verification and Validation** | *Verification*: Are we building the system right? (testing, reviews) *Validation*: Are we building the right system? (stakeholder review) |
| **Maintenance** | Fix bugs, adapt to new environments, and extend functionality after deployment |

A key insight from decades of software engineering research is that **maintenance dominates cost**. Studies consistently show that 60–80% of total software cost is incurred after initial deployment (Sommerville, 2016). This has profound implications: the decisions made during requirements and design — naming conventions, modularity, documentation — echo through the entire lifetime of a system.

### 1.4.2 The Cost of Change

Another well-established finding is that **the cost of fixing a defect rises dramatically the later it is found**. A requirement error caught in a design review costs relatively little. The same error discovered after deployment may require changes to a live system, database migrations, user retraining, and regulatory notification.

![Cost to Fix Bugs Over Time](../images/chapter-1-cost-to-fix-bugs.png)

This cost curve is the economic argument for investing in requirements, design, and testing — and for short feedback cycles. The sooner a problem is discovered, the cheaper it is to fix.

From an economic perspective, software and hardware have also swapped their relative costs. In the early days of computing, hardware was the dominant expense. Today, software development and maintenance far exceed hardware costs in most systems — which is why software engineering as a discipline commands serious investment.

### 1.4.3 SDLC Models Overview

No single development process fits every project. The right choice depends on how well requirements are understood upfront, how stable they are likely to remain, team size, risk tolerance, and regulatory context.

| Model | Approach | Best For |
|---|---|---|
| **Plan-driven (Waterfall)** | Sequential phases; each complete before the next | Stable, well-understood requirements |
| **Incremental** | Deliver in functional slices | Partial requirements; early delivery needed |
| **Agile** | Iterative; embrace change | Evolving requirements; fast feedback |
| **Open Source** | Community-driven; distributed contributions | Widely used tools and libraries |

### 1.4.4 Waterfall

The Waterfall model, introduced by Winston Royce in 1970 (though Royce actually presented it as a flawed approach in the same paper ([Royce, 1970](http://www-scf.usc.edu/~csci201/lectures/Lecture11/royce1970.pdf))), organises development as a strict sequence of phases. Each phase must be completed before the next begins. The model assumes requirements can be fully and correctly specified at the start.

![A Waterfall Software Development Process.](../images/waterfall.png)

**Strengths:**
- Clear milestones and deliverables
- Easy to manage and document
- Works well for projects with stable, well-understood requirements (e.g., certain embedded systems, regulated government contracts)

**Weaknesses:**
- Requirements almost never remain stable
- Errors discovered late are expensive to fix
- Users see no working software until the end
- Poor fit for projects with high uncertainty

### 1.4.5 Incremental Development

Incremental development addresses Waterfall's most critical weakness: users see nothing working until the project is complete. Instead of delivering the entire system at once, the team divides the system into a series of **increments** — functional slices that can be designed, built, and delivered independently.

Each increment adds value. Early increments cover the core functionality; later increments add secondary features. Stakeholders can use and evaluate each increment and provide feedback that shapes subsequent ones.

**Strengths:**
- Users see working software early and can redirect development based on real experience
- Core functionality can be used while secondary features are still being built
- Risk is reduced — if the project is cancelled or budget is cut, at least a working subset has been delivered

**Weaknesses:**
- Requires careful planning to partition the system into coherent, deliverable slices
- The overall architecture must accommodate future increments without requiring major rework
- Harder to manage fixed-price contracts when the full scope is not defined upfront

Incremental development is the conceptual foundation of Agile methods, but it can also be applied alongside a more structured, plan-driven approach.

### 1.4.6 The Moving Target Problem

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

### 1.4.7 Limitations of Documentation-Driven Development

A natural response to the moving target problem is to write more comprehensive documentation upfront — detailed specifications that clients sign off on before development begins. This approach, common in Waterfall projects, has well-documented limitations.

**For clients:** Requirements documents are technical artefacts that many non-technical stakeholders cannot meaningfully evaluate. A client may sign off on a 200-page specification without truly understanding what system it describes — only to be disappointed when the software is delivered.

**For developers:** Written requirements are inevitably ambiguous. Natural language is imprecise. Two developers reading the same requirement will often build two different things.

**For the project:** Documentation becomes outdated as soon as implementation begins. A specification written at the start of an 18-month project rarely matches the reality of the system built at the end.

This does not mean documentation is bad — it means documentation alone is insufficient. This insight drove the Agile movement's preference for *working software* and *customer collaboration* over *comprehensive documentation*.

---
