## 7.8 Key Takeaways

How an agent is configured is as consequential as the code it generates. The decisions you make about context, permissions, and tool access determine both what the agent can produce and what it cannot accidentally break:

1. **`AGENTS.md`** is the cross-tool standard for giving agents project context. It works across Claude Code, Cursor, Codex CLI, Gemini CLI, and others. Treat it as living documentation.
2. **Subagents** are specialised agents with explicit model selection, tool allowlists, permission modes, and turn limits. Apply the principle of least privilege: give each subagent only what it needs.
3. **Skills** are deterministic, curated knowledge injections — not retrieval. They encode process knowledge (how your team does a specific type of task) and are invoked by slash commands.
4. **MCP servers** connect agents to external tools. They enable genuinely autonomous workflows across the full engineering lifecycle.
5. **Token cost is real.** Each MCP tool description consumes context. Enable only what is needed for the current project; audit usage regularly.

---

### Review Questions

1. A junior engineer joins your team and asks why the agent keeps using the wrong testing framework. Using the concept of context files, diagnose what is likely missing and describe what you would write to fix it.

2. You are designing a subagent that must read the database schema and generate migration scripts, but must not execute any SQL directly. Which `permission_mode` would you choose, and which tools would you include in the allowlist? Justify each decision.

3. Your team enables 15 MCP servers "so the agent can do everything." A month later, engineers complain that the agent is slower and produces lower-quality output on complex tasks. Using what you know about token cost and context windows, explain what is happening and propose a remedy.

4. A colleague argues that putting a convention in `AGENTS.md` and creating a Skill for it accomplish the same thing. Where do they overlap, and where do they fundamentally differ? Give an example where only one of the two approaches is appropriate.

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

---
