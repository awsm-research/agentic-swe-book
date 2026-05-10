## 7.2 `AGENTS.md`: The Cross-Tool Context Standard

### 7.2.1 What It Is

`AGENTS.md` is a plain Markdown file, typically placed at the root of a repository, that describes your project to an AI coding agent. Think of it as the onboarding document you would write for a new engineer joining the team — except the new engineer reads it every time it starts a task.

The file is an emerging cross-tool standard. It is recognised by:

- **Claude Code** (reads `CLAUDE.md` or `AGENTS.md`)
- **Cursor** (reads `.cursor/rules` and `AGENTS.md`)
- **OpenAI Codex CLI** (reads `AGENTS.md`)
- **Gemini CLI** (reads `AGENTS.md`)
- **GitHub Copilot Workspace** (reads `AGENTS.md`)

Using a standard filename means the same instructions apply consistently regardless of which tool your team members use. You write the context once; every agent respects it.

### 7.2.2 What to Put in It

A well-structured `AGENTS.md` answers five questions:

1. **What is this project?** — One paragraph on the domain, the users, and the business purpose.
2. **How is it structured?** — Key directories, the technology stack, and the data flow at a high level.
3. **How do I build and test it?** — The exact commands to build, run tests, check types, and lint.
4. **What are the conventions?** — Naming, code style, commit message format, branch strategy.
5. **What should I never do?** — Explicit constraints: things that will break production, violate policy, or require human sign-off.

````markdown
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
- Never use `--autogenerate` for data migrations — write those manually
- Never drop a column without confirming it is not in use in the application code
````

---
