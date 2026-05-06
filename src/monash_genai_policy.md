# Generative AI at Monash: Policy, Compliance, and Responsible Use

This page is written for students enrolled in **FIT5136** and **ITO5136** at Monash University. It explains Monash's Generative AI policy, clarifies how that policy applies to this book and its tutorials, and makes the case — directly and with evidence — that using this book responsibly is not only *permitted* under Monash's framework but is precisely the kind of AI engagement the University encourages.

---

## Monash University's Position on Generative AI

Monash University does not prohibit the use of Generative AI tools. It regulates how, when, and with what transparency they are used. The policy framework rests on three documents:

1. **Generative Artificial Intelligence in Assessment — Guidelines for Staff and Students** (Monash Learning and Teaching, 2023; updated 2024). Sets out the conditions under which AI tools may and may not be used in assessed work, and requires unit-level disclosure requirements to be stated in Assessment Task Descriptions. Source: [monash.edu/learning-teaching/teachhq/Teaching-practices/artificial-intelligence](https://www.monash.edu/learning-teaching/teachhq/Teaching-practices/artificial-intelligence)

2. **Assessment in Coursework Policy** (Monash Policy Bank, 2023). Defines academic integrity obligations and sets out that students are responsible for all submitted work, regardless of how it was produced. Source: [monash.edu/policy-bank/academic/education/assessment](https://www.monash.edu/policy-bank/academic/education/assessment)

3. **Student Academic Integrity Policy and Procedure** (Monash Policy Bank, 2021; amended 2024). Specifies that undisclosed use of AI in a way that misrepresents authorship constitutes a form of academic misconduct. Source: [monash.edu/policy-bank/academic/education/conduct](https://www.monash.edu/policy-bank/academic/education/conduct)

Together these documents establish four core principles:

| Principle | What It Requires |
|-----------|-----------------|
| **Transparency** | Disclose AI use where required by the assessment task |
| **Integrity** | You are responsible for all submitted work, AI-assisted or not |
| **Critical Evaluation** | You must interrogate AI outputs — not accept them uncritically |
| **Contextual Appropriateness** | AI use must match the learning purpose; not all tasks permit it |

---

## How This Book Approaches Generative AI

Before addressing compliance, it is worth being precise about what kind of AI engagement this book actually teaches. It does not teach students to use AI as a shortcut. It teaches a four-stage loop:

> **Specify → Generate → Verify → Refine**

Every chapter, every tutorial, and every milestone in the running project is structured around this loop. The human role is concentrated in *Specify* (decomposing problems with precision) and *Verify* (critically evaluating what the agent produced). The agent handles *Generate*. Nobody in this loop is passive.

That distinction matters for policy. A student who uses AI to generate code and submits it without review is not practising this loop — they have collapsed it. This book teaches the full loop, and the Verify step is treated throughout as the most intellectually demanding one.

---

## Compliance Argument — Chapter by Chapter

### Part I: SE Fundamentals (Chapters 1–5)

These chapters teach the foundational skills that make AI use responsible: requirements specification, system design, and testing. A student who understands Chapter 2 (*Requirements Engineering*) knows how to write a specification precise enough that an agent can act on it correctly — and precise enough that they can tell when it has not. A student who has worked through Chapter 4 (*Software Quality and Testing*) has the tools to verify agent-generated code against defined quality criteria.

**Policy relevance:** These chapters build the critical capacity that Monash's policy assumes students should bring to AI-assisted work. Without them, the Verify step is guesswork.

### Chapter 6: Agentic Software Engineering — A New Paradigm

This chapter introduces the Specify → Generate → Verify → Refine loop explicitly and argues that *verification* is the skill that separates responsible AI use from reckless reliance. It is the conceptual foundation for everything that follows.

**Policy relevance:** Directly teaches the critical evaluation principle. The chapter explicitly warns against accepting agent output at face value.

### Chapters 8–9: Security of AI-Generated Code; Security Concerns of Agentic AI Coding Tools

These two chapters are the most policy-aligned content in the book. Chapter 8 trains students to identify security vulnerabilities in code they did not write — including code an AI agent produced. Chapter 9 examines the security risks of the tools themselves: prompt injection, context poisoning, overprivileged agents. Students finish these chapters knowing not just how to use AI tools but what can go wrong when those tools are trusted without scrutiny.

**Policy relevance:** This is the critical evaluation principle applied to security. It is also ULO 6 for FIT5136 — ethical and security-aware practice — operationalised.

### Chapter 12: Licenses, Ethics, and Responsible AI

This chapter addresses the legal and ethical dimensions of AI-generated artefacts directly: software licences as they apply to AI-generated code, intellectual property concerns, bias and fairness in AI systems, and the professional obligations of engineers who deploy AI tools. Tutorial 12 puts these topics into practice.

**Policy relevance:** This chapter aligns with Monash's commitment to graduating ethically literate engineers. It is the book's most direct engagement with the *contextual appropriateness* principle — helping students understand when, legally and ethically, AI-generated code can and cannot be used.

### Preface: A Note to the Reader

The preface discloses that AI tools were used in writing parts of this book, describes how those tools were used, and states that every AI-assisted passage was reviewed, edited, and verified by the author before publication.

**Policy relevance:** This is the book modelling the exact behaviour it asks of students — transparency about AI use, authorial responsibility for all outputs. It is a deliberate pedagogical choice, not incidental disclosure.

---

## Your Obligations as a Student

Using this book and its tutorials does not automatically make your submitted work compliant with Monash policy. Your obligations depend on what each assessment task permits. Follow these principles:

### 1. Check the Assessment Task Description First

Every assessment task in FIT5136 and ITO5136 will specify one of the following:

- **AI use not permitted** — complete the task without AI assistance
- **AI use permitted with disclosure** — use AI tools and document how, submitting a brief AI Use Statement
- **AI use unrestricted** — AI tools are fully permitted; no disclosure required beyond what the task specifies

When in doubt, ask your unit coordinator before submitting.

### 2. You Are Responsible for Every Line You Submit

Monash policy is unambiguous: submitting AI-generated work as your own, without authorised disclosure, constitutes academic misconduct. This applies whether the AI generated one function or the entire project. The policy does not distinguish by quantity — it distinguishes by disclosure and intent.

### 3. Verify Before You Submit

Chapter 8 and the book's running project both require you to review and test AI-generated code. Apply that same standard to your assessments. If you cannot explain what a piece of submitted code does and why it is correct, you should not be submitting it.

### 4. Cite AI Tools Where Required

Where disclosure is required, use the format specified in your unit's Assessment Task Description. A typical AI Use Statement includes: which tool was used, for which part of the task, what the output was, and what changes you made to it.

---

## Why This Book Encourages Responsible Use — Not Shortcuts

There is a version of AI-assisted learning that the Monash policy is designed to prevent: students who outsource their thinking to AI, submit outputs they do not understand, and graduate without developing the judgment the degree is meant to produce. That version is an integrity violation and a disservice to the student.

This book is designed in deliberate opposition to that pattern. Consider:

- Every tutorial requires the student to specify the problem before invoking the agent. You cannot skip to Generate.
- Every milestone in the running project requires the student to verify what was produced — through tests, code review, or security analysis.
- Chapters 8 and 9 specifically train students to find the errors, biases, and vulnerabilities that AI tools introduce. Passing these chapters requires *distrusting* AI outputs in a disciplined way.
- Chapter 12 forces students to confront the legal and ethical limits of AI-generated artefacts.

A student who works through this book thoroughly is *less* likely to misuse AI tools in their career — not because the book tells them not to, but because it builds the verification instincts that make misuse visible.

---

## References

- Monash University. (2023, updated 2024). *Generative Artificial Intelligence in Assessment: Guidelines for Staff and Students*. Monash Learning and Teaching. [https://www.monash.edu/learning-teaching/teachhq/Teaching-practices/artificial-intelligence](https://www.monash.edu/learning-teaching/teachhq/Teaching-practices/artificial-intelligence)

- Monash University. (2023). *Assessment in Coursework Policy*. Monash Policy Bank. [https://www.monash.edu/policy-bank/academic/education/assessment](https://www.monash.edu/policy-bank/academic/education/assessment)

- Monash University. (2021, amended 2024). *Student Academic Integrity Policy and Procedure*. Monash Policy Bank. [https://www.monash.edu/policy-bank/academic/education/conduct](https://www.monash.edu/policy-bank/academic/education/conduct)

- UNESCO. (2023). *Guidance for Generative AI in Education and Research*. United Nations Educational, Scientific and Cultural Organization. [https://unesdoc.unesco.org/ark:/48223/pf0000386693](https://unesdoc.unesco.org/ark:/48223/pf0000386693)

- Tantithamthavorn, K. (2026). *Agentic Software Engineering: A Practical Guide for the AI-Native Engineer*. This book, Chapter 12: Licenses, Ethics, and Responsible AI.

- Tantithamthavorn, K. (2026). *Agentic Software Engineering: A Practical Guide for the AI-Native Engineer*. This book, Preface: A Note to the Reader.

---

*Questions about this page or its policy interpretations should be directed to [chakkrit@monash.edu](mailto:chakkrit@monash.edu). For unit-specific assessment guidance, contact your unit coordinator.*
