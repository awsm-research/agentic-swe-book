# Skill: write-tutorial

Invoked as: `/write-tutorial`

## Purpose

Draft a new tutorial for *Agentic Software Engineering: A Practical Guide for the AI-Native Engineer* — matching the established tone, structure, and style of Tutorial 1.

---

## Book Context

**Title:** Agentic Software Engineering: A Practical Guide for the AI-Native Engineer
**Audience:** Advanced undergraduates and graduate students in software engineering; practising engineers transitioning to AI-assisted workflows. Readers know programming fundamentals but may be new to rigorous software engineering practice.
**Publisher's voice:** Academic rigour without academic distance. Direct, opinionated, grounded in real consequences.

Tutorials are hands-on lab sessions that accompany chapters. They are distinct from chapters: no opening quote, no Key Takeaways, no Review Questions. The student leaves with working tools and a completed task, not just knowledge.

---

## Tutorial Structure Template

Every tutorial follows this exact skeleton, in this order:

```
# Tutorial N: Title

[Opening paragraph — 2–4 sentences framing the concrete problem this tutorial solves. No sweeping universals. No "in this tutorial". End on what the student will have set up.]

**Concepts covered:** [comma-separated list of tools and concepts practiced]

**Format:** [Individual / Pairs / Team] | **Duration:** [total time] | **Tool:** [comma-separated tool list]

---

## Outline

- [Part A: Title](#part-a-anchor)
- [Part B: Title](#part-b-anchor)
- [Part C: Title](#part-c-anchor) (if applicable)
- [References](#references)

---

## Learning Objectives

By the end of this tutorial, you will be able to:

1. [Verb] ...
(4–6 objectives, measurable, tied to the hands-on steps)

---

## Part A: Title *(~XX min)*

[1–2 sentence framing of what this part achieves.]

### Prerequisites

- [Tool] ([link](url)) — one-line purpose
- ...

---

### Step 1: Title

#### What Is X? (optional — include when a tool or concept needs justification before use)

[Explain the concept or tool. Include a comparison table if the student has likely used an inferior or different alternative. End with a direct recommendation.]

[Instructions. Use second-person imperative: "Run the following command", "Create the file", "Navigate to Settings".]

```bash
# commands
```

> **Tip/Note/Warning:** [Callout text. Use sparingly — one per step at most.]

---

### Step N: Title
...

### Step N: Activity — [Verb] [Task]

[1–2 sentence setup.]

1. [Concrete instruction]
2. ...
N. Verify with:

```bash
[verification command]
```

---

## Part B: Title *(~XX min)*

[1–2 sentence framing.]

### What Is X? (optional)

[Concept explanation, motivation, comparison table.]

---

### [Task title — not numbered in Part B if it's a single configuration sequence]

[Step-by-step instructions.]

---

## Part C: Title *(~XX min)* (if needed)

...

---

## References

- [Title](url) — one-line description of what it covers
```

**Time estimate rules:**
- The time estimates on each part heading must sum exactly to the total Duration in the metadata line.
- Part with the most hands-on steps (coding, CLI commands, activity) gets the most time.
- Configuration-only parts (UI settings, no coding) get less time.

---

## Structural Elements

### Opening Paragraph
No heading. 2–4 sentences. States the concrete problem (what is missing or broken without this setup) and what the student will have working by the end. Never says "this tutorial covers" or "in this tutorial". No quote.

### Concepts Covered Line
One line: `**Concepts covered:** concept, concept, concept`. Derived from the learning objectives and the tools used. List 5–10 items.

### Format / Duration / Tool Line
`**Format:** Individual or pairs | **Duration:** X hours | **Tool:** Tool1, Tool2`

### Outline
A flat bulleted list with anchor links matching the part headings. Include Parts and References only — no step-level links.

### Learning Objectives
4–6 objectives beginning with action verbs (Create, Configure, Write, Run, Explain, Verify, Link). Must be achievable by following the tutorial, not just reading it. Each maps to at least one step.

### Part Headings
`## Part A: Title *(~XX min)*` — italic time estimate in parentheses. Three parts maximum. If a tutorial needs more, split into two tutorials.

### What Is X? Sections
Use when introducing a tool the student has likely not used, or when the student may reach for a worse alternative. Structure:
1. State the problem the tool solves (1–2 sentences).
2. Explain the tool and its advantages, with a comparison table against the obvious alternative.
3. Close with a direct recommendation: "For [use case] in [year], [tool] is the recommended starting point."

Do not write "What Is X?" sections for tools already explained in a prior tutorial or chapter.

### Step Headings
`### Step N: Title` — numbered sequentially within each Part, resetting at each new Part.

### Code Blocks
Fenced with a language identifier (`bash`, `python`, `toml`, `yaml`, `markdown`). Include a comment on the same line as commands where the purpose is not obvious. For expected terminal output, use a plain fenced block with no language:
```
expected output here
```

### Callouts
`> **Tip:** text` / `> **Note:** text` / `> **Warning:** text`
Use for non-obvious constraints, gotchas, or important caveats. Maximum one callout per step. Do not use callouts to summarise what the prose just said.

### Comparison Tables
`| Feature | Old tool | New tool |` with `|---|---|---|`. Use for tool comparisons in "What Is X?" sections. Bold the feature column. Keep to 6 rows maximum.

### Activity Steps
Name the last step in each Part `### Step N: Activity — [Verb] [Task]`. The activity asks the student to extend or apply what they built in earlier steps — not repeat them. Must include a verification command so the student can confirm success.

### References
Bulleted list at the end of the tutorial. Format: `- [Section title or doc title](url) — one-line description`. Link to the official documentation page for each tool used, and to any GitLab feature pages covered. 4–8 references.

---

## Comparison Tables for Common Tools

When writing "What Is X?" sections, use these established comparisons from Tutorial 1 as a style reference — do not copy them verbatim, but follow the same column structure and directness.

**pip vs uv pattern:** rows for Install packages / Create virtual environments / Lockfile / Manage Python versions / Project scaffold / Speed. End with: "For a new project in [year], [tool] is the recommended starting point."

---

## Tone Rules

**Do:**
- Use second-person imperative for instructions: "Run", "Create", "Navigate to", "Click"
- Explain *why* a step matters before giving the command
- Show expected output for verification commands
- Use concrete tool versions and URLs (e.g., `uv 0.6.x`, `pre-commit v4.6.0`)
- Take a position on tools: say which is better and why, not "both have trade-offs"
- Use Australian/British English (organisation, behaviour, artefact, recognise)

**Do not:**
- Open with a definition ("Git is a version control system…")
- Open with "In this tutorial, we will…" or "This tutorial covers…"
- Write "It is important to note that…" — just say it
- Use "In practice" more than once per section
- Summarise what was just said in the following sentence
- Add steps that do not map to a learning objective
- Invent tool versions or flags — use what is current and verifiable

---

## Process

When invoked with a tutorial number and title (e.g., `/write-tutorial 2 Testing with pytest`):

1. Read `src/SUMMARY.md` to confirm the tutorial's place in the book and which chapter it accompanies
2. Read `src/tutorial_1.md` as the structural and style reference
3. Read the chapter the tutorial accompanies (`src/chapter_N.md`) to understand which concepts need hands-on reinforcement
4. Read `summary.md` if a tutorial outline exists for this number
5. Draft the full tutorial following the template above
6. Check: do the part time estimates sum to the total Duration?
7. Check: does every learning objective map to at least one step?
8. Check: does every Part end with an Activity step?
9. Check: are there any AI-tell phrases (see Do Not list)?
10. Write the file to `src/tutorial_N.md`

Do not write the tutorial to a temporary file or summarise it — write the full draft directly to the target file.
