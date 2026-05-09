# Chapter 8: Security of AI-Generated Code

> *"Security is not a product, but a process."*
> — Bruce Schneier

---

Veracode's 2025 GenAI Code Security Report tested more than 100 large language models across security-sensitive coding tasks and found that 45% of AI-generated code samples introduce at least one OWASP Top 10 vulnerability — and that AI-generated code contains 2.74 times more security flaws than human-written equivalents ([Veracode, 2025](https://www.veracode.com/resources/analyst-reports/2025-genai-code-security-report/)). The models improved at producing syntactically correct, functional code; they did not improve at producing secure code. Georgia Tech's Vibe Security Radar, launched in May 2025 to formally track CVEs attributable to AI coding tools, documented 78 confirmed AI-linked vulnerabilities through March 2026 — 43 of them rated Critical or High severity — with the pace accelerating sharply: March 2026 alone recorded 35 CVEs, more than the entirety of the second half of 2025 combined ([Georgia Tech, 2026](https://research.gatech.edu/bad-vibes-ai-generated-code-vulnerable-researchers-warn)). The pattern is structural, not incidental. An AI assistant that generates hundreds of lines per session, at a pace no manual reviewer can match, turns every untriaged output into a potential entry point. Functional correctness is not security. Throughput without verification is a liability.

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

## 8.1 Software Security Fundamentals

A single unpatched vulnerability can expose an entire database, bypass authentication for every account, or hand an attacker remote code execution on the server — which is why security must be addressed throughout development, not retrofitted after deployment.

### 8.1.1 Key Terminology

**Vulnerability**: A weakness in software that can be exploited by an attacker to cause harm. Vulnerabilities may arise from coding errors, design flaws, or misconfiguration.

**Exploit**: A technique or piece of code that takes advantage of a vulnerability.

**CVE (Common Vulnerabilities and Exposures)**: A public catalogue of known software vulnerabilities, maintained by MITRE ([cve.mitre.org](https://cve.mitre.org/)). Each CVE entry has a unique identifier (e.g., CVE-2021-44228 for Log4Shell) and describes the vulnerability, affected versions, and severity.

**CWE (Common Weakness Enumeration)**: A catalogue of common software weakness types ([cwe.mitre.org](https://cwe.mitre.org/)). Where CVE describes specific instances ("this version of this library has this vulnerability"), CWE describes classes of weakness ("SQL injection" is CWE-89; "Path Traversal" is CWE-22). CWE is useful for training developers to recognise and avoid vulnerability patterns.

**CVSS (Common Vulnerability Scoring System)**: A standardised scoring system that rates vulnerability severity from 0 (none) to 10 (critical) based on exploitability, impact, and scope ([NIST, 2019](https://nvd.nist.gov/vuln-metrics/cvss)).

### 8.1.2 The OWASP Top 10

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

## 8.2 Common Python Security Vulnerabilities

Five vulnerability classes recur consistently in Python codebases — and appear with measurable frequency in the code that AI assistants generate for them.

### 8.2.1 SQL Injection (CWE-89)

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

### 8.2.2 Command Injection (CWE-78)

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

### 8.2.3 Path Traversal (CWE-22)

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

    # is_relative_to checks path hierarchy, not string prefix, avoiding the
    # prefix-collision bug where /app/uploads_secret passes a startswith check
    if not requested_path.is_relative_to(UPLOAD_DIR.resolve()):
        raise PermissionError(f"Access denied: {filename}")

    with open(requested_path, "rb") as f:
        return f.read()
```

### 8.2.4 Insecure Deserialization (CWE-502)

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

### 8.2.5 Hardcoded Credentials (CWE-798)

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

## 8.3 PII and Credential Detection

### 8.3.1 GitLeaks

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

### 8.3.2 PII Detection

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

## 8.4 The Security Risk of AI-Generated Code

The vulnerability patterns in Section 8.2 appear in AI-generated code at measurable, reproducible rates — documented by independent studies as observed output, not theoretical risk. Two studies establish the evidence.

Perry et al. (2022) conducted a controlled experiment in which developers using GitHub Copilot for security-relevant programming tasks produced code with significantly more vulnerabilities than those who completed the same tasks unaided — and rated their AI-assisted code as *more* secure ([Perry et al., 2022](https://arxiv.org/abs/2211.03622)). The confidence inversion is the finding that matters: AI assistance raised perceived security while lowering actual security. Liu et al. (2023) found that 32.2% of ChatGPT-generated code samples produced incorrect outputs, and nearly half had maintainability issues detectable by standard static analysis ([Liu et al., 2023](https://arxiv.org/abs/2307.12596)). An engineer accepting the output without review ships these failures without knowing.

AI models are trained on the full corpus of publicly available code — which includes, at scale, code that is vulnerable. SQL string concatenation, `shell=True`, hardcoded credentials, and `debug=True` are all prevalent in public repositories; a model trained to complete code *plausibly* reproduces them *plausibly*. The confidence inversion Perry et al. documented is the sharpest illustration: the tool made developers feel more secure while making their code less so.

### 8.4.1 From Benign Prompt to Vulnerable Output

A prompt that contains no malicious intent can produce code that contains serious security defects. The two examples below use prompts that any developer might write on a normal working day.

**Example 1 — SQL Injection from a routine data retrieval prompt**

```
Prompt: "Write a Python function that retrieves a user's task history by their username."
```

A typical AI-generated response:

```python
def get_task_history(username: str) -> list[dict]:
    query = f"SELECT * FROM tasks WHERE assigned_to = '{username}'"
    return db.execute(query).fetchall()
```

This is CWE-89 (SQL Injection), OWASP A03. The f-string interpolation directly into the SQL query is exactly the pattern identified in Section 8.2.1. The prompt contained no instruction to use string formatting — the model reproduced a pattern it had encountered at high frequency in training data. The correct version uses a parameterised query:

```python
def get_task_history(username: str) -> list[dict]:
    return db.execute(
        "SELECT * FROM tasks WHERE assigned_to = %s", (username,)
    ).fetchall()
```

**Example 2 — Remote code execution exposure from a development convenience prompt**

```
Prompt: "Configure the Flask development server to make debugging easier."
```

A typical AI-generated response:

```python
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
```

This triggers Bandit B201 and B104. `debug=True` activates the Werkzeug interactive debugger, which permits arbitrary Python execution directly in the browser for anyone who can reach the server. `host="0.0.0.0"` binds to all network interfaces, extending that exposure beyond localhost. Shipped to a staging or production environment, this configuration enables unauthenticated remote code execution. The corrected version gates the flag on an environment variable:

```python
import os

if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug, host="127.0.0.1", port=5000)
```

### 8.4.2 Why Static Analysis Is Not Sufficient Alone

Static analysis tools — GitLeaks, Semgrep, Bandit — catch many of these patterns automatically. The SAST triage activity in the accompanying tutorial shows their limits: three vulnerability classes eluded automated detection in that exercise, including a hardcoded API key, a logged password, and an unauthenticated admin route. These are design-level and intent-level failures. No static analyser can detect that an endpoint lacks an access-control check without knowing what the access-control requirements were.

AI-generated code requires review rigour at least equal to code produced by an engineer unfamiliar with your security requirements. SAST tools establish a floor — they catch the patterns they were trained to recognise. Human review is the second line, responsible for the design-level issues that pattern matching cannot reach. The Perry et al. finding makes the stakes explicit: developers trusted AI-generated code *more* than warranted. The right response is systematic verification of every AI-generated security-relevant function — not trust, but structured scepticism.

---
