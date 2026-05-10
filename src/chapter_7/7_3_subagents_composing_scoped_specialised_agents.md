## 7.3 Subagents: Composing Scoped, Specialised Agents

### 7.3.1 Why Subagents

A single general-purpose agent can handle many tasks, but it has limitations:

- It must operate within a single permission boundary — either all tools are allowed or none are
- Long tasks risk hitting context limits, with early context "falling out" of the window
- There is no way to run tasks in parallel unless multiple agent instances are launched
- A bug-fixing agent and a deployment agent should not have the same permissions

*Subagents* address these problems. A subagent is a specialised agent, with its own model, tool allowlist, and permission mode, that can be invoked by an orchestrator agent to handle a specific kind of work.

Claude Code implements subagents via Markdown definition files in `.claude/agents/`.

### 7.3.2 Subagent Definition Files

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

### 7.3.3 Configuration Parameters

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

### 7.3.4 Background Tasks

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
