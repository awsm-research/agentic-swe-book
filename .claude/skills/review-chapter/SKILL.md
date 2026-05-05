# Skill: review-chapter

Invoked as: `/review-chapter`

## Purpose

Review a chapter or tutorial of *Agentic Software Engineering: A Practical Guide for the AI-Native Engineer* from three independent critical perspectives, then produce a prioritised list of concrete improvements.

---

## Mode Detection

- If the target file is `tutorial_N.md` → use **Tutorial Mode** (see below)
- If the target file is `chapter_N.md` → use **Chapter Mode** (see below)

---

## Chapter Mode

### Process

When invoked with a chapter file (e.g., `/review-chapter src/chapter_2.md`):

1. Read the target chapter file in full
2. Read `src/chapter_1.md` as the established style baseline
3. Read `summary.md` to confirm the chapter's intended content scope
4. Run all three reviews independently (do not let one perspective soften another)
5. Produce a consolidated report followed by an edit plan
6. Apply the high-priority edits directly to the chapter file

---

### Reviewer 1: The Publisher (Chapter)

**Role:** Senior acquisitions editor at a technical academic press. Cares about market fit, reader experience, pedagogical coherence, and whether the book will hold up in a university course and sell beyond it.

**What to check:**

- **Hook** — Does the chapter open with something a reader would actually want to read? Or does it start with a definition, a sweeping claim, or a meta-announcement ("in this chapter we will…")?
- **Learning objectives** — Are they measurable and specific? Can a student genuinely know whether they achieved each one? Are they all actually taught in the chapter?
- **Scope** — Does the chapter cover what `summary.md` promises? Is anything promised but missing? Is anything present that belongs in a different chapter?
- **Pedagogical flow** — Does each section build on the last? Would a student who reads linearly be able to follow?
- **Case studies** — Are real incidents used? Are they cited? Are they recent enough to be credible? Do they connect to the section's claim, or are they decorative?
- **Review questions** — Are they scenario-based (require reasoning) or recall-based (require memorisation)? At least 80% should require reasoning.
- **Further reading** — Are references current, authoritative, and hyperlinked? Are they actually worth reading, or filler?
- **Structure** — Are `---` separators consistent? Is section numbering correct (N.X for top-level, N.X.Y for subsections with 3+ topics)?
- **Markdown hygiene** — Are links formatted correctly `[text](url)`? Are images using `![alt](path)` format? Are any raw URLs or broken link formats present?
- **Length** — Is the chapter proportionate? Are any sections far too long or suspiciously thin?

---

### Reviewer 2: The Professor (Chapter)

**Role:** Associate Professor in Software Engineering with 15 years of teaching undergraduate and postgraduate courses. Cares about academic accuracy, appropriate depth, alignment with canonical literature, and whether students can actually learn from this.

**What to check:**

- **Technical accuracy** — Are all claims correct? Are dates, names, and attributions accurate? Is the Waterfall model correctly attributed to Royce (who criticised it)? Is the Agile Manifesto's year correct (2001)? Are tool names and version numbers current?
- **Completeness vs. outline** — Does the chapter cover all topics listed for this chapter in `summary.md`? Flag anything missing, not just things that are wrong.
- **Conceptual depth** — Are important concepts explained at the right level, or glossed over? A chapter on requirements that doesn't distinguish functional from non-functional requirements has a gap. A chapter on testing that doesn't mention coverage has a gap.
- **Learning objective alignment** — Map each learning objective to the section that teaches it. Flag any objective with no corresponding content.
- **Citation quality** — Are canonical sources cited (Sommerville, Brooks, Pressman, Beck, Fowler)? Are citations properly formatted? Are any claims made without evidence that should have one?
- **Definitions** — Are key terms defined on first use? Are definitions accurate and not circular?
- **Examples** — Are examples concrete and domain-appropriate? Do they work as examples, or are they so simplified they mislead?
- **AI angle** — For Part I chapters (1–5), is the AI angle mentioned but kept brief? For Part II chapters (6–9), is the engineering discipline rigorous and not just a feature tour?
- **Consistency with Chapter 1** — Are concepts introduced in Chapter 1 (SDLC, PPT model, Waterfall, Agile, maintenance dominance) referenced correctly when they appear in later chapters?

---

### Reviewer 3: The Anti-AI Critic (Chapter)

**Role:** A senior engineering writer who is deeply sceptical of AI-generated content. Has read thousands of AI-produced documents and can identify the patterns instantly. Does not care about being polite.

**What to check — the AI tell inventory:**

**Structural AI tells:**
- Does every section have the same internal structure (definition → bullet list → table → summary paragraph)? Mechanical uniformity is an AI fingerprint.
- Are bullet lists used where prose would be clearer? AI defaults to lists because they look organised.
- Are there exactly three items in every list? AI loves triads.
- Does every table summarise what the prose just said? Redundant tables are AI padding.

**Sentence-level AI tells (flag every instance):**
- "X sounds simple. In practice, it is Y."
- "Both X and Y are valuable / important / necessary."
- "It is important to note that…" / "It is worth mentioning…"
- "X is not merely Y — it is Z."
- "This chapter asks: …" / "In this chapter, we will explore…"
- "In today's world…" / "In the age of X…" / "Every X you use today…"
- "The best X cannot compensate for poor Y. Excellent Y cannot succeed without Z." (parallel platitude triad)
- "This is why X matters as a discipline." / "X is both an aspiration and a responsibility."
- Three perfectly parallel negative constructions in a row
- Ending a section with a moral closer ("ultimately," "at its core," "in the final analysis")
- "In practice" used more than once in a section

**Voice AI tells:**
- No authorial opinions — the text is so balanced it has no point of view
- Hedging everything with "may," "might," "can often," "in many cases" when a direct claim would be defensible
- Describing two opposing views without saying which is better
- Generic examples that could appear in any software engineering textbook (a to-do app, a library system, a shopping cart) — no specific named projects, organisations, or incidents

**Hook AI tells:**
- Opens with a definition
- Opens with a sweeping universal ("Software is at the heart of…")
- Opens with a rhetorical question ("What does it mean to engineer software?")
- Opens with a quote, then immediately explains what the quote means instead of letting it land

---

## Tutorial Mode

### Process

When invoked with a tutorial file (e.g., `/review-chapter src/tutorial_2.md`):

1. Read the target tutorial file in full
2. Read `src/tutorial_1.md` as the established style baseline
3. Read the chapter the tutorial accompanies (e.g., `src/chapter_2.md`) to verify the tutorial reinforces the right concepts
4. Read `summary.md` if a tutorial entry exists there
5. Run all three reviews independently
6. Produce a consolidated report followed by an edit plan
7. Apply the high-priority edits directly to the tutorial file

---

### Reviewer 1: The Publisher (Tutorial)

**Role:** Senior acquisitions editor. For tutorials, cares about whether a student can follow the steps without the instructor present, whether the pacing feels right, and whether the tutorial delivers a tangible result.

**What to check:**

- **Opening paragraph** — Does it state the concrete problem and what the student will have working by the end? Does it avoid "this tutorial covers" or "in this tutorial"? No opening quote — flag if one is present.
- **Metadata lines** — Is the `**Concepts covered:**` line present and accurate? Is the `**Format / Duration / Tool:**` line present?
- **Outline** — Are all Parts listed with working anchor links? Do the anchor slugs match the actual part headings?
- **Learning objectives** — Are they tied to hands-on steps, not just reading? Action verbs must be achievable (Create, Configure, Run, Verify — not Understand, Appreciate, Explore).
- **Part time estimates** — Do the `*(~XX min)*` estimates on each Part heading sum to the total Duration in the metadata? Flag if not.
- **Part endings** — Does each Part end with an Activity step (`### Step N: Activity — …`)? Flag any Part missing one.
- **Step numbering** — Are steps numbered within each Part and reset at each new Part (Part A Step 1, Step 2…; Part B Step 1, Step 2…)?
- **"What Is X?" sections** — Are they only present for tools the student has genuinely not seen? Flag any that explain tools already covered in Tutorial 1 or the accompanying chapter.
- **Activity steps** — Do they ask the student to extend or apply what was built, not merely repeat it? Does each include a verification command?
- **References** — Present? One link per major tool used? Links go to official documentation, not blog posts?
- **Forbidden elements** — Flag the presence of: opening quote, Key Takeaways section, Review Questions section, Further Reading section. Tutorials must not have these.
- **Markdown hygiene** — Correct `[text](url)` links, `![alt](path)` images, fenced code blocks with language identifiers.

---

### Reviewer 2: The Professor (Tutorial)

**Role:** Associate Professor who runs the lab sessions. Cares about whether commands actually work, whether students will get stuck, and whether the tutorial genuinely reinforces the chapter's learning objectives.

**What to check:**

- **Step–objective alignment** — Map each learning objective to the step(s) that teach it. Flag any objective with no corresponding step.
- **Command accuracy** — Are all shell commands syntactically correct? Are flag names and argument orders accurate for the tool versions referenced? Are file paths consistent throughout?
- **Expected outputs** — Are expected terminal outputs shown after verification commands? Are they realistic (not idealised)?
- **"What Is X?" accuracy** — Are comparison tables fair? Are the claims about tool advantages accurate and current? Is the recommendation defensible for the stated year?
- **Prerequisites** — Are all required tools listed in the Prerequisites section with working links? Would a student following only the prerequisites be able to complete Step 1?
- **Activity achievability** — Can the activity be completed using only what was introduced in the current tutorial? Flag if it requires knowledge not yet taught.
- **Tool currency** — Are recommended tools current for 2025? (e.g., `uv` over `pip`, `pre-commit` v4.x). Flag outdated recommendations.
- **Consistency with Tutorial 1** — Are tools introduced in Tutorial 1 (uv, pre-commit, Git) referenced correctly and not re-explained?

---

### Reviewer 3: The Anti-AI Critic (Tutorial)

**Role:** A senior technical writer who has reviewed hundreds of AI-generated tutorials. Knows exactly what they look like. No diplomacy.

**What to check — the AI tell inventory:**

**Structural AI tells:**
- Every step has the same internal structure (explanation → code block → callout) — mechanical uniformity across all steps is a fingerprint.
- Callouts (`> **Tip:**`, `> **Note:**`) appear on every step — AI adds them reflexively. Maximum one per step; not every step needs one.
- "What Is X?" section written for a tool the student already knows — AI pads word count by re-explaining basics.
- Activity step merely asks the student to run the same commands again with different values — AI activity steps are often trivially easy.
- Every code block followed by an explanation sentence that restates what the code does — AI cannot resist narrating.

**Sentence-level AI tells (flag every instance):**
- "It is important to note that…" / "It is worth mentioning…"
- "In practice" used more than once in a section
- "Now that you have X, it is time to Y." — AI transition filler between steps
- "This ensures that…" / "This allows you to…" — AI padding after a command block
- "This tutorial covers…" / "In this tutorial, we will…" — opening tells
- "By the end of this step, you will have…" at the start of every step
- "In today's development environment…" / "In modern software teams…"

**Voice AI tells:**
- Instructions give commands with no rationale — no "why" anywhere
- Or the inverse: every obvious command over-explained
- Example code is domain-generic (a calculator, a to-do list, a "hello world" wrapper) when a domain-specific example would serve the learning objective better
- The "bad example" in a table is cartoonishly bad and the "good example" is cartoonishly perfect — no nuance

---

## Report Format

For both modes, produce the review in this exact format (substituting "Tutorial N" for "Chapter N" as appropriate):

```
## Review: [Chapter/Tutorial] N — [Title]

---

### Publisher's Verdict
[2–3 sentence overall assessment. Be direct.]

**Critical issues (fix before publication):**
- [Issue]: [Specific location or example] → [What to do]

**Improvements (fix before final draft):**
- [Issue]: [Specific location or example] → [What to do]

---

### Professor's Verdict
[2–3 sentence overall assessment.]

**Critical issues (accuracy / completeness):**
- [Issue]: [Specific claim or missing content] → [What the correct content should be]

**Improvements (depth / alignment):**
- [Issue]: [Section or objective] → [What to add or change]

---

### Anti-AI Critic's Verdict
[2–3 sentence overall assessment. No diplomacy.]

**AI tells found (fix all of these):**
- Line ~N: "[Exact offending phrase]" → [Suggested rewrite or delete]

**Voice problems:**
- [Description of the broader voice problem] → [How to fix]

---

### Consolidated Edit Plan

Priority 1 — Fix immediately (accuracy, broken links, missing content, AI tells):
1. [Specific edit]
2. ...

Priority 2 — Fix before next draft (structure, depth, flow):
1. [Specific edit]
2. ...

Priority 3 — Consider for polish (style, variety, examples):
1. [Specific edit]
2. ...
```

---

## Edit Application Rules

After producing the report, apply all **Priority 1** edits directly to the file. For each edit:
- Make the minimum change that fixes the problem — do not rewrite surrounding prose
- Fix broken markdown links by converting `(text)[url]` → `[text](url)`
- Remove or rewrite every AI-tell phrase listed
- Do not add new sections without explicit instruction — flag missing content in the report, do not invent it

For **Priority 2 and 3** edits: list them in the report but do not apply them. The author decides whether to accept them.

---

## Do Not

- Do not soften the Anti-AI Critic's findings to spare feelings — every AI tell must be named
- Do not invent content to fill gaps — flag the gap and stop
- Do not apply Priority 2 or 3 edits without being asked
- Do not review a tutorial against chapter style conventions (no opening quote, no Key Takeaways, no Review Questions in a tutorial — these are correct absences, not gaps)
- Do not write "overall this is a good chapter/tutorial" if it has Priority 1 issues — fix them first
- Do not flag or modify GitLab feature availability callouts (e.g., `> **Availability:** … requires GitLab Premium or Ultimate`) — these are intentional editorial decisions
