## 7.1 The Agent Configuration Problem

When you first run a coding agent on a large codebase, it faces a fundamental problem: it can read any file, run any command, and potentially take any action — but it has no idea what it *should* do, what conventions to follow, what tools are sanctioned, or what parts of the system are off-limits.

Left unconfigured, an agent will make its best guesses. It may use a testing framework you abandoned two years ago, commit without signing, push to a branch that triggers a production deployment, or generate code in a style that conflicts with your team's standards. Agent failures that feel like AI limitations are usually configuration failures.

The central insight of this chapter is that configuring the agent's world is itself an engineering task. It requires the same rigour as writing code: deliberate decisions about what information the agent should have, what it is allowed to do, and what external systems it can reach.

Three mechanisms serve this purpose in modern agent tooling:

1. **Context files** (`AGENTS.md`, `CLAUDE.md`) — what the agent knows about your project
2. **Subagent definitions** — how agents are composed, scoped, and constrained
3. **Tools** — what external capabilities the agent can invoke

---
