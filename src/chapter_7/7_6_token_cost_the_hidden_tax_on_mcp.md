## 7.6 Token Cost: The Hidden Tax on MCP

### 7.6.1 How MCP Tools Consume Context

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

### 7.6.2 The Principle: Enable What You Need

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

### 7.6.3 Auditing Tool Use

Periodically audit which MCP tools your agents actually invoke. Most teams find that:

- 20% of enabled tools account for 80% of actual calls
- Several servers are enabled but never used in practice
- Some tools can be replaced by simpler file reads with no loss in quality

Claude Code's session logs record every tool call. Review them after a sprint to identify unused tools and disable the corresponding servers.

---
