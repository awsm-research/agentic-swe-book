## 7.7 Putting It Together: A Configured Agent Workspace

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
