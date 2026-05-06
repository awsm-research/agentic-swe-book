# Tutorial 10: Licences, Privacy, and Responsible AI in Practice

By the end of this tutorial you will have: audited your project's Python dependencies for copyleft obligations and confirmed the scan fails on a known GPL package; identified GDPR compliance gaps in an AI-generated API endpoint and corrected them with a precise specification; built a standalone PII detection guard that blocks personal data from reaching external AI prompts; extended it with automatic anonymisation; and completed a structured responsible AI checklist with concrete remediation actions for your course project.

**Concepts covered:** Licence compliance auditing, GDPR right-to-erasure, data portability, PII detection, presidio-analyzer, prompt anonymisation, responsible AI self-audit, CI/CD compliance gates

**Format:** Hands-on lab | **Duration:** ~2 hours | **Tool:** pip-licenses · presidio-analyzer · uv · GitHub Actions / GitLab CI

---

## Outline

- [Part A: Licence Compliance Audit](#part-a-licence-compliance-audit) *(~25 min)*
- [Part B: GDPR Gaps in AI-Generated Code](#part-b-gdpr-gaps-in-ai-generated-code) *(~25 min)*
- [Part C: Automated PII Detection in AI Prompts](#part-c-automated-pii-detection-in-ai-prompts) *(~35 min)*
- [Part D: Responsible AI Audit](#part-d-responsible-ai-audit) *(~15 min)*
- [Part E: Add Licence Auditing to CI/CD](#part-e-add-licence-auditing-to-cicd) *(~20 min)*

## Prerequisites

- [uv](https://docs.astral.sh/uv/) installed (Tutorial 1) — manages Python and virtual environments
- A Python project with a `pyproject.toml` and `uv.lock` (the Task Management API from Tutorial 6 is ideal)
- A Git repository ([GitHub](https://github.com/) or [GitLab](https://gitlab.com/)) with push access

---

## Learning Objectives

By the end of this tutorial, you will be able to:

1. Run a licence compliance audit on Python dependencies and detect copyleft obligations using pip-licenses.
2. Identify GDPR compliance gaps in AI-generated code by comparing output against specific regulatory requirements.
3. Build a PII detection guard using presidio-analyzer that raises an error when personal data is detected in a prompt.
4. Extend the guard with automatic anonymisation to replace PII with entity-type placeholders.
5. Complete a structured responsible AI checklist and write concrete remediation actions for each gap.
6. Integrate licence auditing into a GitHub Actions or GitLab CI pipeline as a merge gate.

---

## Part A: Licence Compliance Audit

*(~25 min)*

Every Python project accumulates dependencies, and those dependencies carry licences. Permissive licences (MIT, Apache 2.0) impose no constraints on how you use the software. Copyleft licences (GPL, AGPL) require derivative works — and in some cases SaaS services built on them — to also be open source. Most teams discover a GPL dependency during legal review before acquisition, not before shipping. `pip-licenses` surfaces these obligations in seconds.

### Step 1: Install pip-licenses

```bash
uv add --dev pip-licenses
```

### Step 2: Run the audit

```bash
uv run pip-licenses --format=table
```

Abbreviated output for a typical FastAPI project:

```
Name              Version  License
fastapi           0.111.0  MIT License
httpx             0.27.0   BSD License
pytest            8.2.0    MIT License
sqlalchemy        2.0.30   MIT License
starlette         0.37.2   BSD License
```

### Step 3: Export to JSON for review

```bash
uv run pip-licenses --format=json --output-file=licenses.json
```

Open `licenses.json` and check two things: how many distinct licence families are present, and whether any dependency is labelled `UNKNOWN` — those require manual investigation because pip-licenses cannot determine their terms.

### Step 4: Gate on copyleft licences

```bash
uv run pip-licenses --fail-on="GPL;AGPL" --format=table
echo "Exit code: $?"   # 0 = clean, 1 = copyleft dependency found
```

The `--fail-on` flag accepts a semicolon-separated list of licence-name substrings. `"GPL"` matches GPL v2, GPL v3, and GNU General Public License; `"AGPL"` matches the Affero variants.

### Step 5: Activity — Introduce and detect a copyleft violation

`mysql-connector-python` ships under GPL 2.0. Add it to a throwaway branch, confirm the scan catches it, then remove it:

```bash
git checkout -b test/copyleft-check
uv add mysql-connector-python
uv run pip-licenses --fail-on="GPL;AGPL" --format=table
echo "Exit code: $?"   # expect 1
```

```bash
uv remove mysql-connector-python
uv run pip-licenses --fail-on="GPL;AGPL" --format=table
echo "Exit code: $?"   # expect 0
git checkout main
git branch -d test/copyleft-check
```

Now run the scan on your actual project. If any dependency carries a GPL or AGPL licence, record: the package name, the licence identifier, and whether your use triggers the copyleft obligation (hint: for AGPL, network access is enough).

---

## Part B: GDPR Gaps in AI-Generated Code

*(~25 min)*

AI assistants generate to the prompt, not to the regulation. A prompt that says "delete a user from the database" produces code that deletes a database row — it does not produce code that satisfies GDPR's right to erasure, because the prompt said nothing about GDPR. Identifying these gaps before code reaches production is a skill the regulatory environment now requires.

### Step 1: Generate the non-compliant endpoint

Paste the following into any AI assistant:

**Prompt:**
```
Add a DELETE /users/{user_id} endpoint to our FastAPI application that removes
a user from the database.
```

The AI will generate something close to:

```python
@app.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}
```

Save this as `endpoints/users_delete_v1.py`.

### Step 2: Map the GDPR gaps

Review the generated code against GDPR's right-to-erasure requirements (Article 17). For each row below, mark whether the generated code satisfies it:

| GDPR Requirement | Satisfied? | Gap in Generated Code |
|---|---|---|
| Cascade deletion of all user PII | No | Related tables (tasks, comments, audit logs) retain PII |
| Audit trail of the deletion request | No | No `DeletionRequest` record created |
| Authorisation verification | No | Any authenticated caller can delete any account |
| Financial record handling | No | PII in order history must be anonymised, not deleted |
| Confirmation to the user | No | No confirmation email sent before deletion |

Zero of the five requirements are satisfied.

### Step 3: Write a compliant specification

Save the following as `endpoints/users_delete_v2_prompt.txt`, then submit it to any AI assistant:

**Prompt:**
```
Add a GDPR-compliant DELETE /users/{user_id} endpoint to our FastAPI application:
- Verify the caller is the user themselves (JWT sub claim matches user_id) or has admin role
- Cascade delete: remove all Task, Comment, and AuditLog rows owned by user_id
- Anonymise rather than delete any OrderHistory rows: replace user name and email
  with "Deleted User [user_id]" to preserve financial records
- Create a DeletionRequest record with: user_id, requester_id, timestamp, list of
  cascaded tables
- Return 204 No Content on success
- Send a confirmation email to the user's address before deleting it, using the
  send_email(to, subject, body) utility already in the project
Assume SQLAlchemy models: User, Task, Comment, AuditLog, OrderHistory, DeletionRequest.
```

Re-run the gap table against the new output. All five requirements should now be addressed.

### Step 4: Activity — Write a compliant export endpoint

GDPR Article 20 (data portability) requires that users can export all their personal data in a structured, machine-readable format on request. Write a prompt for a `GET /users/{user_id}/export` endpoint. Your prompt must specify:

1. Which tables contain the user's personal data and must be included in the export
2. That the response format is JSON
3. That only the user themselves (or an admin) can trigger the export
4. A rate limit — one export request per 24 hours per user

Submit the prompt, then verify: does the generated endpoint include data from all relevant tables? Does it check authorisation? Does it enforce the rate limit? Document any remaining gap and write the revised specification that closes it.

---

## Part C: Automated PII Detection in AI Prompts

*(~35 min)*

GDPR Article 28 requires a Data Processing Agreement with any third party that processes personal data on your behalf. Every engineer who pastes a bug report containing a user's email address into an AI chat window is potentially processing personal data without a DPA. Manual vigilance does not scale. Automated detection does.

[Microsoft's Presidio](https://microsoft.github.io/presidio/) is an open source PII detection and anonymisation library that uses named entity recognition to identify over 50 entity types — email addresses, phone numbers, IP addresses, passport numbers, credit card numbers, and more. It runs entirely locally: no data leaves the machine.

### Step 1: Install presidio and its language model

```bash
uv add --dev presidio-analyzer presidio-anonymizer
uv run python -m spacy download en_core_web_lg
```

`presidio-analyzer` performs detection; `presidio-anonymizer` performs redaction. Both depend on spaCy for named entity recognition. `en_core_web_lg` is the large English model presidio uses by default (~550 MB). If disk space is constrained, substitute `en_core_web_sm` — accuracy is lower but sufficient for testing.

### Step 2: Run your first scan

Save as `test_presidio.py`:

```python
# test_presidio.py
from presidio_analyzer import AnalyzerEngine

analyzer = AnalyzerEngine()
text = "Contact john.doe@example.com or call +61 412 345 678 about the incident on 192.168.1.1"
results = analyzer.analyze(text=text, language="en")

for r in results:
    print(f"{r.entity_type:20s}  score={r.score:.2f}  '{text[r.start:r.end]}'")
```

```bash
uv run python test_presidio.py
```

Expected output:

```
EMAIL_ADDRESS         score=1.00  'john.doe@example.com'
PHONE_NUMBER          score=0.75  '+61 412 345 678'
IP_ADDRESS            score=0.95  '192.168.1.1'
```

Each result carries an entity type, a confidence score, and character offsets into the original string. The `score` is a float between 0 and 1 — results below 0.7 are typically too uncertain to act on.

### Step 3: Build pii_guard.py

Save the following as `pii_guard.py` in your project root:

```python
# pii_guard.py
from presidio_analyzer import AnalyzerEngine

_analyzer = AnalyzerEngine()


def check_for_pii(text: str, threshold: float = 0.7) -> list[str]:
    """Return detected PII entity types above the confidence threshold."""
    results = _analyzer.analyze(text=text, language="en")
    return [r.entity_type for r in results if r.score > threshold]


def safe_prompt(text: str) -> str:
    """Return the prompt unchanged, or raise ValueError if PII is detected."""
    found = check_for_pii(text)
    if found:
        raise ValueError(
            f"Prompt contains potential PII ({found}). "
            "Remove personal data before sending to external AI services."
        )
    return text
```

`check_for_pii` is the detection primitive — it returns a list of entity type strings, empty if none are found. `safe_prompt` wraps it for use at call sites: pass any string through it before forwarding to an AI API.

### Step 4: Test the guard

Save as `test_pii_guard.py`:

```python
# test_pii_guard.py
from pii_guard import safe_prompt

# Should block — contains an email address
try:
    safe_prompt("Fix the bug reported by john.doe@example.com in the checkout flow")
    print("FAIL: should have raised ValueError")
except ValueError as e:
    print(f"Blocked (expected): {e}")

# Should pass — no PII
result = safe_prompt("Fix the null pointer exception in the checkout flow")
print(f"Passed (expected): returned {len(result)} chars")
```

```bash
uv run python test_pii_guard.py
```

Expected:

```
Blocked (expected): Prompt contains potential PII (['EMAIL_ADDRESS']). Remove personal data before sending to external AI services.
Passed (expected): returned 51 chars
```

### Step 5: Activity — Extend with anonymisation

Blocking forces engineers to redact manually before retrying. Anonymisation automates the redaction, replacing each detected entity with its entity-type label. Create `anonymize_prompt.py`:

```python
# anonymize_prompt.py
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

_analyzer = AnalyzerEngine()
_anonymizer = AnonymizerEngine()


def anonymize_prompt(text: str) -> str:
    """Replace detected PII with <ENTITY_TYPE> placeholders."""
    results = _analyzer.analyze(text=text, language="en")
    if not results:
        return text
    return _anonymizer.anonymize(text=text, analyzer_results=results).text
```

Verify the output:

```python
from anonymize_prompt import anonymize_prompt

original = "The user john.doe@example.com on 192.168.1.1 reported a crash in checkout"
print(anonymize_prompt(original))
# Expected: "The user <EMAIL_ADDRESS> on <IP_ADDRESS> reported a crash in checkout"
```

Then extend `pii_guard.py` with a third function:

```python
import logging

_log = logging.getLogger(__name__)


def sanitize_prompt(text: str) -> str:
    """Anonymise PII in text and log a warning when redaction occurs."""
    from anonymize_prompt import anonymize_prompt
    found = check_for_pii(text)
    if not found:
        return text
    sanitized = anonymize_prompt(text)
    _log.warning("PII redacted from prompt: %s → anonymised before sending", found)
    return sanitized
```

`sanitize_prompt` is the production-safe wrapper: it never blocks, always logs, and returns a redacted string the caller can forward to an AI API. Verify it against the same test strings used in Step 4.

---

## Part D: Responsible AI Audit

*(~15 min)*

### Step 1: Generate an AI risk assessment

Open any AI assistant. Set the system prompt and submit the user message below, replacing the example project description with your own course project:

**System prompt:**
```
You are a responsible AI auditor with expertise in software engineering and AI ethics
frameworks. You provide concise, actionable risk assessments grounded in established
responsible AI principles (Fairness, Transparency, Accountability, Privacy, Safety,
Beneficence). Be specific to the technology stack and deployment context described.
```

**User:**
```
Based on the project description below, provide a brief responsible AI risk assessment.
For each of the six principles — Fairness, Transparency, Accountability, Privacy,
Safety, and Beneficence — identify:

1. The primary risk for this project
2. A specific mitigation recommendation

Project:
[Paste your project description here: technology stack, what user data is stored,
who uses the system, and whether AI coding assistants were used in development]
```

Save the output as `docs/responsible-ai-assessment.md`.

### Step 2: Activity — Complete the checklist and write remediations

Work through the responsible AI self-audit checklist from Section 10.7.2 for your own project. For every unchecked item, write one concrete remediation action — a specific code change, process change, or documentation addition that closes the gap.

Record your findings in a table saved alongside the AI assessment:

| Checklist Item | Status | Remediation Action |
|---|---|---|
| All AI-generated code has been reviewed by a human engineer | ✗ | Add mandatory AI-code reviewer label to PR template; configure CODEOWNERS |
| No PII was included in AI prompts | ✗ | Wrap all AI calls through `sanitize_prompt()` from Part C |
| Dependencies audited for licence compatibility | ✓ | — |
| ... | ... | ... |

At minimum, one row should reference the PII guard from Part C and one should reference the GDPR specification work from Part B. If every checklist item is already satisfied, revisit Section 10.6.1 and verify whether your data deletion and export paths address all five GDPR requirements.

---

## Part E: Add Licence Auditing to CI/CD

*(~20 min)*

The licence scan is most useful when it runs on every pull request that changes dependencies. A package whose licence changes in a patch release slips past manual review; automated gating catches it before it merges.

### Step 1: GitHub Actions configuration

Create `.github/workflows/compliance.yml`:

```yaml
name: Compliance Checks

on:
  pull_request:
    paths:
      - 'pyproject.toml'
      - 'uv.lock'

jobs:
  licence-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install pip-licenses
        run: pip install pip-licenses

      - name: Audit dependency licences
        run: |
          pip-licenses --format=json --output-file=licenses.json
          pip-licenses --fail-on="GPL;AGPL" --format=table

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: licence-report
          path: licenses.json
```

The job triggers only when `pyproject.toml` or `uv.lock` changes. The `if: always()` on the artifact upload preserves the licence report for review even when the job fails.

### Step 2: GitLab CI configuration

Add to `.gitlab-ci.yml`:

```yaml
licence-audit:
  stage: test
  image: python:3.12-slim
  before_script:
    - pip install pip-licenses
  script:
    - pip-licenses --format=json --output-file=licenses.json
    - pip-licenses --fail-on="GPL;AGPL" --format=table
  artifacts:
    when: always
    paths:
      - licenses.json
    expire_in: 30 days
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      changes:
        - pyproject.toml
        - uv.lock
```

### Step 3: Activity — Trigger and fix the pipeline

1. Create a feature branch and add `mysql-connector-python` to `pyproject.toml`
2. Push and open a pull/merge request
3. Confirm: the `licence-audit` job fails and names the GPL licence in its output
4. Remove the package, push again, confirm the job passes
5. Download the `licenses.json` artifact from the passing run — verify it lists all project dependencies and contains no `UNKNOWN` licence entries

If your project already has a passing CI configuration from Tutorial 9, add the `licence-audit` job alongside the existing `sast` job so both run in parallel on every pull request.

---

## References

- [pip-licenses](https://github.com/raimon49/pip-licenses)
- [Microsoft Presidio](https://microsoft.github.io/presidio/)
- [GDPR full text — EUR-Lex](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32016R0679)
- [FOSSA — automated licence compliance](https://fossa.com/)
- [TLDR Legal — plain-English licence summaries](https://tldrlegal.com/)
- [Australian Privacy Act 1988 — OAIC](https://www.oaic.gov.au/privacy/the-privacy-act)
