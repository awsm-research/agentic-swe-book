## 7.4 Skills: On-Demand Knowledge Injection

### 7.4.1 The Retrieval Temptation

A common approach to giving agents specialised knowledge is *retrieval-augmented generation* (RAG): index a corpus of documents, embed the user's query, find the nearest neighbours in the vector space, and inject the matching chunks into the prompt.

RAG works well for large, unstructured corpora — customer support knowledge bases, research literature, product documentation. For software engineering tasks, it has a significant limitation: *semantic similarity is not the same as relevance*. The code chunk most similar to your query embedding may not be the code the agent actually needs. Retrieval introduces non-determinism: the same task may inject different context on different runs, producing inconsistent results.

### 7.4.2 What Skills Are

A *Skill* in Claude Code is a different mechanism. It is a curated, deterministic knowledge injection — a Markdown document that contains exactly the information an agent needs for a specific class of task, loaded on demand when a matching command is invoked.

When you type `/security-review` in Claude Code, a Skill file is loaded into the agent's context verbatim. No embedding. No retrieval. No probability. The exact content you wrote is what the agent receives.

The key properties of Skills:

- **Deterministic**: The same command always injects the same content
- **Curated**: A human engineer decides what goes in the Skill, not a retrieval algorithm
- **On-demand**: Content is only injected when explicitly invoked, not pre-loaded for every task
- **Composable**: Skills can invoke other Skills and spawn subagents

This makes Skills appropriate for *process knowledge* — how to perform a specific type of task — rather than *factual knowledge* — what something is. Use Skills for: "how we do code reviews on this team," "how we write database migrations," "our checklist for releasing to production." Use RAG (or context files) for: "what does this library's API look like," "what are the features of this third-party service."

### 7.4.3 Creating Custom Skills

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
```

The Skill directory can contain additional files — templates, checklists, example outputs — that the `SKILL.md` can reference or that the agent can read directly.

### 7.4.4 Invoking Skills

Skills are invoked using the slash command syntax in Claude Code:

```
/db-migration Add a not-null column for assignee_id to the tasks table
/security-review Review the authentication module
/release-checklist Prepare the v2.3.1 release
```

The Skill is loaded, the agent reads the instructions, and then applies them to the specific request. The result is a *structured, repeatable process* — the agent behaves like an engineer who has been trained in your specific workflows, not a general-purpose assistant guessing at conventions.

---
