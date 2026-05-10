# Chapter 7: Configuring the Agent's World — Context, Skills, and Tools

> *"An agent is only as good as the world it can see. What you choose to put in front of it — and what you keep out — is an engineering decision, not a configuration detail."*
> — Kla Tantithamthavorn

---

Within twelve months of Anthropic releasing the Model Context Protocol in November 2024, the open MCP registry listed thousands of community-built servers — integrations for issue trackers, databases, design tools, observability platforms, and internal APIs that teams had wired to their agents because the agents needed them to work. The Everything Claude Code project, a community-maintained library of reusable agent skills, catalogued hundreds of specialised workflows: security review, database migration, CI/CD orchestration, code review, deployment checklists — process knowledge that teams had encoded so their agents would stop guessing at conventions. The `AGENTS.md` format — a plain Markdown file describing a project's stack, commands, and constraints — had been adopted as a shared cross-tool standard by Claude Code, Cursor, OpenAI's Codex CLI, and Gemini CLI before any single organisation had formally standardised it. Engineers did not build all of this because agents worked correctly by default. They built it because an unconfigured agent, dropped into a production codebase, makes its best guesses — and in engineering organisations, best guesses accumulate into incidents.

---
