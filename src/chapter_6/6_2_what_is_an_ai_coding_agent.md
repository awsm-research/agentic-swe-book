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

### 6.2.2 A Six-Level Taxonomy of AI-Assisted Software Engineering

Not all AI involvement in software development is equivalent. A developer using IDE autocomplete and an engineer directing an autonomous refactoring agent are both, in a broad sense, using "AI in development" — but the engineering consequences differ categorically: the degree of human oversight required, the skill of delegation needed, and the blast radius of a mistake each escalate with the level of autonomy delegated. A recent taxonomy, paralleling the SAE International framework for vehicle driving automation, proposes six discrete levels of AI autonomy in software engineering ([arXiv:2509.06216, 2025](https://arxiv.org/html/2509.06216v2)). The automotive parallel is instructive precisely because the SAE levels are well understood in terms of what the *human operator* remains responsible for at each tier.

| Level | Name | Core Function | Representative Technologies | SAE Parallel |
|---|---|---|---|---|
| **0** | Manual Coding | Human translates ideas into code by typing, with no AI involvement | Plain text editors (Notepad, vi, Emacs) | Level 0: No Automation |
| **1** | Token Assistance | Predicts the next token from the engineer's immediate editing context | IDE autocomplete (IntelliSense, basic tab-completion) | Level 1: Driver Assistance |
| **2** | Task-Agentic | Generates a complete code block, test, or artefact from a task description | GitHub Copilot, Amazon CodeWhisperer, Tabnine | Level 2: Partial Automation |
| **3** | Goal-Agentic | Devises and executes a multi-step plan from a stated technical goal | Claude Code, Cognition's Devin, Google Jules, OpenAI Codex | Level 3: Conditional Automation |
| **4** | Specialised Domain Autonomy | Translates a broad mandate into concrete goals within a defined technical domain | GPT-5 (frontend web development), specialised security agents | Level 4: High Driving Automation |
| **5** | General Domain Autonomy | Exercises high autonomy across any technical domain at arbitrary scale | Conceptual — no production system as of 2025 | Level 5: Full Driving Automation |

The critical boundary in this taxonomy lies between Level 2 and Level 3. Below it, the human retains step-by-step control: every suggestion is evaluated individually, and the engineer determines the next action. Above it, the agent plans and executes multi-step sequences autonomously — reading files, writing code, running tests, and iterating — with the engineer setting the goal and verifying the result. This is precisely the boundary at which the engineering disciplines of specification quality and verification rigour become central to the workflow rather than peripheral to it.

Current production tooling spans Levels 1 through 3. Level 1 autocomplete is present in every modern IDE and carries no meaningful oversight burden — the engineer sees each suggestion before accepting it. Level 2 task-agentic systems (GitHub Copilot, Amazon CodeWhisperer) generate complete functions, test suites, and documentation stubs from a developer description; the engineer still approves each generated block. Level 3 goal-agentic systems — the primary subject of this chapter — accept a technical goal such as "implement rate limiting on the API gateway" and autonomously plan, execute, and verify the required changes across multiple files and subsystems without human mediation between steps.

Level 4 remains an emerging frontier. Specialisation at this level occurs along two primary axes: *technology stack* and *quality attributes*. A stack-specialised Level 4 system combines deep implementation capability with calibrated domain judgment — GPT-5, positioned for frontend web development, combines what its official guidance describes as "rigorous implementation abilities" with technologies such as Next.js and Tailwind CSS alongside "excellent baseline aesthetic taste." A quality-attribute-specialised Level 4 agent takes the orthogonal approach: deep expertise in a single attribute (for example, security) applied consistently across any technology stack, translating a broad mandate such as "ensure the reliability of the payment service" into a prioritised list of concrete technical goals. Level 5, in which an agent would generalise this specialised capability across *all* technology domains and *all* quality attributes simultaneously, remains at the conceptual stage.

For the practices described in this chapter, Level 3 is the operative tier. It is the level at which agents begin to plan autonomously, and therefore the level at which the engineer's oversight model must change — from supervising individual suggestions to specifying goals clearly and verifying the outputs of multi-step agentic sessions.

### 6.2.3 AI Coding Agents in the Terminal

The first category of AI coding agent operates directly in the terminal, treating the file system and shell as its primary environment. Two widely used examples are *Claude Code* (Anthropic, 2024) and *Gemini CLI* (Google, 2024).

*Claude Code* is a command-line interface that runs in the engineer's terminal. The engineer describes a task in natural language; Claude Code reads the relevant files, writes code, runs tests, and iterates — all within the existing project structure, using the existing toolchain, without opening a browser or an IDE. It is designed to be invisible to the project: it adds no dependencies, requires no plugins, and leaves the engineer's workflow otherwise unchanged.

*Gemini CLI* provides similar terminal-based agentic capabilities backed by Google's Gemini model family. Both tools share a design philosophy: bring the AI to the engineer's environment, rather than requiring the engineer to move to an AI-specific environment.

Terminal agents suit engineers who prefer full control over their toolchain, work on complex or unfamiliar codebases where reading source is the primary activity, or operate in environments (remote servers, CI pipelines) where a graphical IDE is unavailable.

### 6.2.4 AI-Native IDEs

The second category integrates agentic AI directly into the editing experience. *Cursor* and *Windsurf* are the most widely adopted examples as of 2025.

*Cursor* is a fork of Visual Studio Code with AI capabilities built into the editor at a fundamental level — not as a plugin but as a first-class part of the interface. The agent can see the entire codebase, understand the editor's open files, run commands in the integrated terminal, and apply changes directly to open files. Engineers interact via a chat panel that sits alongside the editor.

*Windsurf* (Codeium, 2024) takes a similar approach with an additional emphasis on *flow* — the agent proactively observes what the engineer is doing and offers suggestions without being explicitly prompted, analogous to a pair programmer who notices when you are stuck.

AI-native IDEs suit engineers doing sustained feature work in a single codebase, working on tasks where visual context (seeing the code alongside the AI conversation) speeds up verification, or transitioning to agentic workflows from an IDE-centric background.

For engineers new to agentic workflows, an AI-native IDE is the lower-friction starting point — the visual context alongside the conversation speeds up verification. Terminal agents earn their place when shell flexibility, composability, or remote access matters more than IDE integration. Many engineers use both, choosing by task.

---
