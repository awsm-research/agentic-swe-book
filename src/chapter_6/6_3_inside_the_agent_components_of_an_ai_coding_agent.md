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
