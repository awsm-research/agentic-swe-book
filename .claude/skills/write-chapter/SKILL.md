# Skill: write-chapter

Invoked as: `/write-chapter`

## Purpose

Draft a new chapter of the book *Agentic Software Engineering: A Practical Guide for the AI-Native Engineer* — matching the established tone, structure, and style of Chapter 1.

---

## Book Context

**Title:** Agentic Software Engineering: A Practical Guide for the AI-Native Engineer
**Audience:** Advanced undergraduates and graduate students in software engineering; practising engineers transitioning to AI-assisted workflows. Readers know programming fundamentals but may be new to rigorous software engineering practice.
**Publisher's voice:** Academic rigour without academic distance. Direct, opinionated, grounded in real consequences.

**Part structure (from SUMMARY.md):**
- Part I: SE Fundamentals — Chapters 1–5 (foundations before AI)
- Part II: Agentic Software Engineering — Chapters 6–9 (AI-native practice)
- Part III: Engineering with Responsibility — Chapters 10–12

---

## Chapter Structure Template

Every chapter follows this exact skeleton, in this order:

```
# Chapter N: Title

> *"Opening quote."*
> — Attribution

---

[Hook paragraph — a specific real-world incident or concrete problem, 3–5 sentences. No sweeping universals. No "this chapter asks".]

---

## Learning Objectives

By the end of this chapter, you will be able to:

1. [Verb] ...
2. [Verb] ...
(4–6 objectives, measurable, specific to this chapter)

---

## N.1 First Section Title

[Content]

### Subsection Title (unnumbered)
[Content]

---

## N.2 Second Section Title
...

## N.X Key Takeaways

1. **Bold lead.** Explanation sentence.
2. ...
(6–10 takeaways)

---

## Review Questions

1. [Scenario-based question]
2. ...
(4–6 questions)

---

## Further Reading

- Author. (Year). *Title*. [url](url)
```

**Separator rules:**
- `---` after the opening hook paragraph
- `---` after Learning Objectives
- `---` between every `## N.X` top-level section
- `---` between Key Takeaways and Review Questions
- `---` between Review Questions and Further Reading

---

## Section Numbering Convention

- `## N.X` — top-level sections (e.g., `## 2.1 What Is a Requirement?`)
- `### N.X.Y` — numbered subsections only when the section has 3+ substantial sub-topics
- `### Subsection Title` — unnumbered subsections for groupings within a section
- Never skip levels — `###` only appears under `##`, `####` is not used

---

## Tone Rules

**Do:**
- Open with a specific, documented real-world incident, not a sweeping claim
- Take positions — say what the better approach is, not just "it depends"
- Use concrete failure consequences (dollar amounts, specific dates, named organisations)
- Name people: Fred Brooks, Margaret Hamilton, Linus Torvalds, Kent Beck — with dates and context
- Use Australian examples where well-documented (MYKI, CBA, NDIS) — frame them as patterns, not anomalies
- Vary sentence length: short declarative sentences after complex ones
- Use em dashes — like this — for parenthetical remarks (with spaces)
- Use *italics* for key terms on first introduction in a sentence
- Use **bold** for terms being formally defined or in definition tables

**Do not:**
- Open with "In today's world..." / "Every X you use today..." / "In the age of AI..." — these are AI tells
- Write "This chapter asks:" or "In this chapter, we will explore" — announce nothing
- Use the construction "X sounds simple. In practice, it is Y" — cut it
- Write "Both are X. Y and Z" balanced fence-sitting — take a side
- Use three perfectly parallel sentences that say the same thing three ways
- Write "It is important to note that..." / "It is worth mentioning..." — just say it
- End sections with "This is why X matters as a discipline" or similar moral closers — show consequences instead
- Write "X is not merely Y" as an opener — AI tells
- Use "In practice" more than once per section
- Summarise what was just said in the paragraph that follows it

---

## Language and Localisation

Australian/British English throughout:
- organisation (not organization)
- programme (not program, except for computer programs)
- behaviour, colour, favour, recognise, analyse
- artefact (not artifact)
- whilst is acceptable but not preferred; use "while"
- licence (noun), license (verb)

---

## Structural Elements

### Opening Quote
A real quote from a practitioner or researcher directly relevant to the chapter's central claim. Format:
```
> *"Quote text."*
> — Name, Context/Year
```

### Hook Paragraph
A specific incident — ideally named, dated, and with a dollar figure or consequence. 3–5 sentences. End on the implication for the chapter's content, not a thesis statement. Never reference "this book" or "this chapter" in the hook.

### Learning Objectives
Numbered list. Each begins with an action verb (Explain, Compare, Design, Identify, Apply, Distinguish). 4–6 objectives. Each must be testable — a student should be able to know whether they can do it.

### Tables
Use for: comparisons (two or more things side by side), definition glossaries, model/pattern overviews, lesson summaries.
Format: `| Column | Column |` with `|---|---|` separator row. Bold the left column for definition tables.

### Code Blocks
Use fenced code blocks with language identifiers. For ASCII diagrams, use plain ` ``` ` with no language.

### Images
```markdown
![Descriptive alt text](images/chapter-N-descriptive-name.png)
```
Follow immediately with an italic caption only for photographs: `*Caption text.*`
Do not add captions to diagrams — the alt text and surrounding prose are sufficient.

Image filename convention: `chapter-N-topic-name.png` (lowercase, hyphenated).

### Case Studies
Format as `### Case Study N: Name` subsections under a `## N.X When X Fails` or similar section.
Each case study ends with a bullet list of 3–4 failure patterns labelled in bold.
Follow all case studies with a `### Lessons from Failures` table.

### Key Takeaways
Numbered list. Each entry: `**Bold lead phrase.** One or two sentences of explanation.`
Vary the construction — not every entry should follow identical rhythm.
6–10 items.

### Review Questions
4–6 questions. Every question must be scenario-based or require application — no "define X" or "list the Y attributes of Z". Students should need to reason, not recall.

Good pattern: "A [role] [scenario]. [What would you do / what went wrong / how would you evaluate]?"

### Further Reading
Academic citations in APA-adjacent style: `Author, A. (Year). *Title*. Publisher/URL`
Hyperlink URLs in markdown: `[text](url)`. 4–8 references.

---

## Process

When invoked with a chapter number and title (e.g., `/write-chapter 2 Requirements Engineering`):

1. Read `src/SUMMARY.md` to confirm the chapter's place in the book
2. Read `outline.md` to get the intended content list for this chapter
3. Read `src/chapter_1.md` as the style reference
4. If a prior chapter exists in `src/`, read it to check for concepts that should carry forward
5. Draft the full chapter following the template above
6. Check: does every `## N.X` section have a `---` before and after it?
7. Check: are there any AI-tell phrases (see Do Not list)?
8. Check: does every learning objective have a corresponding section that teaches it?
9. Write the file to `src/chapter_N.md`

Do not write the chapter to a temporary file or summarise it — write the full draft directly to the target file.
