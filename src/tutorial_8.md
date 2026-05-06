# Tutorial 8: SAST Triage — True Positives vs False Positives

A junior developer built a task-management REST API over the weekend. The code compiles and all unit tests pass. Your job is to run two static analysis tools against the file, collect every finding, and determine which are genuine vulnerabilities and which are tool noise — then fix the real ones.

**Concepts covered:** SAST tools (Bandit, Semgrep), true positives vs false positives, OWASP Top 10 mapping, CWE identifiers, AI-generated vulnerability patterns

**Format:** Pairs or small groups | **Duration:** 2 hours | **Tool:** Python, Bandit, Semgrep

---

## Outline

- [Phase 1: Setup](#phase-1--setup-15-min)
- [Phase 2: Run the Tools](#phase-2--run-the-tools-20-min)
- [Phase 3: Triage Worksheet](#phase-3--triage-worksheet-50-min)
- [Phase 4: Fix the True Positives](#phase-4--fix-the-true-positives-20-min)
- [Phase 5: Group Discussion](#phase-5--group-discussion-15-min)
- [Reference: Bandit Rule Codes](#reference-bandit-rule-codes)
- [References](#references)

---

## Learning Objectives

By the end of this tutorial you will be able to:

1. Run Bandit and Semgrep against a Python codebase and interpret their output.
2. Distinguish between true positives (real vulnerabilities) and false positives (acceptable patterns the tool over-flags).
3. Map findings to OWASP Top 10 categories and CWE identifiers.
4. Propose a minimal, correct fix for each confirmed vulnerability.
5. Identify vulnerabilities that SAST tools miss entirely (false negatives).

---

## Phase 1 — Setup *(~15 min)*

The lab file is at `labs/ch08_vulnerable_app.py`. Install the two SAST tools into a virtual environment:

```bash
python -m venv .venv && source .venv/bin/activate
pip install flask bandit semgrep
```

Verify they are installed:

```bash
bandit --version
semgrep --version
```

---

## Phase 2 — Run the Tools *(~20 min)*

Run each tool against the lab file and save the output so you can refer back to it during triage.

**Bandit** — a Python-specific SAST tool that maps findings to CWE and reports severity and confidence levels:

```bash
# -r  recursive  -ll  medium-and-above severity  -f json  machine-readable output
bandit -r labs/ch08_vulnerable_app.py -ll -f json -o bandit_results.json

# Human-readable version for review
bandit -r labs/ch08_vulnerable_app.py -ll
```

**Semgrep** — a multi-language SAST tool that uses rule sets from the community registry:

```bash
semgrep --config=auto labs/ch08_vulnerable_app.py --json -o semgrep_results.json

# Human-readable version
semgrep --config=auto labs/ch08_vulnerable_app.py
```

> **Tip:** Bandit and Semgrep flag different subsets of issues. Some findings appear in both tools; some in only one. Note which tool produced each finding — this matters during triage.

---

## Phase 3 — Triage Worksheet *(~50 min)*

For every finding reported by either tool, complete one row of the triage table below. Work through findings in order of reported severity (Critical → High → Medium → Low).

For each finding, ask:

1. **Is the flagged code reachable with attacker-controlled input?** If not, it may be a false positive.
2. **Does the context change the risk?** (e.g., MD5 for a password vs. MD5 for an HTTP cache key)
3. **What is the worst-case impact if the vulnerability is exploited?**

Copy this table into a text file or spreadsheet and fill it in:

```
| # | Tool    | Rule / Check       | Line | Description                        | TP / FP | Reason                                           | OWASP | CWE   | Proposed Fix                        |
|---|---------|--------------------|----|-------------------------------------|---------|--------------------------------------------------|-------|-------|-------------------------------------|
| 1 |         |                    |    |                                     |         |                                                  |       |       |                                     |
| 2 |         |                    |    |                                     |         |                                                  |       |       |                                     |
| … |         |                    |    |                                     |         |                                                  |       |       |                                     |
```

**Column guide**

| Column | What to write |
|---|---|
| Tool | `bandit`, `semgrep`, or `both` |
| Rule / Check | The rule ID (e.g. `B608`, `python.lang.security.audit.eval-detected`) |
| Line | Line number in the source file |
| Description | One sentence — what the tool thinks is wrong |
| TP / FP | Your verdict: **TP** (genuine vulnerability) or **FP** (acceptable pattern) |
| Reason | Why you made that call — cite code context, not just the rule description |
| OWASP | Relevant OWASP Top 10 category (e.g. A03 — Injection) |
| CWE | Relevant CWE ID (e.g. CWE-89) |
| Proposed Fix | For TPs only: one sentence or a code sketch of the fix |

### Step 1: Activity — Complete the Triage Worksheet

Work through every finding. When you have finished, count your totals: how many TPs, how many FPs, how many did both tools catch vs only one?

---

## Phase 4 — Fix the True Positives *(~20 min)*

Choose **three** of the confirmed true positives from your worksheet. For each one:

1. Write the corrected version of the function directly in the file (create a new function with a `_safe` suffix).
2. Add a one-line comment explaining what was wrong and how the fix addresses it.
3. Re-run Bandit on your fixed version to confirm the finding is gone.

> **Constraint:** Do not fix the false positives. If your fix causes Bandit to stop flagging a true false positive, add a `# nosec BXX` annotation with a comment explaining why it is safe, rather than restructuring the code.

### Step 2: Activity — Verify Your Fixes

After fixing your three chosen vulnerabilities, run both tools again and confirm the findings are resolved:

```bash
bandit -r labs/ch08_vulnerable_app.py -ll
semgrep --config=auto labs/ch08_vulnerable_app.py
```

Check that no new findings were introduced by your fixes.

---

## Phase 5 — Group Discussion *(~15 min)*

Compare your triage worksheets across groups and discuss:

1. **Did every group agree on which findings were TP vs FP?** Where did groups disagree, and why?
2. **Which vulnerabilities did BOTH tools catch?** Which did only one tool catch? Which did neither catch?
3. **What did the tools miss entirely?** Look at the login route (`/login`) and the admin route (`/admin/users`) — are there security problems there that neither tool reported?
4. **AI-generated code risk:** If a junior developer used an AI coding assistant to write this file, which of these vulnerabilities might the assistant have introduced? Which are more likely to be human mistakes?
5. **Severity triage:** If you had only 30 minutes to fix the most critical issues before deploying, which three vulnerabilities would you prioritise and why?

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
<summary><strong>Reveal answer key</strong> — attempt the triage worksheet before expanding</summary>

> *This section should be distributed only after groups have completed their worksheets.*

The table below lists every intentional finding in `labs/ch08_vulnerable_app.py` and the expected verdict. **Bold** rows are findings that SAST tools flag but that require human context to classify correctly — these are the false positives.

Run Bandit without any severity filter to see all findings including Low:

```bash
bandit -r labs/ch08_vulnerable_app.py   # no -ll flag
```

| Finding | Line | Bandit Rule | Verdict | Key Reasoning |
|---------|------|-------------|---------|---------------|
| Hardcoded `app.secret_key` | 43 | B105 | **TP** | Flask session signing key in source code and git history |
| `STRIPE_API_KEY` — *missed by Bandit* | 49 | — (false negative) | **TP** | Bandit B105 matched `secret_key` but not `STRIPE_API_KEY`; use Semgrep or GitLeaks for broad secrets scanning |
| **`CACHE_SALT` string** | **50** | **B105 (if flagged)** | **FP** | Not a credential — a static, non-secret cache namespace prefix |
| SQL injection in `find_task` | 64 | B608 | **TP** | `task_id` is user-controlled and interpolated directly into the query string |
| SQL injection in `search_tasks` | 78 | B608 | **TP** | `keyword` is user-controlled; `LIKE` with wildcards does not prevent injection |
| MD5 in `hash_password` | 88 | B324 | **TP** | MD5 is cryptographically broken for password storage; use bcrypt or Argon2 |
| **MD5 in `compute_etag`** | **93** | **B324** | **FP** | An ETag is a cache identifier, not a security control; MD5 is acceptable for non-cryptographic checksums |
| `random.randint` in `generate_session_token` | 98 | B311 | **TP** | `random` is seeded and predictable; session tokens must use `secrets.token_urlsafe` |
| `random.randint` in `generate_reset_code` | 103 | B311 | **TP** | Same issue; a 6-digit code from `random` is brute-forceable |
| Path traversal in `read_report` | 112 | Semgrep (CWE-22) | **TP** | `filename` comes from the URL with no validation; `../../etc/passwd` escapes `REPORTS_DIR` |
| **Allowlist-guarded `read_template`** | **119–122** | **Semgrep (CWE-22)** | **FP** | The `allowed` set check before path construction prevents traversal entirely |
| Command injection in `run_report_generator` | 133–135 | B602 | **TP** | `report_id` is user-supplied and interpolated into a shell command string |
| **Static `hostname` command** | **144–146** | **B602** | **FP** | Bandit itself notes "seems safe" — the shell string is a hardcoded literal with no user input |
| `pickle.loads` on cookie data | 159 | B301 | **TP** | `session_data` arrives from an HTTP cookie; arbitrary code execution on deserialization |
| **`pickle.load` on internal ML model** | **165–166** | **B301** | **FP** | The model file is written by a trusted internal pipeline, not by users; the file path is not user-controlled |
| **`eval` on constant `"1 + 1"`** | **173** | **B307** | **FP** | The argument is a hardcoded string literal; no user input can reach this call |
| `eval` on `request.args` in `/calculate` | 200–201 | B307 | **TP** | `expr` is taken directly from the query string; enables arbitrary Python execution |
| Insecure `mktemp` in `/upload` | 208 | B306 | **TP** | `mktemp` returns a name before creating the file — TOCTOU race condition; use `tempfile.NamedTemporaryFile` |
| Logging password in `/login` — *missed by both* | 219 | — (false negative) | **TP** | Credentials written to stdout in plaintext; requires manual code review |
| No auth on `/admin/users` — *missed by both* | 229 | — (false negative) | **TP** | Any unauthenticated caller can list all users; SAST cannot detect design-level access-control gaps |
| Flask `debug=True` and `host="0.0.0.0"` | 238 | B201, B104 | **TP** | Exposes the Werkzeug interactive debugger on all interfaces; enables remote code execution |

**Summary counts**

| Category | Count |
|----------|-------|
| True positives (genuine vulnerabilities) | 13 |
| False positives (tool noise — acceptable patterns) | 5 |
| False negatives (missed entirely by both tools) | 3 |

**Key teaching points**

- Bandit flags *patterns* (any use of MD5, any pickle, any `shell=True`), not *intent*. Context determines whether the pattern is actually exploitable — that is the human's job.
- B105 matched `app.secret_key` but not `STRIPE_API_KEY`. No SAST tool has perfect pattern coverage; complement Bandit with Semgrep and GitLeaks for secrets.
- Three findings — the hardcoded Stripe key, the logged password, and the unauthenticated admin route — require manual reasoning and are invisible to at least one or both tools. SAST is a floor, not a ceiling.
- The false positive rate in this file (~28%) is representative of real-world SAST deployments. Teams that dismiss all FPs start ignoring true positives too.
- AI coding assistants commonly reproduce all the patterns in this file: SQL concatenation, `debug=True`, hardcoded credentials, and `shell=True` are among the most frequent AI-generated vulnerabilities. Running SAST on every commit catches them before they reach production.

</details>

---

## References

- [Bandit documentation](https://bandit.readthedocs.io/)
- [Semgrep documentation](https://semgrep.dev/docs/)
- [OWASP Top 10 (2021)](https://owasp.org/www-project-top-ten/)
- [MITRE CWE catalogue](https://cwe.mitre.org/)
- [GitLeaks](https://github.com/gitleaks/gitleaks)
