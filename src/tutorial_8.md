# Tutorial 8: SAST, AI, and Human on Vulnerability Detection

A junior developer built a task-management REST API over the weekend. The code compiles and all unit tests pass. Three reviewers are about to look at it: a static analysis tool, an AI assistant, and you. Your job is to run both automated approaches, record what each finds, and apply your own judgement to determine what is real — then compare how well each approach did.

**Concepts covered:** SAST tools (Bandit, Semgrep), AI-assisted code review, true positives vs false positives, OWASP Top 10 mapping, CWE identifiers, cross-tool consistency

**Format:** Pairs or small groups | **Duration:** 2 hours | **Tool:** Python, Bandit, Semgrep, AI assistant (your choice)

---

## Outline

- [Phase 1: Setup](#phase-1--setup-10-min)
- [Phase 2: SAST Analysis](#phase-2--sast-analysis-15-min)
- [Phase 3: AI Analysis](#phase-3--ai-analysis-20-min)
- [Phase 4: Comparison Worksheet](#phase-4--comparison-worksheet-35-min)
- [Phase 5: Fix the True Positives](#phase-5--fix-the-true-positives-20-min)
- [Phase 6: Group Discussion](#phase-6--group-discussion-20-min)
- [Reference: Bandit Rule Codes](#reference-bandit-rule-codes)
- [References](#references)

---

## Learning Objectives

By the end of this tutorial you will be able to:

1. Run Bandit and Semgrep against a Python codebase and interpret their output.
2. Query an AI assistant to identify security vulnerabilities and record its findings systematically.
3. Apply human judgement to classify each finding as a true positive or false positive.
4. Compare what SAST tools, AI assistants, and human review each find — and what each misses.
5. Explain why consistency between tools does not guarantee correctness.

---

## Phase 1 — Setup *(~10 min)*

### Step 1: Install the SAST tools

The lab file is at `labs/ch08_vulnerable_app.py`. Install Bandit and Semgrep into a virtual environment:

```bash
python -m venv .venv && source .venv/bin/activate
pip install flask bandit semgrep
```

Verify:

```bash
bandit --version
semgrep --version
```

### Step 2: Declare your AI tool

Before running any analysis, record which AI assistant your group will use for Phase 3. Write it down — you will need it for the comparison worksheet.

| | Your entry |
|---|---|
| **AI tool used** | e.g., Claude, ChatGPT, GitHub Copilot Chat, Gemini |
| **Model / version (if shown)** | e.g., Claude Sonnet 4.6, GPT-4o |
| **Access method** | e.g., web interface, IDE extension, API |

You will use the same tool for all AI analysis in this tutorial. Do not switch mid-exercise.

---

## Phase 2 — SAST Analysis *(~15 min)*

Run each tool against the lab file and save the output so you can refer back to it.

**Bandit:**

```bash
# Medium-and-above severity, JSON output
bandit -r labs/ch08_vulnerable_app.py -ll -f json -o bandit_results.json

# Human-readable
bandit -r labs/ch08_vulnerable_app.py -ll
```

**Semgrep:**

```bash
semgrep --config=auto labs/ch08_vulnerable_app.py --json -o semgrep_results.json

# Human-readable
semgrep --config=auto labs/ch08_vulnerable_app.py
```

For each finding, note:
- Which tool reported it
- The rule ID (e.g., `B608`, `python.lang.security.audit.eval-detected`)
- The line number
- The reported severity

> **Tip:** Some findings appear in both tools; some in only one. Track which tool produced each finding — this matters in Phase 4.

### Step 3: Activity — List every SAST finding

Write out every finding from both tools before moving to Phase 3. You will add columns for AI and Human in Phase 4.

---

## Phase 3 — AI Analysis *(~20 min)*

Query your chosen AI assistant to independently review the same file. Do this **before** looking at the SAST output in detail — you want an independent assessment.

### Step 4: Prepare the AI prompt

Paste the full contents of `labs/ch08_vulnerable_app.py` into your AI tool with the following prompt:

```
You are a security engineer reviewing a Python Flask application for vulnerabilities.
For each security vulnerability you identify, provide:
1. The function name and line number (approximate is fine)
2. The vulnerability type (e.g., SQL injection, path traversal, command injection)
3. The CWE identifier if applicable (e.g., CWE-89)
4. One sentence explaining why it is vulnerable
5. One sentence describing the fix

Review the entire file systematically. Include both obvious vulnerabilities and subtle ones.
Do not skip findings because they look like they might be intentional.

[paste file contents here]
```

### Step 5: Activity — Record the AI findings

For each vulnerability the AI reports, write down:
- The function/location it identified
- The vulnerability type and CWE it named
- Whether it gave a rationale or just named the type

Also note anything the AI flagged that does not appear in the SAST output, and anything it explicitly said was safe.

---

## Phase 4 — Comparison Worksheet *(~35 min)*

Now bring together what SAST found, what AI found, and your own judgement. For every distinct finding reported by **any** source, complete one row of the comparison table.

### Step 6: Activity — Complete the three-way comparison table

Copy this table into a text file or spreadsheet:

```
| # | Location (fn / line) | Vulnerability Type | CWE | SAST? (tool) | AI? | Human Verdict | SAST Correct? | AI Correct? | Notes |
|---|----------------------|--------------------|-----|--------------|-----|---------------|---------------|-------------|-------|
| 1 |                      |                    |     |              |     | TP / FP       | Y / N         | Y / N       |       |
| 2 |                      |                    |     |              |     |               |               |             |       |
```

**Column guide:**

| Column | What to write |
|---|---|
| Location | Function name and approximate line number |
| Vulnerability Type | e.g., SQL Injection, Path Traversal, Hardcoded Credential |
| CWE | CWE identifier (e.g., CWE-89) — look it up if neither tool provided it |
| SAST? | Which SAST tool(s) flagged it: `bandit`, `semgrep`, `both`, or `—` (missed) |
| AI? | Did your AI tool flag this? `Y` or `N` |
| Human Verdict | **TP** — genuine vulnerability, or **FP** — acceptable pattern flagged in error |
| SAST Correct? | Does the SAST result match your Human Verdict? `Y` (agreed) or `N` (disagreed) |
| AI Correct? | Does the AI result match your Human Verdict? `Y` (agreed) or `N` (disagreed) |
| Notes | Any context that affected your verdict — e.g., "ETag, not a security control" |

**When making your Human Verdict, ask:**

1. Is the flagged code reachable with attacker-controlled input?
2. Does the context change the risk? (MD5 for a password vs. MD5 for a cache key are different risks)
3. What is the worst-case impact if an attacker exploits this?

### Step 7: Activity — Fill in the summary scorecard

After completing the comparison table, tally your results:

| Metric | SAST | AI | Human (reference) |
|---|---|---|---|
| Total findings reported | | | — |
| True positives identified | | | 13 |
| False positives reported | | | 5 |
| False negatives (missed entirely) | | | 3 |
| Precision (TP / total reported) | | | — |
| Findings consistent with Human verdict | | | — |

> **Precision** = true positives ÷ total findings reported. A tool that flags 30 issues and 10 are real has precision of 0.33. A tool that flags 5 issues and 5 are real has precision of 1.0 — but may have missed others.

---

## Phase 5 — Fix the True Positives *(~20 min)*

Choose **three** confirmed true positives from your worksheet where both SAST and AI agreed with your verdict. For each:

1. Write the corrected version in the file (new function with a `_safe` suffix).
2. Add a one-line comment explaining the flaw and the fix.
3. Re-run Bandit to confirm the finding is gone.

> **Constraint:** Do not fix false positives. If your fix suppresses a false positive, add a `# nosec BXX` annotation explaining why the pattern is safe, rather than restructuring the code around the tool's limitations.

### Step 8: Activity — Verify your fixes

```bash
bandit -r labs/ch08_vulnerable_app.py -ll
semgrep --config=auto labs/ch08_vulnerable_app.py
```

Confirm the three findings are gone and no new ones were introduced.

---

## Phase 6 — Group Discussion *(~20 min)*

Compare your completed worksheets across groups and discuss:

1. **SAST vs AI coverage**: Which findings did SAST catch that AI missed? Which did AI catch that SAST missed? Were there findings only a human spotted?

2. **Consistency without correctness**: Did SAST and AI agree on any findings that your human verdict classified as false positives? What does agreement between tools tell you — and not tell you?

3. **AI tool variation**: If different groups used different AI tools, compare their finding lists. Did the same tool produce consistent results across groups? Did different tools produce different findings for the same code?

4. **False positive rates**: Compare precision scores from your scorecards. Which approach had the highest precision? Which had the lowest? What is the cost of a high false-positive rate in a real security review?

5. **Design-level gaps**: Look at the login route (`/login`) and admin route (`/admin/users`). Did SAST find anything? Did AI? Did either identify the missing access-control check on `/admin/users`? What does this tell you about the limits of automated tooling?

6. **If a developer used AI to write this code**: Which vulnerabilities are most likely AI-generated? Which are patterns that both AI assistants and AI-written code share — and why?

---

## Reference: Bandit Rule Codes

| Rule | Description | Severity |
|------|-------------|----------|
| B105 | Hardcoded password or secret string | Medium |
| B201 | Flask app run with debug=True | High |
| B301 | Use of `pickle` module | Medium |
| B306 | Use of `mktemp` (race-condition risk) | Medium |
| B307 | Use of `eval()` | Medium |
| B311 | Use of `random` for security purposes | Low |
| B324 | Use of MD5 or SHA-1 hash function | Medium |
| B602 | `subprocess` with `shell=True` | High |
| B608 | SQL query constructed with string formatting | Medium |

---

### Instructor Answer Key

<details>
<summary><strong>Reveal answer key</strong> — attempt the worksheet before expanding</summary>

> *Distribute only after groups have completed their worksheets.*

Run Bandit without severity filter to see all findings including Low:

```bash
bandit -r labs/ch08_vulnerable_app.py   # no -ll flag
```

#### Full finding list with expected verdicts

**Bold** rows are findings that tools flag but human context classifies as false positives.

| # | Location | Type | CWE | SAST (Bandit/Semgrep) | Expected AI | Human Verdict | Notes |
|---|----------|------|-----|----------------------|-------------|---------------|-------|
| 1 | `app.secret_key` (L43) | Hardcoded credential | CWE-798 | Bandit B105 | Likely Y | **TP** | Flask session signing key — in source and git history |
| 2 | `STRIPE_API_KEY` (L49) | Hardcoded credential | CWE-798 | **Missed by Bandit**; Semgrep may catch | Likely Y | **TP** | B105 matched `secret_key` but not `STRIPE_API_KEY` — Bandit false negative |
| 3 | **`CACHE_SALT` (L50)** | **Hardcoded string** | **—** | **B105 (if flagged)** | **May flag** | **FP** | Static, non-secret cache namespace prefix — not a credential |
| 4 | `find_task` (L64) | SQL injection | CWE-89 | Bandit B608 | Likely Y | **TP** | `task_id` is user-controlled; interpolated directly into query string |
| 5 | `search_tasks` (L78) | SQL injection | CWE-89 | Bandit B608 | Likely Y | **TP** | `keyword` is user-controlled; `LIKE` does not prevent injection |
| 6 | `hash_password` (L88) | Broken cryptography | CWE-327 | Bandit B324 | Likely Y | **TP** | MD5 broken for password storage; use bcrypt or Argon2 |
| 7 | **`compute_etag` (L93)** | **MD5 usage** | **—** | **Bandit B324** | **May flag** | **FP** | ETag is a cache identifier, not a security control; MD5 is acceptable here |
| 8 | `generate_session_token` (L98) | Weak PRNG | CWE-338 | Bandit B311 | Likely Y | **TP** | `random` is predictable; use `secrets.token_urlsafe` |
| 9 | `generate_reset_code` (L103) | Weak PRNG | CWE-338 | Bandit B311 | Likely Y | **TP** | 6-digit `random` code is brute-forceable |
| 10 | `read_report` (L112) | Path traversal | CWE-22 | Semgrep | Likely Y | **TP** | `filename` from URL with no validation; `../../etc/passwd` escapes `REPORTS_DIR` |
| 11 | **`read_template` (L119–122)** | **Path traversal** | **CWE-22** | **Semgrep** | **May flag** | **FP** | Allowlist check before path construction prevents traversal entirely |
| 12 | `run_report_generator` (L133–135) | Command injection | CWE-78 | Bandit B602 | Likely Y | **TP** | `report_id` user-supplied and interpolated into shell string |
| 13 | **`hostname` command (L144–146)** | **`shell=True`** | **—** | **Bandit B602** | **May flag** | **FP** | Hardcoded literal — no user input reachable; Bandit itself notes "seems safe" |
| 14 | `pickle.loads` on cookie (L159) | Insecure deserialization | CWE-502 | Bandit B301 | Likely Y | **TP** | `session_data` from HTTP cookie; arbitrary code execution on deserialization |
| 15 | **`pickle.load` on ML model (L165–166)** | **Pickle usage** | **CWE-502** | **Bandit B301** | **May flag** | **FP** | Internal pipeline writes the file; path is not user-controlled |
| 16 | **`eval("1 + 1")` (L173)** | **`eval` usage** | **—** | **Bandit B307** | **May flag** | **FP** | Hardcoded literal argument; no user input can reach this call |
| 17 | `eval` on `request.args` (L200–201) | Code injection | CWE-94 | Bandit B307 | Likely Y | **TP** | `expr` from query string; enables arbitrary Python execution |
| 18 | `mktemp` in `/upload` (L208) | TOCTOU race | CWE-377 | Bandit B306 | Variable | **TP** | `mktemp` returns a name before creating the file; use `tempfile.NamedTemporaryFile` |
| 19 | Logged password in `/login` (L219) | Sensitive data exposure | CWE-532 | **Missed by both** | Likely Y | **TP** | Credentials written to stdout in plaintext; requires manual or AI review |
| 20 | No auth on `/admin/users` (L229) | Broken access control | CWE-284 | **Missed by both** | Variable | **TP** | Any unauthenticated caller lists all users; design-level gap invisible to pattern matchers |
| 21 | `debug=True` + `host="0.0.0.0"` (L238) | Security misconfiguration | CWE-94 | Bandit B201, B104 | Likely Y | **TP** | Werkzeug debugger on all interfaces; remote code execution |

#### Expected summary scorecard

| Metric | SAST (Bandit+Semgrep) | Notes |
|---|---|---|
| Total findings reported | ~18–20 | Varies by Semgrep ruleset version |
| True positives | 13 | |
| False positives | 5–7 | Tool version and config dependent |
| False negatives | 3 | Stripe key, logged password, missing auth |
| Precision | ~0.65–0.72 | |

**AI tool expectations (approximate — varies by model and prompt):**
- Strong models (Claude Opus, GPT-4o) typically catch findings 1–18 with low false-positive rates
- Weaker models may miss the TOCTOU race (finding 18) and the `CACHE_SALT` FP distinction
- All models tested as of 2025 miss or inconsistently catch finding 20 (missing access control) without explicit prompting about authorisation requirements
- AI findings 19 and 20 (logged password, missing auth) are the clearest test of whether AI reason about *intent* rather than just *pattern*

#### Key teaching points

- **Consistency ≠ correctness.** If SAST and AI both flag `compute_etag` for MD5, both are wrong. Agreement amplifies confidence, not accuracy.
- **AI catches what SAST misses — sometimes.** The logged password (finding 19) is typically invisible to Bandit and Semgrep but flagged by most AI assistants. Design-level gaps (finding 20) are harder for all automated tools.
- **AI has its own false positives.** AI assistants frequently flag `CACHE_SALT`, `pickle` on internal ML models, and `eval("1+1")` — the same patterns SAST over-flags — because they are trained on security advice that says "never use pickle/eval."
- **Different AI tools produce different results.** The same code produces different finding lists across Claude, ChatGPT, and Copilot Chat. No AI tool has a stable, reproducible output the way Bandit does.
- **Human review closes gaps all tools share.** Finding 20 — no authentication on `/admin/users` — requires knowing what the access-control requirements *should have been*, which neither SAST nor AI can infer without being told.

</details>

---

## References

- [Bandit documentation](https://bandit.readthedocs.io/)
- [Semgrep documentation](https://semgrep.dev/docs/)
- [OWASP Top 10 (2021)](https://owasp.org/www-project-top-ten/)
- [MITRE CWE catalogue](https://cwe.mitre.org/)
- [Perry et al. (2022) — Do Users Write More Insecure Code with AI Assistants?](https://arxiv.org/abs/2211.03622)
- [Liu et al. (2023) — Refining ChatGPT-Generated Code: Characterizing and Mitigating Code Quality Issues](https://arxiv.org/abs/2307.12596)
