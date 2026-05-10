## 12.7 License Compliance Audit and Responsible AI Checklist

### 12.7.1 License Compliance Audit with pip-licenses

```bash
uv add --dev pip-licenses

# List all dependencies and their licenses
uv run pip-licenses --format=table

# Export to CSV for review
uv run pip-licenses --format=csv --output-file=licenses.csv

# Check for copyleft licenses that may require disclosure
uv run pip-licenses --fail-on="GPL;AGPL" --format=table
```

Sample output:
```
Name              Version  License
anthropic         0.28.0   MIT License
fastapi           0.111.0  MIT License
pytest            8.2.0    MIT License
sqlalchemy        2.0.30   MIT License
```

If any dependency has a GPL or AGPL licence, review whether your use triggers copyleft obligations.

### 12.7.2 Responsible AI Checklist for the Course Project

**Step 1: Generate a risk assessment with an AI assistant**

Paste the following prompt into any AI assistant (Claude, ChatGPT, Gemini), replacing the project block with your own project description:

**System prompt:**

<div class="admonish-prompt">

You are a responsible AI auditor with expertise in software engineering and AI ethics
frameworks. You provide concise, actionable risk assessments grounded in established
responsible AI principles (Fairness, Transparency, Accountability, Privacy, Safety,
Beneficence). Be specific to the technology stack and deployment context described.

</div>

**User:**

<div class="admonish-prompt">

Based on the project description below, provide a brief responsible AI risk assessment.
For each of the six principles — Fairness, Transparency, Accountability, Privacy,
Safety, and Beneficence — identify:

1. The primary risk for this project
2. A specific mitigation recommendation

Project:
Task Management API for software development teams.
- Built with Python and FastAPI
- Uses AI coding assistants for feature development
- Stores user data including email addresses and work activity
- Will be deployed as a SaaS product to paying customers

</div>

**Step 2: Complete the self-audit checklist**

Work through the checklist below for your own project. Each unchecked item is a gap to address before the project is considered responsible-AI-compliant.

<div class="admonish-prompt">

### Responsible AI Self-Audit

### Fairness
- [ ] Have we considered who may be disadvantaged by AI-generated code quality disparities?
- [ ] Have we tested the system with diverse inputs, not just the "happy path"?

### Transparency
- [ ] Is it documented which parts of the codebase are AI-generated?
- [ ] Are AI tools used in this project disclosed in project documentation?

### Accountability
- [ ] Has all AI-generated code been reviewed by a human engineer?
- [ ] Is there clear ownership of each component, including AI-generated ones?

### Privacy
- [ ] Have we verified that no PII or credentials were included in AI prompts?
- [ ] Does the system comply with applicable privacy regulations (GDPR, Privacy Act)?

### Security
- [ ] Has AI-generated code undergone security review (Bandit, manual review)?
- [ ] Have we run GitLeaks to ensure no credentials are in the repository?

### Licensing
- [ ] Have all dependencies been audited for licence compatibility?
- [ ] Is it clear that AI-generated code does not reproduce copylefted code?
</div>

---
