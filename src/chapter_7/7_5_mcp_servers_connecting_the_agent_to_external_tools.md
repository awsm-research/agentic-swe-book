## 7.5 MCP Servers: Connecting the Agent to External Tools

### 7.5.1 The Model Context Protocol

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

### 7.5.2 Categories of MCP Servers

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

### 7.5.3 Configuring MCP in Claude Code

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

### 7.5.4 What Agents Can Do with MCP

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
