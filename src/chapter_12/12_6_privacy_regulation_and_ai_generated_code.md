## 12.6 Privacy Regulation and AI-Generated Code

A governance policy controls what engineers do with AI tools. Privacy regulation controls what the code those tools produce does with user data. The two obligations are independent — an organisation can have a perfect AI use policy and still ship GDPR-non-compliant code.

### 12.6.1 Key Regulations

**GDPR (General Data Protection Regulation)** — applies to any organisation that processes personal data of EU residents, regardless of where the organisation is located ([EU Regulation 2016/679](https://gdpr.eu/)).

Key obligations relevant to AI-generated code:
- **Data minimisation**: Collect only the data you need. AI-generated code that logs request bodies may inadvertently collect PII.
- **Purpose limitation**: Use data only for the purpose collected. AI-generated analytics code may aggregate data in ways that exceed the original purpose.
- **Right to erasure ("right to be forgotten")**: Code must support deleting a user's personal data on request. AI-generated CRUD code frequently omits this.
- **Data portability**: Code must support exporting a user's personal data in a structured format.
- **Lawful basis**: You need a lawful basis (consent, contract, legitimate interest) to process personal data. AI-generated signup flows may not implement consent collection correctly.

**CCPA (California Consumer Privacy Act)** — similar to GDPR in scope, applies to businesses collecting personal information of California residents ([California Attorney General](https://oag.ca.gov/privacy/ccpa)).

**Australian Privacy Act 1988** — applies to Australian Government agencies and organisations with annual turnover over $3 million ([OAIC](https://www.oaic.gov.au/privacy/the-privacy-act)).

### 12.6.2 Worked Scenario: AI-Generated User Deletion Endpoint

**Prompt to AI assistant:**
```
Add a DELETE /users/{user_id} endpoint to our FastAPI application that removes 
a user from the database.
```

**AI-generated code (non-compliant):**
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

This deletes the `User` row but fails GDPR requirements in several ways:

| GDPR Requirement | Gap in Generated Code |
|---|---|
| Cascade deletion | User's tasks, comments, audit logs may retain PII |
| Audit trail | No record that deletion was requested and completed |
| Third-party notification | External services (email, analytics) may still hold the user's data |
| Verification | No check that the requester is authorised to delete this account |
| Confirmation | No confirmation email to document the right-to-erasure request |

**Improved specification for AI:**
```
Add a GDPR-compliant DELETE /users/{user_id} endpoint:
- Verify the caller is the user themselves (JWT claim) or an admin
- Cascade delete: remove all tasks, comments, and audit logs owned by the user
- Anonymise rather than delete activity that is required for financial records (replace 
  user name/email with "Deleted User [id]" in order history)
- Create a DeletionRequest audit record with: user_id, requester_id, timestamp, 
  cascaded_tables
- Return 204 No Content on success
- Send a confirmation email to the user's address before deleting it
Assume: User, Task, Comment, AuditLog, DeletionRequest SQLAlchemy models; 
        send_email(to, subject, body) utility function available
```

The difference between the two prompts is one sentence of context per GDPR requirement. That is the engineering cost of compliance — not implementing deletion differently, but specifying it precisely enough that the generated code actually does it.

### 12.6.3 PII in AI Prompts

GDPR Article 28 requires a Data Processing Agreement (DPA) with any third party that processes personal data on your behalf. Most major AI providers offer DPAs, but these must be executed before sending personal data.

**Do not send to external AI APIs (without a DPA and privacy review):**
- Names, email addresses, phone numbers
- IP addresses (considered personal data under GDPR)
- User-generated content that may contain PII
- Authentication tokens or session identifiers

**Automated PII detection before AI prompts:**

```bash
uv add --dev presidio-analyzer presidio-anonymizer
```

```python
# pii_guard.py
import anthropic
from presidio_analyzer import AnalyzerEngine

analyzer = AnalyzerEngine()
client = anthropic.Anthropic()


def safe_ai_request(prompt: str, model: str = "claude-haiku-4-5-20251001") -> str:
    """Reject prompts that contain detectable PII."""
    results = analyzer.analyze(text=prompt, language="en")
    
    pii_found = [r.entity_type for r in results if r.score > 0.7]
    if pii_found:
        raise ValueError(
            f"Prompt contains potential PII ({pii_found}). "
            "Remove PII before sending to external AI services."
        )
    
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


# Usage
try:
    result = safe_ai_request(
        "Fix the bug in this function. The user john.doe@example.com reported it."
    )
except ValueError as e:
    print(f"PII guard blocked request: {e}")
    # Sanitise the prompt: remove the email address before retrying
```

---
