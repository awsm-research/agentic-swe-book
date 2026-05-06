# Chapter 6: Agentic Software Engineering: A New Paradigm

> *"The programming barrier is incredibly low. We have closed the digital divide. Everyone is a programmer now — you just have to say something to the computer."*
> — Jensen Huang, Computex Keynote, Taipei (2023)

---

In May 2023, NVIDIA chief executive Jensen Huang told an audience at Computex in Taipei: "The programming barrier is incredibly low. We have closed the digital divide. Everyone is a programmer now — you just have to say something to the computer." Nearly two years later, Andrej Karpathy — co-founder of OpenAI and former director of AI at Tesla — gave that vision a name. In a post on 6 February 2025, he coined the term *vibe coding* to describe a practice that had become widespread: "you fully give in to the vibes, embrace exponentials, and forget that the code even exists." He described accepting every AI-generated change without reading it, copying error messages straight back to the model, and watching "the code grow beyond my usual comprehension." He was honest that this approach was suited to throwaway weekend projects. A Monash University study by Liu et al. had already measured what happened when it was not: 32.2% of ChatGPT-generated code samples produced incorrect outputs, and nearly half had maintainability issues that standard static analysis could detect — failures an engineer who never read the diff would ship without knowing ([Liu et al., 2023](https://arxiv.org/abs/2307.12596)).

---

## Learning Objectives

By the end of this chapter, you will be able to:

1. Distinguish between a large language model and an AI coding agent, and explain why the distinction matters for engineering practice.
2. Identify the four core components of an AI coding agent: tools, skills, connectors, and memory.
3. Compare terminal-based AI coding agents (Claude Code, Gemini CLI) with AI-native IDEs (Cursor, Windsurf) and explain the appropriate use of each.
4. Describe the Agentic SDLC — Spec, Generate, Verify, Refine — and explain what the engineer's primary responsibilities are at each phase.
5. Identify common patterns and anti-patterns in agentic software engineering workflows.
6. Evaluate the risks of AI teammate workflows — including overreliance, accountability gaps, and intellectual property concerns — and explain why human engineers retain responsibility for AI-generated work.

---

## 6.1 What Is Agentic Software Engineering?

*Agentic software engineering* is the practice of directing AI coding agents — autonomous systems that can plan, execute, and verify multi-step development tasks — as a central mode of producing and maintaining software. It is not a tool category or a product feature. It is a change in how the work of software engineering is organised.

The distinction from earlier forms of AI-assisted development is one of degree that becomes a difference in kind. A developer using GitHub Copilot still makes every decision: they read the suggestion, accept or reject it, move to the next line. The AI accelerates keystrokes. The developer's workflow is otherwise unchanged. An agentic workflow is different: the developer writes a specification, delegates the implementation to an agent that reads files, runs tests, and iterates autonomously, and then reviews the result. The bottleneck has moved from *writing* to *specifying and verifying*.

This shift has been underway since at least 2024, when tools like Devin ([Cognition, 2024](https://cognition.ai/blog/introducing-devin)), Claude Code (Anthropic, 2024), and Cursor demonstrated that an LLM with access to a shell and a file system could resolve real-world software issues with meaningful autonomy. SWE-bench — a benchmark of GitHub issues drawn from popular Python projects — provided a standardised measure: the fraction of issues an agent could fix without human intervention. Early scores in 2024 were below 20%. By mid-2025, leading agents exceeded 50% ([SWE-bench Leaderboard, 2025](https://www.swebench.com/)). The capability curve is steep.

*Agentic software engineering*, properly understood, is the discipline of working with these agents in a way that captures the productivity gains while enforcing the engineering standards that prevent the gaps from being amplified.

---

## 6.2 What Is an AI Coding Agent?

The term *AI coding agent* is used loosely in the industry to mean anything from a code-completion plugin to a fully autonomous system that opens pull requests without human instruction. A useful definition must be more precise.

An *AI coding agent* is a system in which a large language model is connected to a set of tools that allow it to take actions in the development environment — reading and writing files, executing commands, browsing documentation, calling APIs — in pursuit of a multi-step goal, with the ability to observe the results of its actions and adapt its plan accordingly ([Russell & Norvig, 2020](https://aima.cs.berkeley.edu/)).

The critical phrase is *multi-step goal with adaptation*. A chatbot answers a question. An AI coding agent implements a feature — reading the codebase to understand the context, writing code, running the tests, reading the test output, fixing failures, and producing a pull request. It does not wait for the engineer to mediate between each step.

### 6.2.1 LLMs vs. Agentic AI

Understanding the difference between a *large language model* and an *AI coding agent* is not just a technical distinction — it determines what the tool can and cannot be asked to do.

A *large language model* (LLM) is a neural network trained on text that predicts the most likely continuation of a given input. It takes text in and produces text out. It has no persistent state between calls, cannot take actions in the world, and does not know whether what it produced was actually run. Every response is stateless.

An *AI coding agent* wraps an LLM with infrastructure that gives it state and agency:

| Capability | LLM alone | AI coding agent |
|---|---|---|
| **Generate code** | Yes | Yes |
| **Read files from disk** | No | Yes |
| **Execute shell commands** | No | Yes |
| **Run tests and read results** | No | Yes |
| **Maintain state across steps** | No | Yes |
| **Adapt plan based on results** | No | Yes |
| **Take irreversible actions** | No | Yes |

The last row matters most for engineering practice. An LLM cannot delete a file or push a commit. An agent can. This is why the judgment and verification skills covered throughout this book become *more* important in agentic workflows, not less — the agent's mistakes have real consequences.

### 6.2.2 AI Coding Agents in the Terminal

The first category of AI coding agent operates directly in the terminal, treating the file system and shell as its primary environment. Two widely used examples are *Claude Code* (Anthropic, 2024) and *Gemini CLI* (Google, 2024).

*Claude Code* is a command-line interface that runs in the engineer's terminal. The engineer describes a task in natural language; Claude Code reads the relevant files, writes code, runs tests, and iterates — all within the existing project structure, using the existing toolchain, without opening a browser or an IDE. It is designed to be invisible to the project: it adds no dependencies, requires no plugins, and leaves the engineer's workflow otherwise unchanged.

*Gemini CLI* provides similar terminal-based agentic capabilities backed by Google's Gemini model family. Both tools share a design philosophy: bring the AI to the engineer's environment, rather than requiring the engineer to move to an AI-specific environment.

Terminal agents suit engineers who prefer full control over their toolchain, work on complex or unfamiliar codebases where reading source is the primary activity, or operate in environments (remote servers, CI pipelines) where a graphical IDE is unavailable.

### 6.2.3 AI-Native IDEs

The second category integrates agentic AI directly into the editing experience. *Cursor* and *Windsurf* are the most widely adopted examples as of 2025.

*Cursor* is a fork of Visual Studio Code with AI capabilities built into the editor at a fundamental level — not as a plugin but as a first-class part of the interface. The agent can see the entire codebase, understand the editor's open files, run commands in the integrated terminal, and apply changes directly to open files. Engineers interact via a chat panel that sits alongside the editor.

*Windsurf* (Codeium, 2024) takes a similar approach with an additional emphasis on *flow* — the agent proactively observes what the engineer is doing and offers suggestions without being explicitly prompted, analogous to a pair programmer who notices when you are stuck.

AI-native IDEs suit engineers doing sustained feature work in a single codebase, working on tasks where visual context (seeing the code alongside the AI conversation) speeds up verification, or transitioning to agentic workflows from an IDE-centric background.

For engineers new to agentic workflows, an AI-native IDE is the lower-friction starting point — the visual context alongside the conversation speeds up verification. Terminal agents earn their place when shell flexibility, composability, or remote access matters more than IDE integration. Many engineers use both, choosing by task.

---

## 6.3 Inside the Agent: Components of an AI Coding Agent

Regardless of whether the agent runs in a terminal or an IDE, its architecture consists of four components: tools, skills, connectors, and memory. Understanding these components allows you to reason about what the agent can and cannot do, and where it is likely to fail.

### 6.3.1 Tools

*Tools* are the primitive actions an agent can take in the world — atomic, executable operations with defined inputs and outputs. They are the agent's hands.

Common tools available to coding agents:

| Tool | Description |
|---|---|
| **read_file** | Read the contents of a file at a given path |
| **write_file** | Write or overwrite a file at a given path |
| **run_command** | Execute a shell command and return stdout/stderr |
| **search_code** | Search the codebase for a pattern or symbol |
| **fetch_url** | Retrieve the contents of a URL |
| **create_branch** | Create a new git branch |
| **submit_pr** | Open a pull request with a given diff and description |

Tools are powerful because they allow the agent to *observe* the results of its actions and adapt. After calling `run_command("pytest")`, the agent reads the test output, identifies failures, and updates its plan accordingly. This observe-adapt loop — formalised by Yao et al. as the *ReAct* pattern — is what distinguishes an agent from a stateless text predictor ([Yao et al., 2022](https://arxiv.org/abs/2210.03629)).

Tools are also the primary source of risk. A `write_file` call on a production configuration file, a `run_command` that drops a database table, a `submit_pr` that opens a request to the wrong repository — these are irreversible actions that the engineer must prevent through careful permissions, sandboxing, and oversight postures.

### 6.3.2 Skills

*Skills* are reusable, higher-order capabilities composed from multiple tool calls — the agent's learned repertoire. Where a tool answers "what can the agent do in one step?", a skill answers "what can the agent accomplish as a unit of work?"

Examples of skills:

- **code-review**: Read a diff, check it against a checklist, return a structured review
- **write-tests**: Given a function signature and docstring, generate a suite of unit tests
- **security-scan**: Traverse a codebase looking for OWASP Top 10 vulnerabilities
- **refactor-rename**: Rename a symbol consistently across all files

Skills are typically defined as reusable prompts or prompt templates stored alongside the project. Claude Code calls these *slash commands* (e.g., `/review`, `/test`). They allow teams to encode their engineering standards into the agent — "when we do a security review, we always check these ten things" — rather than relying on the engineer to prompt correctly every time.

### 6.3.3 Connectors

*Connectors* are integrations that give the agent access to external systems beyond the file system — databases, issue trackers, CI pipelines, documentation repositories, and APIs.

The *Model Context Protocol* (MCP), published by Anthropic in 2024, is a standardised protocol for connecting agents to external tools and data sources. Before MCP, every team building an agentic system had to write bespoke integration code for each external system. MCP defines a common interface — a server exposes resources and tools; the agent connects to the server; the agent can now use those resources and tools as if they were built-in.

```
Agent ←→ MCP Client ←→ MCP Server ←→ External System
                              (GitHub, Jira, PostgreSQL, Confluence)
```

The practical consequence is that an agent connected to a GitHub MCP server can read issues, create branches, and open pull requests using the same mechanism it uses to read files. The engineer configures the connection once; the agent handles the rest.

### 6.3.4 Memory

*Memory* determines what information persists across steps, sessions, and agents. It is the most architecturally subtle of the four components. Surveys of LLM-based agent architectures identify four distinct memory types ([Wang et al., 2024](https://arxiv.org/abs/2308.11432)):

| Memory type | Scope | Persistence | Example |
|---|---|---|---|
| **In-context** | Single session | Until session ends | Current conversation, open files |
| **External** | Across sessions | Indefinite | A `CLAUDE.md` file, a vector database |
| **Episodic** | Across tasks | Configurable | Summaries of past tasks the agent has performed |
| **Semantic** | Across agents | Configurable | Shared facts about the codebase or team conventions |

In-context memory is cheapest and most immediate but limited by the model's context window (typically 200,000 tokens for current Claude models). External memory persists to files or databases and survives session restarts. Episodic and semantic memory allow multi-agent systems to share knowledge.

The practical implication for engineering teams: place the information the agent most needs to get work right in *external memory*. A well-maintained `CLAUDE.md` file at the project root — describing architecture decisions, coding conventions, test structure, and known constraints — dramatically improves agent output quality. It is, in effect, the onboarding document the agent reads before starting every task.

---

## 6.4 AI as the New Teammate

Hassan's central argument is that the correct mental model for AI coding tools is not *tool* but *teammate* — a collaborator with specific capabilities, blind spots, and tendencies that an effective engineer must learn to work with ([Hassan, 2025](https://agenticse-book.github.io/pdf/AgenticSE_Book.pdf)).

The tool metaphor leads engineers to treat AI as passive: you invoke it, it does a thing, you evaluate the output. The teammate metaphor leads engineers to think about communication, context, delegation, and feedback loops. A good teammate is not one who executes instructions blindly; it is one who understands the goal, flags when the instructions conflict with the goal, and asks for clarification before going wrong.

**Context matters as much as instructions.** Compare two ways to kick off the same task:

> *"Add input validation to the user registration endpoint."*

> *"Add input validation to the `/api/register` endpoint in `auth/views.py`. The project uses Pydantic v2 for validation — see `schemas/user.py` for existing patterns. Reject emails that are not RFC 5322 compliant, passwords under 12 characters, and usernames containing special characters other than hyphens and underscores. Do not touch the rate-limiting middleware in `auth/middleware.py`. Tests live in `tests/test_auth.py`."*

The first prompt produces code that validates *something*. The second produces code that validates *exactly what you need*. The difference is not in the model — it is in the brief. Effective AI-native engineers invest in context files (`CLAUDE.md`, `.cursorrules`) that provide this background automatically before every task.

**Feedback is iterative.** You would not expect a teammate to get a complex task right on the first attempt. The Spec → Generate → Verify → Refine loop (see Section 6.5) is the professional workflow for collaborating with an AI teammate — not a workaround for the AI's limitations, but the natural structure of iterative collaborative work.

**Strengths and blind spots are learnable.** AI coding agents are reliably strong at: boilerplate generation, test scaffolding, translating between languages, finding related code, explaining unfamiliar codebases, and writing documentation. They are reliably weak at: multi-file refactors without explicit context, maintaining invariants across a long session, security reasoning without explicit prompting, and understanding implicit organisational conventions. Knowing the map of strengths and weaknesses allows you to delegate effectively and verify precisely where it matters.

**Responsibility does not transfer.** A teammate's mistake on a project does not absolve the person who assigned the work. The same holds for AI. If an agent introduces a security vulnerability and you commit it without review, the vulnerability is yours. Section 6.8 returns to this in detail.

---

## 6.5 The Agentic SDLC: Spec → Generate → Verify → Refine

The traditional SDLC — Requirements, Design, Implementation, Testing, Deployment — was designed around human execution speeds and human cognitive bottlenecks. When a developer writes a thousand lines of code per day, the bottleneck is implementation. When an agent writes a thousand lines in three minutes, the bottleneck shifts entirely.

The *Agentic SDLC* restructures the workflow around the new bottleneck: specification quality and verification rigour.

```
Spec → Generate → Verify → Refine
  ↑                              │
  └──────────────────────────────┘
```

This loop is iterative and fast — a single round typically takes minutes. The engineer's time is concentrated in the Spec and Verify phases. Generation is nearly instantaneous. Refinement feeds corrections back into the specification.

### Spec

*Specification* is the act of describing precisely and completely what the agent should produce. In the Agentic SDLC, specification is the primary engineering activity. Vague inputs produce plausible but incorrect outputs. The quality of your specification is the binding constraint on the quality of what is generated.

A complete specification for an AI agent includes:

- **Context**: What is this component? Where does it fit in the system?
- **Inputs and outputs**: What does the function receive? What must it return?
- **Behaviour rules**: At least five concrete behavioural requirements
- **Constraints**: What must the function explicitly NOT do?
- **Examples**: Concrete input-output pairs covering the normal case, edge cases, and error cases
- **Quality attributes**: Performance bounds, security requirements, style conventions

An underspecified prompt ("add validation to the login endpoint") produces code that technically adds validation but misses the cases the engineer cared about. A fully specified prompt produces code that can be verified against the specification directly.

### Generate

*Generation* is the act of invoking the agent with the specification to produce code, tests, documentation, or other artefacts. In the Agentic SDLC, generation is largely mechanical — the intellectual work is in the phases before and after it.

Key decisions at this phase:
- **Which model**: Match capability to task complexity — capable models for security-critical or complex reasoning tasks, faster models for boilerplate and scaffolding
- **Which agent**: Terminal agent or AI-native IDE, depending on task and context
- **What context to include**: Which files, conventions, and background does the agent need?

The common mistake is to treat generation as the primary activity. Engineers who spend most of their time crafting prompts to coax better generation are inverting the model. The specification should be thorough enough that generation is routine.

### Verify

*Verification* is the act of determining whether the generated output meets the specification. This is where most engineering judgment lives in the Agentic SDLC.

Verification is not optional and cannot be delegated to the agent itself. An agent asked to check its own output will often confirm that the output is correct even when it is not — it is evaluating against the same implicit model that produced the error ([Huang et al., 2023](https://arxiv.org/abs/2310.01798)). Verification requires a human with the engineering knowledge to recognise what correct looks like.

A structured verification checklist for AI-generated code:

| Category | Questions |
|---|---|
| **Functional correctness** | Does the code do what the specification says, for all specified cases? |
| **Edge cases** | Does it handle empty inputs, null values, boundary conditions? |
| **Security** | Does it introduce injection risks, broken auth, or unsafe defaults? |
| **Error handling** | Are errors surfaced, not silently swallowed? |
| **Type correctness** | Do types match? Does the type checker pass? |
| **Test coverage** | Does the generated test suite actually test the specified behaviours? |
| **Conventions** | Does the code follow the project's style, naming, and structure conventions? |
| **No accidental side effects** | Does the code modify state it was not supposed to touch? |

Automated checks — test suites, linters, type checkers, security scanners — are the first line of verification. They are necessary but not sufficient. Many specification violations pass automated checks because the test suite tests what the code does, not what the specification required.

An important nuance: agents can assist with verification as well as generation. A separate agent configured for security review can audit AI-generated code for vulnerability patterns without the cognitive overhead of the engineer who wrote the original specification ([Roychoudhury, 2025](https://arxiv.org/abs/2508.17343)). However, this only works when the verification agent has access to what Roychoudhury terms *intent inference* — an explicit representation of what the code was supposed to do, grounded in the specification or in program structure analysis — rather than simply re-reading the generated code and guessing. Verification-by-agent without a clear specification to verify against is the same problem as generation-without-specification, one layer deeper.

### Refine

*Refinement* is the act of returning to the specification with information from the verification step and adjusting before regenerating. Refinement is how the loop closes.

Common refinement triggers:

- A test fails: add the failing case as an explicit example in the specification
- The agent used a deprecated library: add a constraint ("do not use X, use Y")
- The output misunderstood a domain concept: add a clarifying definition
- The generated code is technically correct but violates a convention: add the convention to the context

The discipline of refinement is to *improve the specification*, not just re-run the agent with the same input hoping for a different result. Regenerating without refining is the most common time-wasting pattern in agentic workflows.

---

## 6.6 Patterns and Anti-Patterns

Agentic software engineering has accumulated a short but instructive body of practice. Hassan (2025) identifies patterns that distinguish effective AI-native engineers from those who simply adopted new tools without changing their approach. Each pattern has a corresponding failure mode:

| Pattern | Anti-Pattern it corrects |
|---|---|
| Specification-first development | Prompt-and-pray |
| Verification-driven generation | Confidence by plausibility |
| Context file discipline | Context starvation |
| Incremental delegation | Overlong agentic sessions |
| Commit granularity | Ownership transfer |

### Patterns

**Specification-first development.** Write the complete specification before invoking the agent. Engineers who start typing a prompt and refine it as they go produce weaker output than engineers who think through the specification completely, then invoke the agent once.

**Verification-driven generation.** Write the verification criteria — test cases, behavioural requirements, security checks — before generating the implementation. This is the AI-native analogue of test-driven development: the tests define what "correct" means, so that when the agent generates an implementation you can immediately verify it.

**Context file discipline.** Maintain a project-level context file (`CLAUDE.md`, `.cursorrules`, or equivalent) that the agent reads before every task. Keep it current. An outdated context file that references a library the project no longer uses causes the agent to generate code using the wrong dependency — silently.

**Incremental delegation.** Start with smaller, well-bounded tasks and expand the delegation as you build confidence in the agent's output for your specific codebase. An agent that reliably generates correct tests for utility functions may still produce insecure code in authentication flows. Calibrate trust by task type, not globally.

**Commit granularity.** Commit AI-generated changes frequently and at a granularity that makes diffs reviewable. A single 2,000-line commit labelled "AI refactor" is unverifiable in practice. Fifty commits of 40 lines each, each with a clear message, are verifiable.

### Anti-Patterns

**Prompt-and-pray.** The engineer submits a vague prompt, receives output, ships it without systematic verification, and hopes the tests catch any issues. Tests catch syntactic and logical errors; they rarely catch specification mismatches, security weaknesses, or architectural violations.

**Confidence by plausibility.** AI-generated code looks correct because it is well-formatted, uses familiar patterns, and contains no obvious syntax errors. Plausibility is not correctness. The Stanford Copilot study is the controlled-trial version of this anti-pattern ([Perry et al., 2022](https://arxiv.org/abs/2211.03622)).

**Ownership transfer.** The engineer treats AI-generated code as the AI's code — "the agent wrote this, not me" — and applies less rigorous review than they would to their own work. This is both epistemically wrong (the engineer directed and accepted the output) and professionally dangerous (the engineer is responsible for what they commit, regardless of how it was generated).

**Context starvation.** The engineer invokes the agent with minimal context — no project conventions, no relevant file background, no architectural constraints — and then iterates through many rounds of refinement because the initial output was disconnected from the project's reality. The fix is to invest in context upfront, not to iterate expensively later.

**Overlong agentic sessions.** A developer asks an agent to implement a new authentication flow — "full OAuth2 integration with GitHub, including token refresh." The agent runs for 23 steps: reads the codebase, writes token storage code, adds callback handlers, modifies session middleware, generates tests. The tests pass. The developer commits. Two days later, in code review, a colleague spots that the token storage in step 4 wrote refresh tokens to a plain-text log file — and every subsequent step was built on that foundation. Unwinding it requires reworking 19 steps of layered changes.

The rule: establish a verification checkpoint after every 3–5 significant steps. Confirm the agent is still on track before continuing.

---

## 6.7 Working with an AI Teammate: Productivity and Risk

Hoda (2025) argues that the field risks making a categorical error: treating agentic software engineering as an acceleration of *coding* when it is actually a transformation of *the entire software process* ([Hoda, 2025](https://arxiv.org/abs/2510.19692)). Teams that adopt AI agents to write code faster while leaving their requirements practices, design processes, review cultures, and testing disciplines unchanged are, in Hoda's framing, using a paradigm-shifting tool within a paradigm that has not shifted. The efficiency gains are real but bounded. The deeper opportunity — and the deeper risk — lies in what happens when AI agents are applied across the full socio-technical process, not just the coding step.

### Productivity Expectations

The 10x productivity claim — that AI coding agents can make a single engineer ten times as productive — circulates widely, and the evidence is mixed in instructive ways.

Studies consistently find productivity gains for *specific task types*: routine code generation, test scaffolding, documentation, boilerplate, and translation between languages. [GitHub's internal study (2023)](https://github.blog/2022-09-07-research-quantifying-github-copilots-impact-on-developer-productivity/) found Copilot users completed certain coding tasks 55% faster. McKinsey (2023) found mid-complexity tasks saw 20–45% time reductions. These are real and significant gains.

The 10x claim typically comes from productivity profiles that are heavily skewed toward tasks AI handles well. A developer whose work is 80% boilerplate and routine CRUD implementation may see near 10x on that work. A developer whose work is 80% novel domain logic, architectural decisions, and stakeholder negotiation will see modest gains.

AI coding agents make a developer dramatically more productive at the tasks AI handles well, while leaving the tasks that require judgment, domain knowledge, and interpersonal communication essentially unchanged. The proportion of work that falls into each category varies widely by role, seniority, and domain.

### Risks and Concerns

The productivity gains are real, but so are the incident reports. In 2025, reports of *agentic incidents* — cases where AI coding agents took destructive, irreversible actions — proliferated across developer communities. Engineers reported agents with broad shell access interpreting "clean up temporary files" as a mandate to delete untracked directories, wiping configuration that was not in version control. Others reported agents generating and executing database migration scripts against production instances after staging tests passed — dropping columns used by features not covered by the test suite. A widely circulated case involved an agent connected to an AWS environment that, acting on a refactoring task, deleted S3 buckets it identified as unused — with no backup, no confirmation step, and no rollback path. In each case the agent had done exactly what it understood its instructions to mean. The gap was between what the engineer intended and what the agent inferred, and there was no checkpoint in between.

Liu et al. (2023) document the baseline problem: 32.2% of ChatGPT-generated code samples produced incorrect outputs, and nearly half had maintainability issues detectable by standard static analysis ([Liu et al., 2023](https://arxiv.org/abs/2307.12596)). ChatGPT could self-repair some defects when shown the errors — but only when the engineer knew to ask. An engineer who accepted the output without verification shipped the failure.

**Overreliance and skill atrophy.** Perry et al. (2022) identified a mechanism beyond the immediate code errors: Copilot users relied on the tool as a substitute for understanding, rather than as an accelerator for it. Engineers who stop practising a skill because AI does it for them lose the judgment needed to verify AI's execution of that skill. Overreliance is not a hypothetical future risk — it is a documented present-day outcome ([Perry et al., 2022](https://arxiv.org/abs/2211.03622)).

**Responsibility and accountability.** When AI-generated code causes a production incident, the question of who is responsible is not legally ambiguous: the engineer who committed the code and the organisation that deployed it are responsible. AI systems are not legal persons. They cannot be held accountable. The accountability sits with the humans in the chain.

**Intellectual property and licences.** AI models are trained on publicly available code, much of it under open-source licences. When an agent generates code that closely resembles a licensed open-source function, questions arise about licence obligations. As of 2025, this remains an active area of litigation in multiple jurisdictions. Engineering teams working on proprietary products should understand their organisation's policy on AI-generated code and verify that generated output does not reproduce copyrighted material verbatim.

**Autonomy and the expanding blast radius.** As agents become more capable and are delegated more consequential tasks, the potential damage from a single bad agentic session increases. An agent that generates a wrong function is a minor problem. An agent that refactors a database schema incorrectly, generates a migration script, and runs it against a production database is a major incident. The appropriate response is not to avoid agentic tools — it is to match the agent's autonomy to the reversibility of its actions, a principle addressed in Section 6.8.

**Security attack surface.** Agents that are connected to external systems — issue trackers, CI pipelines, production APIs — can be manipulated through malicious content in those systems. *Prompt injection* attacks embed AI instructions in user-controlled content (a ticket title, a code comment, a test fixture) that the agent reads and executes as instructions. Chapter 9 covers this threat in detail; for now, the principle is: treat any content the agent reads from an external system as untrusted input, just as you would user-supplied data in a web application.

---

## 6.8 Human Responsibility in the Agentic Era

The human engineer retains full responsibility for everything that is committed, deployed, or shipped — regardless of how it was produced.

This is not a philosophical position. It is the practical reality of how accountability works in engineering organisations and in law. When a software defect causes harm, the investigation asks who designed, built, tested, and deployed the system. The answer is the humans and the organisation — not the tools they used. This was true when the tool was a compiler, a framework, or a cloud provider. It remains true when the tool is an AI agent.

Roychoudhury et al. (2025) frame this directly in their analysis of agentic SE systems: the central challenge is not capability but *trust* — establishing the conditions under which engineers and organisations can place justified confidence in AI-generated outputs ([Roychoudhury et al., 2025](https://arxiv.org/abs/2502.13767)). Trust is not granted by default. It is earned through verification discipline, bounded delegation, and accumulated evidence of reliable behaviour in specific contexts. An agent that has produced correct, secure authentication code fifty times on a project earns a degree of trust for that task type. That trust does not generalise to database migrations, production deployments, or security-critical logic the agent has not been tested against.

This has three concrete implications for agentic practice:

**Review everything before it is committed.** The agent's output is a first draft, not a final product. The engineer's review is what transforms it from a generated artefact into code the engineer stands behind. This review should be at least as thorough as a review of code written by a junior teammate — someone competent but fallible, whose work you are co-signing by approving.

**Understand what you are committing.** Committing code you do not understand is not acceptable regardless of its origin. An engineer who cannot explain what a function does, why it uses a particular approach, and what its failure modes are, has not adequately verified the output. If the agent produces code you do not understand, the right response is to ask the agent to explain it, to read the relevant documentation, and to ensure you understand it before committing — not to trust that it looks plausible.

**Set appropriate delegation boundaries.** Not every task should be fully delegated. Determine which actions in your agentic workflow are irreversible (database migrations, production deployments, external API calls that have side effects) and require explicit human approval before the agent takes them. Reversible actions in a version-controlled environment — editing files, generating tests, updating documentation — can be delegated with human review at the end. Irreversible actions require human-in-the-loop approval at the point of action.

The tool does not make the engineer. Jensen Huang was right that the barrier to producing code has fallen. The barrier to producing *correct, secure, maintainable* code has not moved. That barrier has always been engineering judgment, and it remains so.

---

## 6.9 Key Takeaways

1. **A tool does not confer judgment.** Liu et al. (2023) found that 32.2% of AI-generated code samples were functionally incorrect; Perry et al. (2022) found that developers using AI produced more insecure code with greater confidence. Agentic tools amplify existing engineering capability — they do not substitute for it.

2. **An AI coding agent is not an LLM.** It is an LLM connected to tools, skills, connectors, and memory that allow it to take multi-step actions in the world. The difference is consequential: agents can make irreversible changes that require careful oversight.

3. **Terminal agents and AI-native IDEs serve different use cases.** Claude Code and Gemini CLI suit complex, flexible, terminal-centric work. Cursor and Windsurf suit sustained feature work where visual context alongside the AI conversation speeds verification. Neither is universally superior.

4. **The four components of an agent are tools, skills, connectors, and memory.** Tools are atomic actions. Skills are reusable multi-step capabilities. Connectors link the agent to external systems. Memory determines what persists across steps and sessions.

5. **The Agentic SDLC is Spec → Generate → Verify → Refine.** Generation is fast and cheap; specification and verification are where engineering judgment concentrates. Investing in specification quality is more efficient than iterating through poor generations.

6. **Common anti-patterns include prompt-and-pray, confidence by plausibility, and ownership transfer.** All three result from treating AI output as trustworthy by default rather than as a first draft requiring systematic verification.

7. **The 10x productivity claim is partially true and easily misread.** AI coding agents produce large gains for tasks they handle well — boilerplate, tests, documentation. They produce modest gains for tasks requiring deep judgment. The proportion of each in a given role determines the realistic productivity impact.

8. **Significant risks include overreliance, accountability gaps, IP and licence exposure, and prompt injection.** None of these are reasons to avoid agentic tools — they are reasons to use them with engineered controls.

9. **Accountability does not transfer to the AI.** The engineer who commits AI-generated code is responsible for that code. Review before commit is not optional.

---

## Review Questions

1. A team lead proposes giving a junior developer access to Claude Code to implement a new payment processing feature autonomously, with a final code review at the end. Using the concepts from this chapter — agent components, the Agentic SDLC, and human responsibility — identify three specific risks in this proposal and recommend concrete changes to the workflow that would mitigate each risk.

2. The anti-pattern "confidence by plausibility" describes engineers accepting AI output because it looks correct, rather than because it has been verified to be correct. Design a verification checklist for AI-generated authentication code. What specific categories of error would your checklist catch that automated tests might not?

3. Your team is considering adopting an AI-native IDE (Cursor or Windsurf) versus a terminal-based agent (Claude Code). The project is a 200-KLOC Python monolith with a comprehensive test suite and no AI tooling currently. What questions would you ask to determine which approach is more appropriate, and what evidence would lead you toward each choice?

4. A developer uses an AI agent to implement a database migration. The agent runs the migration against the staging database, observes success, and reports the task complete. The developer commits and deploys. The migration silently drops a column used by a feature not covered in the test suite. Who is responsible, and what process changes would have prevented the incident?

---

## Further Reading

- Hassan, A. E. (2025). *Agentic Software Engineering: Building Trustworthy Software with Stochastic Teammates at Unprecedented Scale*. [https://agenticse-book.github.io/pdf/AgenticSE_Book.pdf](https://agenticse-book.github.io/pdf/AgenticSE_Book.pdf)
- Liu, Y., Le-Cong, T., Widyasari, R., Tantithamthavorn, C., Li, L., Le, X.-B. D., & Lo, D. (2023). *Refining ChatGPT-Generated Code: Characterizing and Mitigating Code Quality Issues*. arXiv:2307.12596. [https://arxiv.org/abs/2307.12596](https://arxiv.org/abs/2307.12596)
- Perry, N., Srivastava, M., Kumar, D., & Boneh, D. (2022). *Do Users Write More Insecure Code with AI Assistants?* ACM CCS. [https://arxiv.org/abs/2211.03622](https://arxiv.org/abs/2211.03622)
- Russell, S., & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.). Pearson. [https://aima.cs.berkeley.edu/](https://aima.cs.berkeley.edu/)
- Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., & Cao, Y. (2022). *ReAct: Synergizing Reasoning and Acting in Language Models*. [https://arxiv.org/abs/2210.03629](https://arxiv.org/abs/2210.03629)
- Anthropic. (2024). *Model Context Protocol Specification*. [https://modelcontextprotocol.io](https://modelcontextprotocol.io)
- GitHub. (2023). *Research: Quantifying GitHub Copilot's Impact on Developer Productivity*. [https://github.blog/2022-09-07-research-quantifying-github-copilots-impact-on-developer-productivity/](https://github.blog/2022-09-07-research-quantifying-github-copilots-impact-on-developer-productivity/)
- Chen, M., et al. (2021). *Evaluating Large Language Models Trained on Code (Codex)*. [https://arxiv.org/abs/2107.03374](https://arxiv.org/abs/2107.03374)
- Roychoudhury, A., Pasareanu, C., Pradel, M., & Ray, B. (2025). *Agentic AI Software Engineers: Programming with Trust*. arXiv:2502.13767. [https://arxiv.org/abs/2502.13767](https://arxiv.org/abs/2502.13767)
- Roychoudhury, A. (2025). *Agentic AI for Software: Thoughts from the Software Engineering Community*. arXiv:2508.17343. [https://arxiv.org/abs/2508.17343](https://arxiv.org/abs/2508.17343)
- Hoda, R. (2025). *Toward Agentic Software Engineering Beyond Code: Framing Vision, Values, and Vocabulary*. arXiv:2510.19692. [https://arxiv.org/abs/2510.19692](https://arxiv.org/abs/2510.19692)
