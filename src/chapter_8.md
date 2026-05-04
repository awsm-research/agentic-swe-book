# Chapter 8: Configuring the Agent's World — Context, Skills, and Tools
<!-- 
> *"An agent is only as good as the world it can see. What you choose to put in front of it — and what you keep out — is an engineering decision, not a configuration detail."*

---

## Learning Objectives

By the end of this chapter, you will be able to:

1. Explain the purpose of `AGENTS.md` and why it serves as a cross-tool context standard.
2. Define subagents and configure them with appropriate model selection, tool allowlists, permission modes, and turn limits.
3. Describe what Skills are in Claude Code and how they differ from retrieval-based approaches.
4. Create custom Skills as directories with `SKILL.md` files.
5. Connect external tools to an agent using MCP servers.
6. Reason about token cost when enabling MCP tools and make deliberate trade-offs.

---

## 8.1 The Agent Configuration Problem

When you first run a coding agent on a large codebase, it faces a fundamental problem: it can read any file, run any command, and potentially take any action — but it has no idea what it *should* do, what conventions to follow, what tools are sanctioned, or what parts of the system are off-limits.

Left unconfigured, an agent will make its best guesses. It may use a testing framework you abandoned two years ago, commit without signing, push to a branch that triggers a production deployment, or generate code in a style that conflicts with your team's standards. These are not AI failures — they are *configuration failures*.

The central insight of this chapter is that configuring the agent's world is itself an engineering task. It requires the same rigour as writing code: deliberate decisions about what information the agent should have, what it is allowed to do, and what external systems it can reach.

Three mechanisms serve this purpose in modern agent tooling:

1. **Context files** (`AGENTS.md`, `CLAUDE.md`) — what the agent knows about your project
2. **Subagent definitions** — how agents are composed, scoped, and constrained
3. **Tools** — what external capabilities the agent can invoke

---

## 8.2 `AGENTS.md`: The Cross-Tool Context Standard

### 8.2.1 What It Is

`AGENTS.md` is a plain Markdown file, typically placed at the root of a repository, that describes your project to an AI coding agent. Think of it as the onboarding document you would write for a new engineer joining the team — except the new engineer reads it every time it starts a task.

The file is an emerging cross-tool standard. It is recognised by:

- **Claude Code** (reads `CLAUDE.md` or `AGENTS.md`)
- **Cursor** (reads `.cursor/rules` and `AGENTS.md`)
- **OpenAI Codex CLI** (reads `AGENTS.md`)
- **Gemini CLI** (reads `AGENTS.md`)
- **GitHub Copilot Workspace** (reads `AGENTS.md`)

Using a standard filename means the same instructions apply consistently regardless of which tool your team members use. You write the context once; every agent respects it.

### 8.2.2 What to Put in It

A well-structured `AGENTS.md` answers five questions:

1. **What is this project?** — One paragraph on the domain, the users, and the business purpose.
2. **How is it structured?** — Key directories, the technology stack, and the data flow at a high level.
3. **How do I build and test it?** — The exact commands to build, run tests, check types, and lint.
4. **What are the conventions?** — Naming, code style, commit message format, branch strategy.
5. **What should I never do?** — Explicit constraints: things that will break production, violate policy, or require human sign-off.

```markdown
# AGENTS.md

## Project: Meridian Task API

Meridian is a task-management REST API used by field technicians to log and 
assign repair jobs. It processes ~50,000 requests per day from mobile clients.

## Stack
- Runtime: Python 3.12, FastAPI
- Database: PostgreSQL 16 (managed by Supabase)
- Testing: pytest + httpx (async)
- CI: GitHub Actions (see .github/workflows/)

## Build & Test
```bash
uv run pytest                   # run all tests
uv run ruff check .             # lint
uv run mypy src/                # type-check
```

## Conventions
- All endpoints must have corresponding tests in tests/
- Use snake_case for Python identifiers; kebab-case for URL segments
- Commit messages: feat/fix/chore/docs followed by a colon and imperative verb
  Example: `feat: add pagination to task list endpoint`
- Never commit directly to main — open a PR

## Do Not
- Never drop or truncate tables without a reviewed migration
- Never add a new dependency without updating pyproject.toml and uv.lock
- Never disable type checking for a whole module (per-line ignores are acceptable)
```

### 8.2.3 Hierarchical Context Files

Both Claude Code and Cursor support *nested* context files. If a file `src/api/CLAUDE.md` exists, its contents are added to the agent's context when it is working inside `src/api/`. This allows you to:

- Set project-wide conventions at the root
- Add module-specific conventions at subdirectory level
- Override or supplement root instructions without duplicating them

```
project-root/
├── AGENTS.md              ← project-wide: stack, global conventions
├── src/
│   ├── api/
│   │   └── CLAUDE.md      ← API-specific: endpoint conventions, auth rules
│   └── workers/
│       └── CLAUDE.md      ← Worker-specific: retry policies, idempotency rules
└── tests/
    └── CLAUDE.md          ← Test conventions: fixtures, mocking policy
```

The agent automatically merges these files as it navigates the codebase. You get targeted context without polluting the global configuration.

### 8.2.4 Context Files as Living Documentation

A practical benefit of `AGENTS.md` is that it forces the team to articulate conventions that often exist only in senior engineers' heads. When you write "never disable type checking for a whole module," you are not just instructing the agent — you are documenting a team decision that a new human engineer also needs to know.

Treat `AGENTS.md` as a first-class document: review it in pull requests, update it when conventions change, and version it with the code. It is not a configuration file — it is documentation that happens to be machine-readable.

---

## 8.3 Subagents: Composing Scoped, Specialised Agents

### 8.3.1 Why Subagents

A single general-purpose agent can handle many tasks, but it has limitations:

- It must operate within a single permission boundary — either all tools are allowed or none are
- Long tasks risk hitting context limits, with early context "falling out" of the window
- There is no way to run tasks in parallel unless multiple agent instances are launched
- A bug-fixing agent and a deployment agent should not have the same permissions

*Subagents* address these problems. A subagent is a specialised agent, with its own model, tool allowlist, and permission mode, that can be invoked by an orchestrator agent to handle a specific kind of work.

Claude Code implements subagents via Markdown definition files in `.claude/agents/`.

### 8.3.2 Subagent Definition Files

A subagent definition file is a Markdown file with a YAML frontmatter block that specifies configuration, followed by a natural-language description of the subagent's purpose and behaviour.

```
.claude/
└── agents/
    ├── code-reviewer.md
    ├── test-runner.md
    └── db-migrator.md
```

**Example: A read-only code review subagent**

```markdown
---
name: code-reviewer
description: Reviews code for quality, security, and style. Use when the user asks for a review or after implementing a feature.
model: claude-opus-4-7
tools: [read_file, list_files, grep]
permission_mode: read_only
maxTurns: 20
---

You are a rigorous code reviewer. Your job is to:
1. Read the changed files and their surrounding context
2. Check for security vulnerabilities, edge cases, and style violations
3. Produce a structured review with: Summary, Issues (blocker / warning / suggestion), and Verdict

You have read-only access. You cannot modify files or run commands.
Always check: input validation, error handling, SQL injection, and test coverage.
```

### 8.3.3 Configuration Parameters

Each parameter in the frontmatter is a deliberate engineering decision:

**`model`** — Which language model to use for this subagent. Subagents are not required to use the same model as the orchestrator. A common pattern:

| Subagent role | Recommended model | Rationale |
|---|---|---|
| Code review | Opus (most capable) | Requires nuanced judgment |
| Test generation | Sonnet (balanced) | Predictable, formulaic output |
| Docstring writer | Haiku (fast/cheap) | Simple, high-volume task |
| Database migration | Sonnet | Correctness matters; speed less so |

**`tools`** — An explicit allowlist of tools this subagent may invoke. This is the *principle of least privilege* applied to agents: give each subagent only the tools it needs to do its job. A code reviewer needs `read_file` and `grep` — it does not need `run_command` or `write_file`.

Common tool categories:

| Category | Examples | Risk level |
|---|---|---|
| Read | `read_file`, `list_files`, `grep` | Low |
| Write | `write_file`, `edit_file` | Medium |
| Execute | `run_command`, `bash` | High |
| Network | `fetch_url`, `call_api` | High |
| Agent | `spawn_agent` | High |

**`permission_mode`** — Controls whether the subagent can take actions that affect the environment:

- `read_only` — Can read files and search the codebase; cannot modify anything
- `sandboxed` — Can read and write files in a temporary workspace; changes are discarded
- `restricted` — Can read and write; cannot execute shell commands
- `normal` — Full access to allowed tools
- `auto` — Full access with no confirmation prompts (use with caution)

**`maxTurns`** — The maximum number of tool-call cycles before the subagent stops. This is a safety mechanism. Without a turn limit, a subagent that encounters an unexpected state can loop indefinitely, consuming tokens and potentially taking unintended actions. Start with a conservative limit (10–20 turns) and increase it only if the subagent genuinely needs more.

### 8.3.4 Background Tasks

Subagents can be invoked as *background tasks* — running concurrently while the orchestrator continues other work. This is particularly useful for:

- Running a test suite while implementing the next feature
- Performing a security scan while writing documentation
- Parallelising independent code generation tasks

In Claude Code, background subagents are launched via the `--background` flag or the `spawn_agent` tool with `background: true`. GitHub's Copilot Workspace uses a similar model for parallelising code review.

Background subagents introduce coordination complexity: the orchestrator must eventually collect results, handle failures, and reconcile conflicting changes. Design background tasks to be *independent* — they should not write to the same files or depend on each other's outputs.

```
Orchestrator
    │
    ├── [background] test-runner: run the full test suite
    ├── [background] code-reviewer: review the last commit
    │
    └── [foreground] Continue: implement the next feature
                                    │
                                    └── Wait for background results
                                        → If tests failed, fix before proceeding
```

---

## 8.4 Skills: On-Demand Knowledge Injection

### 8.4.1 The Retrieval Temptation

A common approach to giving agents specialised knowledge is *retrieval-augmented generation* (RAG): index a corpus of documents, embed the user's query, find the nearest neighbours in the vector space, and inject the matching chunks into the prompt.

RAG works well for large, unstructured corpora — customer support knowledge bases, research literature, product documentation. For software engineering tasks, it has a significant limitation: *semantic similarity is not the same as relevance*. The code chunk most similar to your query embedding may not be the code the agent actually needs. Retrieval introduces non-determinism: the same task may inject different context on different runs, producing inconsistent results.

### 8.4.2 What Skills Are

A *Skill* in Claude Code is a different mechanism. It is a curated, deterministic knowledge injection — a Markdown document that contains exactly the information an agent needs for a specific class of task, loaded on demand when a matching command is invoked.

When you type `/security-review` in Claude Code, a Skill file is loaded into the agent's context verbatim. No embedding. No retrieval. No probability. The exact content you wrote is what the agent receives.

The key properties of Skills:

- **Deterministic**: The same command always injects the same content
- **Curated**: A human engineer decides what goes in the Skill, not a retrieval algorithm
- **On-demand**: Content is only injected when explicitly invoked, not pre-loaded for every task
- **Composable**: Skills can invoke other Skills and spawn subagents

This makes Skills appropriate for *process knowledge* — how to perform a specific type of task — rather than *factual knowledge* — what something is. Use Skills for: "how we do code reviews on this team," "how we write database migrations," "our checklist for releasing to production." Use RAG (or context files) for: "what does this library's API look like," "what are the features of this third-party service."

### 8.4.3 Creating Custom Skills

Skills are stored as directories in `.claude/skills/`. Each Skill is a directory containing at minimum a `SKILL.md` file.

```
.claude/
└── skills/
    ├── security-review/
    │   └── SKILL.md
    ├── db-migration/
    │   ├── SKILL.md
    │   └── migration_template.sql
    └── release-checklist/
        └── SKILL.md
```

The `SKILL.md` file contains the instructions and context the agent receives when the Skill is invoked. It is plain Markdown — write it as if you are writing a process guide for a capable engineer who is unfamiliar with your specific conventions.

**Example: A database migration Skill**

```markdown
# Skill: db-migration

Invoked as: /db-migration

## Purpose
Generate and validate Alembic database migrations for the Meridian project.

## Context
- We use Alembic for migrations; never hand-write raw SQL for schema changes
- Migrations live in db/migrations/
- Always include both upgrade() and downgrade() functions
- All migrations must be reversible unless explicitly annotated otherwise

## Process
1. Read the current model in src/models/ to understand the target schema
2. Read the most recent migration to understand the current state
3. Generate an Alembic migration using `alembic revision --autogenerate`
4. Review the generated migration — autogenerate is not always correct, especially for:
   - Column type changes (may drop and recreate)
   - Index naming conflicts
   - Constraint naming
5. Verify the downgrade function is correct
6. Run `alembic upgrade head` in a test environment and confirm success

## Output
Return the migration file path and a summary of what changed.

## Do Not
- Never use `--autogenerate` for data migrations — write those manually
- Never drop a column without confirming it is not in use in the application code
```

The Skill directory can contain additional files — templates, checklists, example outputs — that the `SKILL.md` can reference or that the agent can read directly.

### 8.4.4 Invoking Skills

Skills are invoked using the slash command syntax in Claude Code:

```
/db-migration Add a not-null column for assignee_id to the tasks table
/security-review Review the authentication module
/release-checklist Prepare the v2.3.1 release
```

The Skill is loaded, the agent reads the instructions, and then applies them to the specific request. The result is a *structured, repeatable process* — the agent behaves like an engineer who has been trained in your specific workflows, not a general-purpose assistant guessing at conventions.

---

## 8.5 MCP Servers: Connecting the Agent to External Tools

### 8.5.1 The Model Context Protocol

The *Model Context Protocol* (MCP) is an open standard, introduced by Anthropic in 2024, that defines how AI agents communicate with external tools and data sources. An MCP server is a process that exposes tools, resources, and prompts to any MCP-compatible agent.

Before MCP, each AI tool had its own bespoke integration format: a plugin system, a custom API wrapper, or a proprietary tool definition format. MCP standardises this: if you write an MCP server for your company's internal ticketing system, it works with Claude Code, Cursor, Gemini CLI, and any other MCP-compatible client without modification.

The architecture is straightforward:

```
Agent (Claude Code)
    │
    └── MCP Client ──── [stdio or HTTP] ──── MCP Server
                                                 │
                                                 ├── Tool: create_issue(title, body, labels)
                                                 ├── Tool: get_issue(id)
                                                 ├── Resource: issues://open
                                                 └── Prompt: triage_issue
```

### 8.5.2 Categories of MCP Servers

MCP servers fall into several broad categories:

**Project management and communication**
- Notion (read/write pages and databases)
- Linear (create and update issues)
- GitHub (pull requests, issues, code search)
- Jira (tickets, sprints, boards)
- Slack (send messages, read channels)

**Design and assets**
- Figma (read design specs, extract tokens, inspect component properties)
- Storybook (browse component library)

**Databases and data**
- PostgreSQL (run queries, read schema)
- Supabase (tables, storage, auth)
- BigQuery (analytics queries)
- Redis (read/write cache)

**Infrastructure and observability**
- AWS (EC2, S3, Lambda operations)
- Kubernetes (pod management, logs)
- Datadog (metrics, alerts, dashboards)
- Sentry (error tracking, stack traces)

**Internal tools**
- Custom REST APIs
- Internal documentation systems
- Company-specific data pipelines

### 8.5.3 Configuring MCP in Claude Code

MCP servers are configured in Claude Code's settings file (`.claude/settings.json` for project-level, `~/.claude/settings.json` for user-level):

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "${DATABASE_URL}"
      }
    },
    "figma": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-figma"],
      "env": {
        "FIGMA_ACCESS_TOKEN": "${FIGMA_TOKEN}"
      }
    }
  }
}
```

Once configured, the tools exposed by these servers are available to the agent like any built-in tool. The agent can call `github_create_issue(title, body)` or `postgres_query(sql)` as naturally as it calls `read_file(path)`.

### 8.5.4 What Agents Can Do with MCP

The combination of MCP servers transforms an agent from a code-generation tool into an active participant in the full engineering workflow:

```
User: "The login endpoint is throwing 500 errors in production. Fix it."

Agent (with MCP):
  1. [Sentry MCP] Fetch the latest 500 errors from the login endpoint
  2. [GitHub MCP] Find the last commit that touched src/auth/login.py
  3. [Read file] Read the current login.py implementation
  4. [Postgres MCP] Query the auth_attempts table to check for patterns
  5. Identify the bug: null pointer on missing device_fingerprint field
  6. [Write file] Fix the null check in login.py
  7. [Run tests] pytest tests/test_auth.py
  8. [GitHub MCP] Create a pull request with the fix and the Sentry error ID in the description
  9. [Linear MCP] Update the linked ticket to "In Review"
```

Without MCP, steps 1, 2, 4, 8, and 9 require the engineer to fetch information manually and paste it into the agent. With MCP, the agent handles the full workflow autonomously.

---

## 8.6 Token Cost: The Hidden Tax on MCP

### 8.6.1 How MCP Tools Consume Context

Each MCP server you enable adds *tool descriptions* to the agent's context at the start of every interaction. These descriptions tell the model what tools are available, what parameters they accept, and what they return. They are necessary — without them, the model cannot use the tools — but they are not free.

A typical MCP tool description consumes 200–800 tokens. A server with 20 tools consumes 4,000–16,000 tokens before the agent has read a single file or received a single instruction. With multiple servers enabled, this overhead compounds:

| MCP Server | Approximate tools | Approximate tokens |
|---|---|---|
| GitHub | 30 tools | ~12,000 tokens |
| Linear | 15 tools | ~6,000 tokens |
| Figma | 10 tools | ~4,000 tokens |
| PostgreSQL | 8 tools | ~3,000 tokens |
| Sentry | 12 tools | ~5,000 tokens |
| **Total** | **75 tools** | **~30,000 tokens** |

At Claude Sonnet pricing (roughly $3 per million input tokens), 30,000 tokens of tool descriptions costs approximately $0.09 per agent interaction. Across a team of 20 engineers running 30 agent interactions per day, this is ~$1,600 per month — just for tool descriptions, before any actual work is done.

More importantly: a context window loaded with 75 tool descriptions is a context window with 30,000 fewer tokens available for code, specifications, test results, and reasoning. This directly reduces the agent's effectiveness on complex tasks.

### 8.6.2 The Principle: Enable What You Need

The correct approach is *task-appropriate tool selection*:

- **Do not enable all MCP servers globally.** Configure servers at the project level (`.claude/settings.json`) only when they are relevant to that project.
- **Disable servers when not in use.** Uncheck an MCP server in Claude Code's settings during sessions where it is not needed.
- **Use subagents with constrained tool sets.** Instead of giving the main orchestrator access to all tools, give each subagent only the tools its role requires.
- **Prefer file-based context for static information.** If the information you need from a tool does not change (e.g., a design spec you fetched yesterday), save it to a file and read the file rather than re-fetching it via MCP on every interaction.

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}" },
      "enabled": true
    },
    "figma": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-figma"],
      "env": { "FIGMA_ACCESS_TOKEN": "${FIGMA_TOKEN}" },
      "enabled": false
    }
  }
}
```

### 8.6.3 Auditing Tool Use

Periodically audit which MCP tools your agents actually invoke. Most teams find that:

- 20% of enabled tools account for 80% of actual calls
- Several servers are enabled but never used in practice
- Some tools can be replaced by simpler file reads with no loss in quality

Claude Code's session logs record every tool call. Review them after a sprint to identify unused tools and disable the corresponding servers.

---

## 8.7 Putting It Together: A Configured Agent Workspace

A well-configured agent workspace looks like this:

```
project-root/
├── AGENTS.md                        ← Cross-tool context: stack, conventions, constraints
├── .claude/
│   ├── settings.json                ← MCP servers (only what this project needs)
│   ├── agents/
│   │   ├── code-reviewer.md         ← Read-only, Opus, maxTurns: 20
│   │   ├── test-runner.md           ← Execute, Sonnet, maxTurns: 30
│   │   └── db-migrator.md           ← Write, Sonnet, maxTurns: 15
│   └── skills/
│       ├── security-review/
│       │   └── SKILL.md
│       ├── db-migration/
│       │   ├── SKILL.md
│       │   └── migration_template.sql
│       └── release-checklist/
│           └── SKILL.md
└── src/
    ├── api/
    │   └── CLAUDE.md                ← API-specific context
    └── workers/
        └── CLAUDE.md                ← Worker-specific context
```

Each layer serves a distinct purpose:

| Layer | What it controls | Changes how often |
|---|---|---|
| `AGENTS.md` | What the agent knows | When conventions change |
| `settings.json` | What tools the agent can reach | When new integrations are added |
| `agents/*.md` | What specialised agents can do | When roles are defined or refined |
| `skills/*.md` | How specific tasks are performed | When processes are improved |
| Nested `CLAUDE.md` | Module-specific conventions | When module conventions change |

---

## 8.8 Summary

Effective agent configuration is not boilerplate — it is engineering. The decisions you make about what context to provide, what tools to allow, and how to scope subagents directly determine the quality and safety of what your agents produce.

The key ideas from this chapter:

- **`AGENTS.md`** is the cross-tool standard for giving agents project context. It works across Claude Code, Cursor, Codex CLI, Gemini CLI, and others. Treat it as living documentation.
- **Subagents** are specialised agents with explicit model selection, tool allowlists, permission modes, and turn limits. Apply the principle of least privilege: give each subagent only what it needs.
- **Skills** are deterministic, curated knowledge injections — not retrieval. They encode process knowledge (how your team does a specific type of task) and are invoked by slash commands.
- **MCP servers** connect agents to external tools. They enable genuinely autonomous workflows across the full engineering lifecycle.
- **Token cost is real.** Each MCP tool description consumes context. Enable only what is needed for the current project; audit usage regularly.

---

## Tutorial Activity: Configuring an Agent Workspace

In this activity, you will configure a complete agent workspace for the course project you specified in Chapter 5.

### Part A: Write Your `AGENTS.md`

Create an `AGENTS.md` file at the root of your course project repository. It should include:

1. A one-paragraph description of the project (domain, users, purpose)
2. The technology stack and key directory structure
3. The commands to build, run tests, lint, and type-check
4. At least four team conventions (naming, commit style, PR process, etc.)
5. At least three explicit constraints ("never do X")

### Part B: Define a Subagent

Create `.claude/agents/code-reviewer.md` for your project. Configure it with:

- `model`: `claude-opus-4-7` (full review capability)
- `tools`: read-only tools only (no write or execute)
- `permission_mode`: `read_only`
- `maxTurns`: `15`
- A description of what the reviewer should check, specific to your project's language and framework

### Part C: Create a Skill

Create `.claude/skills/test-generation/SKILL.md` that describes your team's process for writing tests:

- Which testing framework and libraries you use
- The conventions for test file naming and placement
- The types of test cases always required (happy path, edge cases, error cases)
- Any mocking or fixture conventions specific to your project

### Part D: Evaluate Token Cost

List the MCP servers you would realistically use for your course project. For each:

1. State what workflow it enables
2. Estimate the number of tools it exposes
3. Estimate the token cost per interaction
4. Decide whether the benefit justifies the cost for a student project (with limited API budget)

Justify your final list of enabled MCP servers.

### Reflection Questions

1. What information in your `AGENTS.md` would you not have known to write before taking this course?
2. What is the difference between putting a convention in `AGENTS.md` and creating a Skill for it?
3. A teammate proposes enabling 12 MCP servers "so the agent can do everything." How would you respond?
4. Which subagent permission mode would you use for a subagent that needs to run tests but should not be able to push code to GitHub? Why?

---

## Further Reading

- Anthropic. (2024). *Model Context Protocol specification*. [https://modelcontextprotocol.io](https://modelcontextprotocol.io)
- Anthropic. (2024). *Claude Code documentation: Subagents*. Anthropic Developer Docs.
- Anthropic. (2024). *Claude Code documentation: Skills*. Anthropic Developer Docs.
- Weng, L. (2023). LLM-powered autonomous agents. *Lil'Log*. [https://lilianweng.github.io/posts/2023-06-23-agent/](https://lilianweng.github.io/posts/2023-06-23-agent/)
- Shinn, N., Cassano, F., Labash, A., Gopalan, A., Narasimhan, K., & Yao, S. (2023). Reflexion: Language agents with verbal reinforcement learning. *Advances in Neural Information Processing Systems, 36*. -->
