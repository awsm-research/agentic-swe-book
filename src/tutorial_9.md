# Tutorial 9: Integrating SAST into a CI/CD Security Pipeline

By the end of this tutorial you will have a working security pipeline that scans Python code for vulnerabilities using Bandit and Semgrep, enforces a pass/fail gate in CI, produces a SARIF report viewable in GitHub's Security tab, and blocks merges on high-severity findings — including vulnerable dependencies.

**Concepts covered:** Static application security testing (SAST), Bandit, Semgrep, custom Semgrep rules, SARIF output, CI/CD security gates, dependency scanning with pip-audit

**Format:** Hands-on lab | **Duration:** ~2 hours | **Tool:** Bandit · Semgrep · pip-audit · GitHub Actions / GitLab CI

---

## Outline

- [Part A: Run SAST Tools Locally](#part-a-run-sast-tools-locally) *(~30 min)*
- [Part B: Build the SAST Runner Script](#part-b-build-the-sast-runner-script) *(~20 min)*
- [Part C: Write a Custom Semgrep Rule](#part-c-write-a-custom-semgrep-rule) *(~25 min)*
- [Part D: Integrate into CI/CD](#part-d-integrate-into-cicd) *(~30 min)*
- [Part E: Add Dependency Scanning](#part-e-add-dependency-scanning) *(~15 min)*

## Prerequisites

- [uv](https://docs.astral.sh/uv/) installed (Tutorial 1) — manages Python and virtual environments
- A Git repository ([GitHub](https://github.com/) or [GitLab](https://gitlab.com/)) with push access
- Familiarity with YAML and basic shell commands

---

## Learning Objectives

By the end of this tutorial, you will be able to:

1. Run Bandit and Semgrep against Python code and interpret findings by CWE and severity.
2. Build a SAST runner script that aggregates exit codes from multiple tools into a single pass/fail result.
3. Write a custom Semgrep rule that enforces a domain-specific security constraint.
4. Configure a GitHub Actions or GitLab CI pipeline that runs SAST on changed files and uploads SARIF results.
5. Detect known CVEs in Python dependencies using pip-audit and block merges on vulnerable packages.

---

## Part A: Run SAST Tools Locally

*(~30 min)*

### Step 1: Install the tools

```bash
uv add --dev bandit semgrep pip-audit
```

`uv add --dev` records the tools under `[dependency-groups.dev]` in `pyproject.toml` and pins exact versions in `uv.lock`, so every teammate gets an identical environment. Run `uv run bandit …` (or activate the virtual environment with `source .venv/bin/activate`) before the commands in subsequent steps.

### Step 2: Create the vulnerable target file

Save the following as `example_vulnerable.py`. Each function contains a deliberate vulnerability:

```python
# example_vulnerable.py
import subprocess
import sqlite3
import pickle
import hashlib


def get_user(username: str):
    conn = sqlite3.connect("users.db")
    # SQL injection: f-string interpolation instead of a parameterised query
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return conn.execute(query).fetchone()


def run_report(report_name: str):
    # Command injection: shell=True with user-controlled input
    subprocess.run(f"generate_report {report_name}", shell=True)


def load_session(data: bytes):
    # Insecure deserialization
    return pickle.loads(data)


def hash_password(password: str) -> str:
    # Weak cryptography: MD5 is not suitable for password hashing
    return hashlib.md5(password.encode()).hexdigest()


API_KEY = "sk-prod-abc123secret"  # Hardcoded credential
```

### Step 3: Run Bandit

```bash
bandit example_vulnerable.py -l -ii
```

Bandit reports each finding with a **Severity** (HIGH / MEDIUM / LOW) and **Confidence** rating. The `-l` flag sets minimum severity to LOW; `-ii` sets minimum confidence to MEDIUM. Expected findings:

| Rule | Finding | Severity |
|---|---|---|
| B105 | Hardcoded password string | HIGH |
| B602 | `subprocess` call with `shell=True` | HIGH |
| B301 | `pickle.loads` call | MEDIUM |
| B303 | Use of MD5 | MEDIUM |

Abbreviated terminal output:

```
>> Issue: [B602:subprocess_popen_with_shell_equals_true] subprocess call with shell=True ...
   Severity: High   Confidence: High
   Location: example_vulnerable.py:11

>> Issue: [B105:hardcoded_password_string] Possible hardcoded password: 'sk-prod-abc123secret'
   Severity: High   Confidence: Medium
   Location: example_vulnerable.py:23
...
Run started: ...
Total issues (by severity):   High: 2   Medium: 2   Low: 0
```

### Step 4: Run Semgrep

```bash
semgrep --config p/python --config p/owasp-top-ten example_vulnerable.py
```

Semgrep's `p/python` ruleset covers injection and insecure API patterns; `p/owasp-top-ten` maps findings to OWASP categories. Both rulesets are fetched from the Semgrep Registry at run time, so the exact set of rules and rule IDs can change between versions — treat the table below as representative, not exhaustive. Expected findings:

| Rule | Finding | CWE |
|---|---|---|
| `python.lang.security.audit.formatted-sql-query` | SQL injection via string formatting | CWE-89 |
| `python.lang.security.insecure-pickle-use` | Unsafe `pickle.loads` | CWE-502 |

Abbreviated terminal output:

```
Findings:
  example_vulnerable.py
    python.lang.security.audit.formatted-sql-query (CWE-89)
      Line 8: query = f"SELECT * FROM users WHERE username = '{username}'"

    python.lang.security.insecure-pickle-use (CWE-502)
      Line 17: return pickle.loads(data)

Ran 2 rules on 1 file: 2 findings.
```

Bandit and Semgrep have complementary coverage: Bandit catches Python built-in misuse (subprocess flags, weak hashing, hardcoded secrets) via AST-level checks; Semgrep's rulesets detect injection patterns by matching against the full expression tree, which lets it flag `f"SELECT ... {username}"` as SQL injection where Bandit sees only a string. Neither tool subsumes the other — running both maximises detection across these two orthogonal axes.

### Step 5: Activity — Fix and verify

Fix each finding in `example_vulnerable.py`:

1. Replace the f-string SQL query with a parameterised query using `?` placeholders and a tuple argument
2. Remove `shell=True` from `subprocess.run` and pass arguments as a list
3. Replace `pickle.loads` with `json.loads`
4. Replace `hashlib.md5` with `hashlib.sha256` (or `bcrypt` for a real password store)
5. Replace the hardcoded `API_KEY` with `os.environ["API_KEY"]`

Re-run both tools after each fix. Both scans should report zero findings when all five are resolved.

---

## Part B: Build the SAST Runner Script

*(~20 min)*

Running individual tool commands works when you're investigating a single file, but it doesn't scale to a pre-push check or a pre-commit hook. The script you build here wraps both tools behind a single command: pass it any number of file paths, it runs both scanners, and exits non-zero if either reports a finding. Part D's CI calls the tools directly with richer output flags (`--sarif`, `-f json`) that don't belong in a local script — but building this wrapper first teaches you the aggregation logic that the CI YAML later encodes.

### Step 1: Create the runner script

Save as `security_review.py`:

```python
# security_review.py
import subprocess
import sys


def run_bandit(path: str) -> tuple[str, int]:
    result = subprocess.run(
        ["bandit", path, "-f", "text", "-l", "-ii"],
        capture_output=True,
        text=True,
    )
    return result.stdout or result.stderr, result.returncode


def run_semgrep(path: str) -> tuple[str, int]:
    result = subprocess.run(
        ["semgrep", "--config", "p/python", "--config", "p/owasp-top-ten", path],
        capture_output=True,
        text=True,
    )
    return result.stdout or result.stderr, result.returncode


def review_file(path: str) -> int:
    print(f"\n{'=' * 60}")
    print(f"SECURITY REVIEW: {path}")
    print("=" * 60)
    exit_code = 0

    print("\n--- Bandit ---")
    bandit_out, bandit_rc = run_bandit(path)
    print(bandit_out if bandit_out.strip() else "No issues found.")
    if bandit_rc != 0:
        exit_code = 1

    print("\n--- Semgrep ---")
    semgrep_out, semgrep_rc = run_semgrep(path)
    print(semgrep_out if semgrep_out.strip() else "No issues found.")
    if semgrep_rc != 0:
        exit_code = 1

    return exit_code


if __name__ == "__main__":
    paths = sys.argv[1:]
    if not paths:
        print("Usage: python security_review.py <file1.py> [file2.py ...]")
        sys.exit(1)
    overall = 0
    for path in paths:
        overall |= review_file(path)
    sys.exit(overall)
```

### Step 2: Test the runner

```bash
python security_review.py example_vulnerable.py
echo "Exit code: $?"   # expect 1 (findings present)
```

After fixing all five vulnerabilities in Part A:

```bash
python security_review.py example_vulnerable.py
echo "Exit code: $?"   # expect 0 (clean)
```

### Step 3: Activity — Add SARIF output

[SARIF](https://sarifweb.azurewebsites.net/) is a standardised JSON schema for static analysis results that GitHub's Security tab understands natively. Extend the runner to produce a SARIF file alongside the text output:

1. Add a `run_semgrep_sarif` function that passes `--sarif --output semgrep-results.sarif` to Semgrep
2. Call `run_semgrep_sarif` from `review_file` in addition to the existing text-output call
3. Verify the output file is valid JSON:

```bash
python security_review.py example_vulnerable.py
python -c "import json; json.load(open('semgrep-results.sarif')); print('Valid SARIF')"
```

---

## Part C: Write a Custom Semgrep Rule

*(~25 min)*

Public rulesets cover common patterns but cannot encode your application's domain-specific constraints. Custom rules let you enforce invariants such as: "all database queries must use parameterised statements", "no route handler may be missing `@login_required`", or "no path may be constructed from request data without sanitisation."

### Step 1: Understand Semgrep rule syntax

A minimal rule:

```yaml
rules:
  - id: rule-id
    patterns:
      - pattern: <code pattern>
    message: <what to report>
    languages: [python]
    severity: ERROR
```

Patterns use `...` as a wildcard for any expression or statement, and metavariables (`$VAR`) to capture code elements. The `patterns` key requires all sub-patterns to match; `pattern-either` matches any one of them.

### Step 2: Write a rule for unsafe path construction

Flask applications commonly construct file paths from user input. Create `rules/unsafe-path.yml`:

```yaml
rules:
  - id: flask-unsafe-path-join
    patterns:
      - pattern: os.path.join(..., request.$ATTR, ...)
    message: >
      Path constructed from request data without sanitisation (CWE-22: Path Traversal).
      Resolve and validate the path against an allowed base directory before use.
    languages: [python]
    severity: ERROR
    metadata:
      cwe: CWE-22
      owasp: A01:2021
```

### Step 3: Test the rule

Save as `test_path.py`:

```python
# test_path.py
from flask import request
import os

def download_file():
    filename = request.args.get("file")
    path = os.path.join("/uploads", filename)   # ← should trigger
    with open(path) as f:
        return f.read()

def safe_download():
    filename = request.args.get("file")
    base = "/uploads"
    path = os.path.realpath(os.path.join(base, filename))
    if not path.startswith(base):
        raise ValueError("Path traversal attempt")
    with open(path) as f:
        return f.read()
```

```bash
semgrep --config rules/unsafe-path.yml test_path.py
```

The rule should flag `download_file` and pass `safe_download`. If it flags `safe_download`, add a `pattern-not` clause to exclude the safe pattern.

### Step 4: Activity — Write a rule for your project

Write a Semgrep rule that enforces a security constraint specific to your course project. Candidates:

- Flag any `requests.get` / `requests.post` call that passes `verify=False` (disabled TLS verification)
- Flag any `logging` call that formats a string using `%` or f-strings with user-controlled data (log injection)
- Flag any SQLAlchemy `session.execute(text(...))` call where the argument is a string concatenation rather than a bound parameter

For each rule:
1. Write a triggering example and a safe counterexample
2. Run `semgrep --config <your-rule.yml> <test-file.py>` and confirm the rule fires only on the triggering example
3. Integrate the rule into the `run_semgrep` call in `security_review.py` using `--config rules/`

---

## Part D: Integrate into CI/CD

*(~30 min)*

### Step 1: GitHub Actions — SAST with SARIF upload

Create `.github/workflows/security.yml`:

```yaml
name: Security Review

on:
  pull_request:
    paths:
      - '**.py'

jobs:
  sast:
    runs-on: ubuntu-latest
    permissions:
      security-events: write  # required to upload SARIF to the Security tab

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 2

      - name: Install tools
        run: pip install bandit semgrep

      - name: Run SAST on changed files
        run: |
          CHANGED=$(git diff --name-only HEAD~1 | grep '\.py$' || true)  # || true: grep exits 1 when no match; don't fail the step
          if [ -z "$CHANGED" ]; then echo "No Python files changed."; exit 0; fi
          echo "$CHANGED" | xargs bandit -f json -o bandit-results.json -l -ii
          echo "$CHANGED" | xargs semgrep --config p/python --config p/owasp-top-ten \
            --sarif --output semgrep-results.sarif

      - name: Upload SARIF to GitHub Security tab
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: semgrep-results.sarif

      - name: Fail on HIGH-severity Bandit findings
        run: |
          python - <<'EOF'
          import json, sys
          with open("bandit-results.json") as f:
              data = json.load(f)
          highs = [r for r in data.get("results", []) if r["issue_severity"] == "HIGH"]
          if highs:
              print(f"FAIL: {len(highs)} HIGH-severity finding(s)")
              for h in highs:
                  print(f"  {h['test_id']} — {h['issue_text']} ({h['filename']}:{h['line_number']})")
              sys.exit(1)
          print("OK: no HIGH-severity findings.")
          EOF
```

### Step 2: GitLab CI configuration

Add to `.gitlab-ci.yml`:

```yaml
sast:
  stage: test
  image: python:3.12-slim
  before_script:
    - pip install bandit semgrep
  script:
    - |
      CHANGED=$(git diff --name-only HEAD~1 | grep '\.py$' || true)  # || true: grep exits 1 when no match
      if [ -z "$CHANGED" ]; then echo "No Python files changed."; exit 0; fi
      echo "$CHANGED" | xargs bandit -f json -o bandit-results.json -l -ii
      echo "$CHANGED" | xargs semgrep --config p/python --config p/owasp-top-ten \
        --sarif --output semgrep-results.sarif
  artifacts:
    when: always
    paths:
      - bandit-results.json
      - semgrep-results.sarif
    expire_in: 7 days
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      changes:
        - "**/*.py"
```

### Step 3: Activity — Trigger and fix the pipeline

1. Re-introduce a deliberate vulnerability into a Python file (e.g., add `shell=True` to a `subprocess.run` call)
2. Commit and push to a feature branch; open a pull/merge request
3. Confirm: Bandit reports the finding, SARIF is uploaded, the job fails and blocks the merge
4. Fix the vulnerability, push again, confirm the job passes and the Security tab shows no new alerts
5. Examine the uploaded SARIF file — identify the `runs[].results[].locations` path and confirm it points to the correct line

---

## Part E: Add Dependency Scanning

*(~15 min)*

Code vulnerabilities are only one surface. Agentic workflows often add or update Python dependencies without a security review. `pip-audit` queries the Python Packaging Advisory Database (PyPA) for known CVEs in installed packages.

### Step 1: Create a requirements file with a known vulnerability

```text
# requirements.txt
flask==2.0.1
requests==2.18.0
```

`requests 2.18.0` is used here as a known-vulnerable pin. It has accumulated several CVEs since its release — CVE-2023-32681 (credential leak via redirect) is one of the more recent, but pip-audit will list all known advisories for the installed version.

### Step 2: Run pip-audit

```bash
pip-audit -r requirements.txt
```

Expected output:

```
Name      Version ID                  Fix Versions
--------- ------- ------------------- ------------
requests  2.18.0  CVE-2023-32681      2.31.0
requests  2.18.0  PYSEC-2018-28       2.20.0
```

pip-audit names the vulnerable package, the installed version, each advisory ID, and the earliest version that resolves it.

### Step 3: Add dependency scanning to CI

**GitHub Actions** — append under `jobs:` in `security.yml`:

```yaml
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install pip-audit
        run: pip install pip-audit
      - name: Scan dependencies
        run: pip-audit -r requirements.txt -f json -o pip-audit-results.json
      - uses: actions/upload-artifact@v4
        with:
          name: pip-audit-results
          path: pip-audit-results.json
```

**GitLab CI** — append to `.gitlab-ci.yml`:

```yaml
dependency-scan:
  stage: test
  image: python:3.12-slim
  before_script:
    - pip install pip-audit
  script:
    - pip-audit -r requirements.txt -f json -o pip-audit-results.json
  artifacts:
    when: always
    paths:
      - pip-audit-results.json
    expire_in: 7 days
```

### Step 4: Activity — Update and verify

1. Update `requests` to the latest version in `requirements.txt`
2. Re-run `pip-audit -r requirements.txt` and confirm the CVE is gone
3. Push the updated `requirements.txt` to your branch; confirm the `dependency-scan` CI job passes
4. Temporarily pin `requests` back to `2.18.0` and push — confirm the job fails and names the CVE

---

## References

- [Bandit documentation](https://bandit.readthedocs.io/)
- [Semgrep documentation](https://semgrep.dev/docs/)
- [pip-audit](https://github.com/pypa/pip-audit)
- [SARIF specification](https://sarifweb.azurewebsites.net/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- Pearce, H., Ahmad, B., Tan, B., Dolan-Gavitt, B., & Karri, R. (2022). Asleep at the keyboard? Assessing the security of GitHub Copilot's code contributions. *2022 IEEE Symposium on Security and Privacy*. [https://arxiv.org/abs/2108.09293](https://arxiv.org/abs/2108.09293)
