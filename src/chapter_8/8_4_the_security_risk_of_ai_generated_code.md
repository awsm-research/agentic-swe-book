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
