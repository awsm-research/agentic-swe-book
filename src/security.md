# Chapter 5: Software Security

> *"Security is not a product, but a process."*
> — Bruce Schneier

---

## Learning Objectives

By the end of this chapter, you will be able to:

1. Explain foundational software security concepts: vulnerability, CVE, CWE, and the OWASP Top 10.
2. Identify and mitigate common Python security vulnerabilities.
3. Perform basic secrets scanning and PII detection.
4. Describe AI-specific threats: prompt injection, data leakage, and AI-generated vulnerabilities.
5. Explain how AI coding assistants can introduce security vulnerabilities.
6. Conduct a basic threat model for an AI-enabled system using STRIDE.

---

## 5.1 Software Security Fundamentals

Security is not a feature you add to a system — it is a property that must be designed in from the start. A single vulnerability in a deployed system can expose all user data, allow unauthorised access, or enable an attacker to take over the entire server.

### 5.1.1 Key Terminology

**Vulnerability**: A weakness in software that can be exploited by an attacker to cause harm. Vulnerabilities may arise from coding errors, design flaws, or misconfiguration.

**Exploit**: A technique or piece of code that takes advantage of a vulnerability.

**CVE (Common Vulnerabilities and Exposures)**: A public catalogue of known software vulnerabilities, maintained by MITRE ([cve.mitre.org](https://cve.mitre.org/)). Each CVE entry has a unique identifier (e.g., CVE-2021-44228 for Log4Shell) and describes the vulnerability, affected versions, and severity.

**CWE (Common Weakness Enumeration)**: A catalogue of common software weakness types ([cwe.mitre.org](https://cwe.mitre.org/)). Where CVE describes specific instances ("this version of this library has this vulnerability"), CWE describes classes of weakness ("SQL injection" is CWE-89; "Path Traversal" is CWE-22). CWE is useful for training developers to recognise and avoid vulnerability patterns.

**CVSS (Common Vulnerability Scoring System)**: A standardised scoring system that rates vulnerability severity from 0 (none) to 10 (critical) based on exploitability, impact, and scope ([NIST, 2019](https://nvd.nist.gov/vuln-metrics/cvss)).

### 5.1.2 The OWASP Top 10

The Open Web Application Security Project publishes a regularly updated list of the most critical web application security risks ([OWASP, 2021](https://owasp.org/www-project-top-ten/)). The 2021 Top 10:

| Rank | Category | Description |
|---|---|---|
| A01 | Broken Access Control | Improper enforcement of what authenticated users can do |
| A02 | Cryptographic Failures | Weak or improperly implemented cryptography |
| A03 | Injection | SQL, command, LDAP injection via untrusted input |
| A04 | Insecure Design | Security risks from flawed design decisions |
| A05 | Security Misconfiguration | Default configs, unnecessary features, missing hardening |
| A06 | Vulnerable Components | Using components with known vulnerabilities |
| A07 | Authentication Failures | Weak authentication, session management |
| A08 | Software & Data Integrity Failures | Insecure deserialization, CI/CD pipeline attacks |
| A09 | Logging & Monitoring Failures | Insufficient logging to detect and respond to attacks |
| A10 | SSRF | Server-Side Request Forgery: server making requests to unintended targets |

---

## 5.2 Common Python Security Vulnerabilities

Python is a safe language in many respects, but its expressiveness and dynamic features introduce specific security pitfalls.

### 5.2.1 SQL Injection (CWE-89)

SQL injection occurs when untrusted input is incorporated directly into a SQL query, allowing attackers to alter the query's logic.

```python
# VULNERABLE: String concatenation in SQL
def get_user_by_name_bad(name: str) -> dict | None:
    query = f"SELECT * FROM users WHERE name = '{name}'"
    # If name = "'; DROP TABLE users; --"
    # Query becomes: SELECT * FROM users WHERE name = ''; DROP TABLE users; --'
    return db.execute(query).fetchone()


# SAFE: Parameterised query
def get_user_by_name(name: str) -> dict | None:
    query = "SELECT * FROM users WHERE name = %s"
    return db.execute(query, (name,)).fetchone()
```

**Rule**: Never concatenate user input into a SQL string. Always use parameterised queries or an ORM.

### 5.2.2 Command Injection (CWE-78)

Command injection occurs when user input is passed to a shell command.

```python
import subprocess

# VULNERABLE: Shell=True with user input
def run_analysis_bad(filename: str) -> str:
    result = subprocess.run(
        f"analyze_tool {filename}",
        shell=True,  # DANGEROUS with user input
        capture_output=True,
        text=True,
    )
    return result.stdout


# SAFE: Shell=False with argument list
def run_analysis(filename: str) -> str:
    # Validate filename first
    if not filename.replace("_", "").replace("-", "").replace(".", "").isalnum():
        raise ValueError(f"Invalid filename: {filename}")

    result = subprocess.run(
        ["analyze_tool", filename],  # List form, no shell interpretation
        shell=False,
        capture_output=True,
        text=True,
    )
    return result.stdout
```

**Rule**: Never use `shell=True` with user-controlled input. Use a list of arguments instead.

### 5.2.3 Path Traversal (CWE-22)

Path traversal allows attackers to access files outside the intended directory by using `../` sequences.

```python
import os
from pathlib import Path

UPLOAD_DIR = Path("/app/uploads")

# VULNERABLE: Direct path construction
def read_upload_bad(filename: str) -> bytes:
    path = UPLOAD_DIR / filename  # filename = "../../etc/passwd" would escape!
    with open(path, "rb") as f:
        return f.read()


# SAFE: Resolve and verify the path stays within the intended directory
def read_upload(filename: str) -> bytes:
    requested_path = (UPLOAD_DIR / filename).resolve()

    # Verify the resolved path is still under UPLOAD_DIR
    if not str(requested_path).startswith(str(UPLOAD_DIR.resolve())):
        raise PermissionError(f"Access denied: {filename}")

    with open(requested_path, "rb") as f:
        return f.read()
```

### 5.2.4 Insecure Deserialization (CWE-502)

Python's `pickle` module can execute arbitrary code when deserialising untrusted data.

```python
import pickle
import json

# VULNERABLE: Deserialising untrusted pickle data
def load_session_bad(data: bytes) -> dict:
    return pickle.loads(data)  # Arbitrary code execution on untrusted data!


# SAFE: Use JSON for data serialisation
def load_session(data: str) -> dict:
    session = json.loads(data)
    # Validate the structure before returning
    if not isinstance(session, dict):
        raise ValueError("Invalid session data")
    return session
```

**Rule**: Never use `pickle`, `marshal`, or `yaml.load` (without `Loader=yaml.SafeLoader`) on untrusted data.

### 5.2.5 Hardcoded Credentials (CWE-798)

Hardcoded passwords, API keys, and tokens in source code are frequently exposed via public repositories.

```python
import os

# VULNERABLE: Hardcoded credentials
def connect_bad():
    return DatabaseConnection(
        host="db.example.com",
        password="SuperSecret123!",  # Visible in source code, git history
    )


# SAFE: Read from environment variables
def connect():
    password = os.environ.get("DB_PASSWORD")
    if not password:
        raise EnvironmentError("DB_PASSWORD environment variable is not set")
    return DatabaseConnection(host=os.environ["DB_HOST"], password=password)
```

**Rule**: Credentials must never appear in source code. Use environment variables, a secrets manager (AWS Secrets Manager, HashiCorp Vault), or a `.env` file that is excluded from version control.

---

## 5.3 PII and Credential Detection

### 5.3.1 GitLeaks

GitLeaks ([Gitleaks, 2019](https://github.com/gitleaks/gitleaks)) is an open-source tool that scans git repositories for secrets — API keys, passwords, tokens, and other credentials — using a library of regular expression patterns.

```bash
# Install
brew install gitleaks   # macOS
# or: go install github.com/gitleaks/gitleaks/v8@latest

# Scan the current repository
gitleaks detect --source .

# Scan git history (catches secrets that were committed then deleted)
gitleaks detect --source . --log-opts="--all"
```

GitLeaks can be added to your CI/CD pipeline to prevent secrets from ever reaching the repository.

```yaml
# .github/workflows/security.yml (add to CI)
- name: Scan for secrets
  uses: gitleaks/gitleaks-action@v2
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 5.3.2 PII Detection

Personally Identifiable Information (PII) — names, email addresses, phone numbers, government IDs — must be handled with particular care under regulations like GDPR (EU) and the Privacy Act (Australia).

For Python applications, the Microsoft Presidio library ([Microsoft, 2019](https://github.com/microsoft/presidio)) provides PII detection and anonymisation:

```python
# pip install presidio-analyzer presidio-anonymizer
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()


def detect_pii(text: str) -> list[dict]:
    """Detect PII entities in a text string."""
    results = analyzer.analyze(text=text, language="en")
    return [
        {
            "entity_type": r.entity_type,
            "start": r.start,
            "end": r.end,
            "score": r.score,
            "text": text[r.start : r.end],
        }
        for r in results
    ]


def anonymise_pii(text: str) -> str:
    """Replace PII entities with type placeholders."""
    results = analyzer.analyze(text=text, language="en")
    anonymised = anonymizer.anonymize(text=text, analyzer_results=results)
    return anonymised.text


# Example
text = "Alice Smith (alice@example.com) was assigned task #123"
print(detect_pii(text))
# [{'entity_type': 'PERSON', ...}, {'entity_type': 'EMAIL_ADDRESS', ...}]

print(anonymise_pii(text))
# "<PERSON> (<EMAIL_ADDRESS>) was assigned task #123"
```

---

## Tutorial Activity: SAST Triage — True Positives vs False Positives

**Duration:** 2 hours | **Format:** Pairs or small groups | **Difficulty:** Intermediate

---

### Scenario

You are a security engineer reviewing a pull request from a junior developer who built a task-management REST API over the weekend. The code compiles and passes all unit tests. Your job is to run two SAST tools against the file, collect every finding, and determine which ones are genuine vulnerabilities and which are tool noise.

The lab file is at `labs/ch05_vulnerable_app.py`.

---

### Learning Outcomes

By completing this activity you will be able to:

- Run Bandit and Semgrep against a Python codebase and interpret their output.
- Distinguish between true positives (real vulnerabilities) and false positives (acceptable patterns the tool over-flags).
- Map findings to OWASP Top 10 categories and CWE identifiers.
- Propose a minimal, correct fix for each confirmed vulnerability.
- Identify vulnerabilities that SAST tools miss entirely (false negatives).

---

### Phase 1 — Setup (15 min)

Install the two SAST tools into a virtual environment:

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

### Phase 2 — Run the Tools (20 min)

Run each tool against the lab file and save the output to a file so you can refer back to it during triage.

**Bandit** — a Python-specific SAST tool that maps findings to CWE and reports severity and confidence levels:

```bash
# -r  recursive  -ll  medium-and-above severity  -f json  machine-readable output
bandit -r labs/ch05_vulnerable_app.py -ll -f json -o bandit_results.json

# Human-readable version for review
bandit -r labs/ch05_vulnerable_app.py -ll
```

**Semgrep** — a multi-language SAST tool that uses rule sets from the community registry:

```bash
semgrep --config=auto labs/ch05_vulnerable_app.py --json -o semgrep_results.json

# Human-readable version
semgrep --config=auto labs/ch05_vulnerable_app.py
```

> **Tip:** Bandit and Semgrep will each flag different subsets of issues. Some findings appear in both tools; some appear in only one. Note which tool produced each finding — this matters during triage.

---

### Phase 3 — Triage Worksheet (50 min)

For every finding reported by either tool, complete one row of the triage table below. Work through the findings in order of reported severity (Critical → High → Medium → Low).

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

---

### Phase 4 — Fix the True Positives (20 min)

Choose **three** of the confirmed true positives from your worksheet. For each one:

1. Write the corrected version of the function directly in the file (create a new function with a `_safe` suffix).
2. Add a one-line comment explaining what was wrong and how the fix addresses it.
3. Re-run Bandit on your fixed version to confirm the finding is gone.

> **Constraint:** Do not fix the false positives. If your fix causes Bandit to stop flagging a true false positive, add a `# nosec BXX` annotation with a comment explaining why it is safe, rather than restructuring the code.

---

### Phase 5 — Group Discussion (15 min)

Compare your triage worksheets across groups and discuss:

1. **Did every group agree on which findings were TP vs FP?** Where did groups disagree, and why?
2. **Which vulnerabilities did BOTH tools catch?** Which did only one tool catch? Which did neither catch?
3. **What did the tools miss entirely?** Look at the login route (`/login`) and the admin route (`/admin/users`) — are there security problems there that neither tool reported?
4. **AI-generated code risk:** If a junior developer used an AI coding assistant to write this file, which of these vulnerabilities might the assistant have introduced? Which are more likely to be human mistakes?
5. **Severity triage:** If you had only 30 minutes to fix the most critical issues before deploying, which three vulnerabilities would you prioritise and why?

---

### Reference: Bandit Rule Codes

The following Bandit rules are relevant to findings in this lab. Use this table to map rule IDs to vulnerability categories.

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

The table below lists every intentional finding in `labs/ch05_vulnerable_app.py` and the expected verdict. **Bold** rows are findings that SAST tools flag but that require human context to classify correctly — these are the false positives.

Run Bandit without any severity filter to see all findings including Low:

```bash
bandit -r labs/ch05_vulnerable_app.py   # no -ll flag
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