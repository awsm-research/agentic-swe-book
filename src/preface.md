<div style="display:flex; justify-content:center; padding: 2rem 0;">
  <img src="cover.svg" alt="Book cover — AI-Native Engineer" style="max-width:480px; width:100%; border-radius:6px; box-shadow: 0 8px 32px rgba(0,0,0,0.4);" />
</div>

# Preface

## About This Book

This book is about a fundamental shift in what software engineers actually do.

For most of the history of the profession, the primary bottleneck in software development was *writing code*: turning a clear understanding of the problem into a working implementation. Tools, languages, and frameworks were all designed to help engineers write code faster, more reliably, and with fewer defects. Being a great engineer meant, in large part, being a great coder.

That bottleneck is moving — fast.

AI agents can now write syntactically correct, contextually relevant code from a natural language description. They can scaffold entire systems, generate test suites, refactor legacy code, and explain unfamiliar codebases in seconds. The implementation layer — once the core of the engineer's craft — is increasingly automated.

What remains irreducibly human is everything that surrounds implementation: **understanding the problem, specifying intent precisely, verifying what was produced, and refining it until it is right.**

This is the new loop of software engineering in the agentic era:

<div align="center">
  <img src="images/banner.png" alt="Agentic Software Engineering: A Practical Guide for the AI-Native Engineer" />
</div>

**Specify** — Define the problem with precision. Decompose ambiguous requirements into clear, agent-sized tasks. Write specifications that leave no room for misinterpretation.

**Generate** — Delegate to AI agents with confidence. Provide the right context, constraints, and success criteria. Let agents handle the implementation.

**Verify** — Review outputs critically and systematically. Test assumptions. Catch hallucinations, edge cases, and silent failures before they reach production.

**Refine** — Iterate. Improve your specifications, your prompts, your verification strategies. Each cycle makes the next one faster and more accurate.

This loop replaces the old SDLC — not by discarding its principles, but by redistributing where human intelligence is most needed. The engineer moves up the abstraction stack: from implementer to architect, from coder to critic, from builder to director.

This book teaches that move. It is not a book about which AI tools to use or how to write clever prompts. It is a book about the new skills that matter when coding is automated: problem decomposition, system thinking, critical verification, and judgment under uncertainty. Skills that compound. Skills that do not expire when the next model is released.





---

## Why This Book

Software engineering education has not kept pace with the shift it is supposed to prepare students for.

Most curricula still centre on coding: write the function, pass the tests, ship the feature. That focus made sense when writing code was the hard part. It makes less sense when an AI agent can produce a working implementation in seconds from a plain-language description (or vibe coding).

What current education largely overlooks is everything *around* the code — the skills that determine whether what gets generated is actually the right thing, built correctly, for the right reasons. How to decompose a vague problem into a specification an agent can act on. How to evaluate generated output with the same rigour you would apply to code you wrote yourself. How to know when to trust the agent and when to override it. These are teachable skills, and they are not yet being taught systematically.

This book is an attempt to close that gap. It emerged from teaching software engineering at the graduate level and watching students who were technically capable nonetheless struggle when AI entered their workflow — not because the tools were too hard to use, but because the underlying engineering judgment had not been developed. They could prompt. They could not yet verify.

The book is the primary learning material for two courses at Monash University: **FIT5136**, a twelve-week on-campus unit within the Master of Information Technology, and **ITO5136**, a six-week online unit within the Master of Computer Science. Both courses target students who arrive with programming foundations but limited exposure to the full software engineering lifecycle — and zero reason to assume that lifecycle looks the same as it did five years ago.

The goal is not to produce students who are good at using today's AI tools. It is to produce engineers who understand *why* the new loop works, so that when the tools change — and they will — the underlying mental model transfers.

---

## On Prior Work and How This Book Differs

The term *agentic software engineering* is not mine, and I do not claim to have coined it. It has been used and developed by several researchers and practitioners ahead of this book, and any reader familiar with the literature will recognise the lineage. I want to acknowledge that work directly, and then be honest about where this book sits in relation to it.

In popular discourse, the broader idea is most commonly credited to **Andrej Karpathy** (OpenAI cofounder and former Tesla AI lead), who from around February 2025 onward articulated a vision in which AI coding tools autonomously plan, write, test, and iterate on software under human oversight, rather than developers writing every line themselves. That framing — humans setting intent and reviewing outcomes while agents do the implementation — is the cultural starting point for much of what followed.

The academic and industry community has since developed the idea into a more concrete research and engineering agenda. The most directly relevant prior works are:

- **Hassan (2025), *Agentic Software Engineering: The Future of Code*** — a book-length treatment focused on architectural thinking, intent, and risk management in AI-assisted teams. [agenticse-book.github.io](https://agenticse-book.github.io/).
- **Takerngsaksiri, Pasuksmit, Thongtanunam, Tantithamthavorn et al. (2025), *Human-In-the-Loop Software Development Agents (HULA)*** — introduces a framework that integrates human oversight into LLM-based software development agents, deployed and evaluated with real engineers inside Atlassian JIRA; an early industrial case study of Agentic Software Engineering in practice. [arXiv:2411.12924](https://arxiv.org/abs/2411.12924).
- **Roychoudhury, Pasareanu, Pradel, and Ray (February 2025), *Agentic AI Software Engineers: Programming with Trust* (Communications of the ACM, 2026)** — reframes the central question of agentic SE from speed to trust, arguing that coupling LLMs with program analysis is the path to deployable AI engineers. [arXiv:2502.13767](https://arxiv.org/abs/2502.13767).
- **Li, Zhang, and Hassan (July 2025), *The Rise of AI Teammates in Software Engineering (SE 3.0)*** — provides large-scale empirical evidence (the AIDev dataset) of how autonomous coding agents actually behave on real repositories, surfacing a measurable trust-and-utility gap. [arXiv:2507.15003](https://arxiv.org/abs/2507.15003).
- **Roychoudhury (2025), *Agentic AI for Software: thoughts from the Software Engineering community*** — positions agents as autonomous team members across both code-level and design-level tasks, with specification inference as the core unsolved problem. [arXiv:2508.17343](https://arxiv.org/abs/2508.17343).
- **Rajbahadur, Hassan, and Izadi (2025), *AIware Bootcamp*** — a community bootcamp on engineering AI-powered software and the transition from passive copilots to autonomous AI teammates ("Agentware"), shaped by leaders from Google, GitHub, Microsoft, Carnegie Mellon, and others. [aiwarebootcamp.io](https://www.aiwarebootcamp.io/).
- **Charoenwet, Tantithamthavorn, Thongtanunam, Lin, Jeong, and Wu (2026), *AgenticSCR: An Autonomous Agentic Secure Code Review for Immature Vulnerabilities Detection*** — applies the agentic paradigm to a concrete SE task, combining LLMs with autonomous tool use, code navigation, and security-focused semantic memory to detect pre-commit vulnerabilities; an example of agentic SE realised end-to-end on a single, well-scoped problem. [arXiv:2601.19138](https://arxiv.org/abs/2601.19138).
- **Hoda (2026), *Toward Agentic Software Engineering Beyond Code: Framing Vision, Values, and Vocabulary*** — argues for a "whole of process" view of agentic SE and proposes shared values and vocabulary for the field. [arXiv:2510.19692](https://arxiv.org/abs/2510.19692).

These works define the research and conceptual frontier of the field. They ask: *What is agentic SE? What should it mean? How do we measure trust? What vocabulary should we share? What does the process look like at the level of the whole organisation?* They are written primarily for the software engineering research community and for senior practitioners shaping team strategy.

This book is a different artefact, with a different audience and a different goal.

It is a **course textbook**, not a research vision. It is written for students and early-career engineers who need to learn how to *do* agentic software engineering this semester — not to debate its boundaries, but to develop working competence in it. Where the prior works above describe the destination and the open problems, this book is concerned with the day-to-day practice required to operate inside the new loop: how to write a specification an agent can act on, how to verify what comes back, how to recognise when to override the agent, and how to do all of this on a realistic, growing system.

Concretely, this book differs from the prior literature in four ways:

1. **Pedagogical first.** Each chapter has learning objectives, a worked example, exercises, and a milestone in a running project. It is designed to be taught, not only read.
2. **A single explicit loop.** The book is organised around one loop — *Specify → Generate → Verify → Refine* — applied repeatedly across the full lifecycle, so that students leave with a transferable mental model rather than a catalogue of techniques.
3. **Practice-facing, not research-facing.** The emphasis is on judgment under uncertainty, verification habits, and engineering responsibility, rather than on defining or measuring the field.
4. **A running project.** A Task Management API grows from a scope statement to a deployed, audited system across twelve chapters, so every concept is anchored to code the reader has actually written and shipped.

In short: the prior works ask what agentic software engineering *is*. This book is an attempt to teach someone how to *practise* it well enough to be useful on Monday morning. Both are needed, and this one is built on the shoulders of the other.

---

## Who This Book Is For

**Primary readers:**
- Software engineers transitioning from traditional to AI-assisted workflows who want sustainable, tool-independent skills
- Advanced undergraduate and graduate students in software engineering
- Senior developers and tech leads adapting team practices

**Secondary readers:**
- Engineering managers redefining development processes
- Researchers in software engineering

**What you need to bring:**
- Comfort with at least one programming language (examples are in Python)
- Familiarity with basic programming concepts: functions, classes, loops, conditionals
- Some exposure to version control (git) and the command line

**What you do not need:**
- Prior experience with AI coding tools
- A background in machine learning or deep learning
- Advanced knowledge of Python — the examples use standard library features and widely-adopted packages

---

<!-- ## How to Use This Book

This book is written for a 12-week university course at Monash University, but it is structured so that it can be used in several ways.

### Path A: 12-Week Course (Recommended)

Follow the chapters in order, one per week. Each chapter builds on the previous and contributes one milestone to the running course project — a Task Management API that grows from a scope statement (Week 1) to a complete AI-native system (Week 12).

```
Weeks 1–5:  SE Fundamentals (Chapters 1–5)
Weeks 6–9:  Agentic Software Engineering (Chapters 6–9)
Weeks 10–12: Engineering with Responsibility (Chapters 10–12)
```

The project milestones at the end of each chapter are the primary assessment vehicle. Submit them on a weekly cadence and use peer review to compare approaches.

### Path B: Practitioner Self-Study

If you are an experienced engineer who wants to develop AI-native skills specifically, start with Chapter 6 (Agentic Software Engineering: A New Paradigm) to calibrate where you are, then read Chapters 7–9 in order. Use Chapters 1–5 as reference when the foundations feel shaky, and Chapters 10–12 for the governance and strategy dimensions.

Recommended reading order: 6 → 7 → 8 → 9 → 10 → 1–5 (reference) → 11 → 12

### Path C: Team Reference

If your team is adopting AI tools and you want to use this as a shared reference, the most immediately useful chapters are:

| Need | Chapter |
|---|---|
| Automated code review, quality, and CI/CD | 5 |
| Adopting an agentic engineering paradigm | 6 |
| Configuring agents with context, skills, and tools | 7 |
| Security of AI-generated code | 8 |
| Security concerns of agentic AI coding tools | 9 |
| Software maintenance and technical debt | 10 |
| Software packaging, versioning, and deployment | 11 |
| Licences, ethics, and responsible AI | 12 |

--- -->

## A Note to the Reader

I want to be transparent about how this book was made, because I know readers have a range of views on the role of AI in writing — and those concerns deserve a direct answer rather than a polished one.

The intellectual content of this book is mine. I designed the structure, defined the chapter outlines, chose the arguments, selected the examples, and decided what belonged on the page and what did not. The perspective, the framing, and the engineering judgment throughout are the product of my own research and experience as the author.

For some chapters, I used AI tools to assist with the writing process — drafting passages from my outlines, suggesting wording, and helping render a small number of conceptual diagrams. In every case, the output was reviewed, edited, fact-checked, and rewritten as needed by me before it became part of the manuscript. Nothing was published unread. Nothing was accepted on faith. The author remains fully responsible for every claim, every conclusion, and every line of code.

I chose to disclose this rather than leave it unsaid. A book about software engineering alongside AI should be honest about its own process — and readers should be able to judge the work knowing exactly how it was made.

## Disclaimers

All code examples in this book use Python. This choice is deliberate and transparent, not an endorsement.

**This is not a sponsored book.** No commercial relationship exists between the author or any other AI provider mentioned.

**This book does not represent the views of Monash University.** It is written in a personal capacity and is not endorsed by, affiliated with, or produced on behalf of Monash University or any other institution. Readers are responsible for applying the concepts and techniques described here thoughtfully and at their own discretion. The author accepts no liability for decisions or outcomes arising from the use of this material.

<!-- **These principles apply to any LLM provider.** Every concept in this book — the AI-native SDLC, specification design, evaluation-driven development, agentic orchestration — applies equally to OpenAI GPT models, Google Gemini, Meta Llama, Mistral, and future models not yet released. The Anthropic API is the *implementation vehicle*, not the *subject*. Where examples use Anthropic-specific classes (`anthropic.Anthropic()`, `client.messages.create()`), the equivalent calls for other providers are:

| Concept | Anthropic (this book) | OpenAI equivalent | Generic pattern |
|---|---|---|---|
| Client init | `anthropic.Anthropic()` | `openai.OpenAI()` | Provider client |
| Completion | `client.messages.create(model=..., messages=[...])` | `client.chat.completions.create(model=..., messages=[...])` | Call with model + messages |
| System prompt | `system="..."` parameter | `{"role": "system", "content": "..."}` in messages | First message or system param |
| Tool definition | `tools=[{name, description, input_schema}]` | `tools=[{type, function: {name, description, parameters}}]` | JSON schema per tool |

See [Appendix C](./appendix_c.md) for provider-agnostic wrappers and guidance on applying these examples to other languages.

**Models change.** The specific model IDs used in examples (`claude-opus-4-7`, `claude-haiku-4-5-20251001`) are current as of writing. New model versions are released regularly. Always check [https://docs.anthropic.com/en/docs/about-claude/models](https://docs.anthropic.com/en/docs/about-claude/models) for the current model list. The principles in this book are model-version-independent; only the model ID strings need updating.

---

## The Running Project

Starting in Chapter 1, you will build a **Task Management API** — a backend system for software development teams to create projects, manage tasks, assign work, and track progress. This is a deliberately familiar problem domain. The focus is not on inventing a novel application but on applying AI-native engineering practices to a realistic, growing system.

By the end of Chapter 12, you will have:
- A requirements specification and design document
- A Python REST API with full test coverage
- A CI/CD pipeline with automated quality gates
- AI-generated features developed using the Specify → Generate → Verify → Refine cycle
- An agentic workflow that automates a development task
- Security review, licence audit, and responsible AI assessment

The project is intentionally modest in scope so that the *process* — not the product — can be the focus of each week.

---

## Companion Resources

All code examples are available at: [github.com/awsm-research/agentic-swe-book](https://github.com/awsm-research/agentic-swe-book)

For updates on regulatory changes (EU AI Act, etc.) and new tool guidance, check the repository's `UPDATES.md` file. The landscape changes faster than print allows. -->

---

## Contributions and Feedback

This book is a living document. Errors, outdated examples, and gaps in explanation are inevitable — and fixable.

The source is open and maintained at [github.com/awsm-research/agentic-swe-book](https://github.com/awsm-research/agentic-swe-book). There are three ways to engage:

- **Questions and discussion** — use [GitHub Discussions](https://github.com/awsm-research/agentic-swe-book/discussions) for questions about the material, chapter reactions, and conversations with other readers. This is the right place for anything that is not a concrete error.
- **Errors and corrections** — open a GitHub Issue with the chapter reference and a brief description of the problem. Reserve issues for specific, actionable mistakes: wrong code, broken links, factual errors.
- **Direct contributions** — submit a pull request with a clear description of the change and why it helps readers. Examples, exercises, and case studies are especially welcome.

If you prefer not to use GitHub, please email chakkrit@monash.edu.

All contributions are credited. No contribution is too small.

---

*Associate Professor Kla Tantithamthavorn,*
*Monash University, Australia*
*2026*
