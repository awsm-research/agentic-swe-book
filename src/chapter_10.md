# Chapter 10: Licenses, Ethics, and Responsible AI

> *"The question is not whether AI systems can do things. The question is who is responsible when they do them badly."*

---

## Learning Objectives

By the end of this chapter, you will be able to:

1. Explain the major categories of software licenses and their obligations.
2. Navigate the copyright ambiguity around AI-generated code.
3. Apply a responsible AI framework to evaluate an AI-enabled system.
4. Identify sources of bias in AI coding assistants and their practical consequences.
5. Describe key governance frameworks for responsible AI development.
6. Conduct a basic license and responsible AI audit of a software project.

---

## 10.1 Intellectual Property and Code Ownership

Intellectual property (IP) law governs who owns creative works, including software. Understanding software IP is essential for every engineer — particularly in the context of open source software and AI-generated code.

### 10.1.1 Copyright

Copyright is the primary form of IP protection for software. In most jurisdictions, copyright in software belongs to its author (or the author's employer if created in the course of employment) automatically upon creation — no registration required.

Copyright grants the owner exclusive rights to:
- Copy the software
- Distribute the software
- Create derivative works
- Display or perform the software publicly

For software, this means that you cannot legally copy, distribute, or build upon someone else's code without either a licence from the copyright holder or an applicable exception (such as fair use/fair dealing).

**Work for hire**: In most employment relationships, software created by an employee in the course of their duties is owned by the employer, not the employee. Contractors may retain ownership depending on the contract.

### 10.1.2 Patents

Software patents protect specific technical implementations or processes. They are controversial in the software industry — critics argue they stifle innovation by allowing trivial ideas to be patented. Their relevance varies significantly by jurisdiction (more significant in the US than in Europe).

### 10.1.3 Trade Secrets

Some software (particularly proprietary algorithms and training data) is protected as a trade secret rather than through copyright or patents. Trade secret protection requires the owner to take reasonable measures to keep the information confidential.

---

## 10.2 Software Licenses

A software licence is a legal instrument through which a copyright holder grants others permission to use, copy, modify, and/or distribute their software under specified conditions.

### 10.2.1 Proprietary Licenses

Proprietary licences retain all rights for the copyright holder. Users may run the software but cannot view the source code, modify it, or redistribute it. Examples: Microsoft Windows, Adobe Photoshop, most commercial SaaS products.

### 10.2.2 Open Source Licenses

Open source licences grant users the freedom to use, study, modify, and distribute the software. The [Open Source Initiative](https://opensource.org/osd) (OSI) maintains the definitive list of approved open source licences.

Open source licences fall broadly into two categories:

**Permissive licences** allow the software to be used in almost any way, including incorporation into proprietary software:

| Licence | Key Conditions | Common Use Cases |
|---|---|---|
| MIT | Include copyright notice | Most popular for libraries |
| Apache 2.0 | Include copyright notice; patent grant | Corporate-friendly projects |
| BSD (2/3-clause) | Include copyright notice | BSD-origin software |

**Copyleft licences** require that derivative works be distributed under the same licence:

| Licence | Key Conditions | Common Use Cases |
|---|---|---|
| GPL v2/v3 | Derivative works must be GPL | Linux kernel, GNU tools |
| LGPL | Weaker copyleft; allows linking without GPL obligation | Libraries intended for wide use |
| AGPL | GPL + network use triggers copyleft | SaaS applications |

**The copyleft risk**: If your proprietary application incorporates AGPL-licensed code, the AGPL requires you to release your application's source code. Mixing GPL-licensed libraries into a proprietary codebase creates licence compatibility problems.

### 10.2.3 Creative Commons

Creative Commons licences are primarily for non-software creative works (documentation, datasets, design assets). They are not appropriate for software source code — use an OSI-approved licence instead.

### 10.2.4 Choosing a License

For open source projects:
- **MIT or Apache 2.0**: Maximise adoption; allow use in proprietary software
- **GPL**: Ensure all derivatives remain open source
- **AGPL**: Ensure even SaaS deployments that use the software release modifications

For internal/proprietary projects: use a proprietary licence (explicitly state no licence is granted if you want to be clear).

**No licence = all rights reserved**: If you publish code without a licence, copyright law gives no-one the right to use it, even if it is publicly visible.

---

## 10.2.5 Real-World Licensing Case Studies

Understanding licensing obligations through concrete cases is more effective than reading licence texts in isolation.

**Case 1: The AGPL Trap — MongoDB and Elastic**

MongoDB originally used the AGPL licence for its core database. When MongoDB's commercial competitiveness was threatened by cloud providers offering MongoDB-as-a-service without contributing back, MongoDB switched to the Server Side Public License (SSPL), which extends the AGPL copyleft to *all* software used to offer the database as a service. Elastic made a similar move with Elasticsearch in 2021.

*Lesson for engineers*: If your SaaS product depends on an AGPL or SSPL component, the copyleft may require you to release your entire application's source code. Check licences before adopting new dependencies.

**Case 2: The GPL Enforcement — BusyBox and Android**

The Software Freedom Conservancy has pursued numerous enforcement actions against device manufacturers shipping Linux (GPL v2) and BusyBox (GPL v2) without distributing corresponding source code, as required by the GPL. High-profile cases include actions against Best Buy, Samsung, and several router manufacturers.

*Lesson for engineers*: GPL compliance for embedded or distributed software (firmware, IoT devices) requires distributing the source code or making it available on written request. Many organisations fail this requirement and only discover the problem during acquisition due diligence.

**Case 3: The GitHub Copilot Class Action**

In 2022, a class action lawsuit was filed against GitHub, Microsoft, and OpenAI alleging that Copilot reproduces copyrighted code from training data — including code under licences that require attribution and source disclosure — without attribution ([Doe v. GitHub, 2022](https://githubcopilotlitigation.com/)). As of 2024–2025, this litigation is ongoing.

*Lesson for engineers*: AI tools trained on copyrighted code may reproduce that code verbatim. Several organisations (Samsung, Apple, JPMorgan) have restricted or banned external AI coding tools to mitigate this risk. Understand your organisation's policy before using AI tools with proprietary code.

**Case 4: The Copyleft Compatibility Matrix**

Not all open source licences are compatible with each other. The following matrix summarises common compatibility issues:

| Combining | With GPL v3 | With Apache 2.0 | With MIT |
|---|---|---|---|
| **GPL v3** | Compatible | Compatible (Apache can be relicensed under GPL v3) | Compatible |
| **Apache 2.0** | Compatible | Compatible | Compatible |
| **GPL v2 only** | **Incompatible** | **Incompatible** | Compatible |
| **AGPL v3** | Compatible | Compatible | Compatible |

The GPL v2 / GPL v3 incompatibility matters because the Linux kernel (GPL v2 only) cannot legally incorporate code from GPL v3 projects. This has practical consequences for kernel modules and embedded Linux distributions.

*Lesson for engineers*: Before incorporating a library, check that its licence is compatible with your project's licence and all other dependencies. Tools like [FOSSA](https://fossa.com/) and [TLDR Legal](https://tldrlegal.com/) can help.

---

## 10.3 AI-Generated Code and Copyright

The copyright status of AI-generated code is one of the most actively litigated and debated questions in technology law as of 2024–2025.

### 10.3.1 The Current Legal Landscape

**Human authorship requirement**: In most jurisdictions, copyright requires human authorship. The United States Copyright Office has repeatedly held that works produced autonomously by AI without human creative input are not copyrightable ([USPTO, 2024](https://www.copyright.gov/ai/)). This means purely AI-generated code may have no copyright holder — it may be in the public domain.

**Human-AI collaboration**: Where a human makes meaningful creative choices in directing, selecting, and refining AI output, the resulting work may be copyrightable as a human-authored work. The threshold for "meaningful creative contribution" is not yet clearly defined.

**Training data and copyright**: Several lawsuits have been filed alleging that AI models trained on copyrighted code without permission infringe copyright ([GitHub Copilot class action, 2022](https://githubcopilotlitigation.com/)). These cases are unresolved as of this writing.

### 10.3.2 Practical Guidance

In the absence of settled law, the pragmatic guidance is:

1. **For critical proprietary systems**: Treat AI-generated code with the same IP review you would apply to any third-party code. Understand what training data the model was trained on, and whether it may reproduce copyrighted code verbatim.

2. **For licence compliance**: AI coding assistants trained on copyleft code could theoretically reproduce that code in their outputs, creating a hidden licence obligation. Some organisations have adopted policies requiring a human review of AI-generated code before incorporating it.

3. **For attribution**: If an AI assistant produces code that is substantially similar to an existing open source project, treat it as if it were copied from that project and apply the appropriate licence obligations.

4. **Keep documentation**: Record which parts of your codebase are AI-generated, which tools were used, and which specifications were provided. This documentation supports IP claims and audits.

---

## 10.4 Responsible AI Principles

Responsible AI is the discipline of designing, developing, and deploying AI systems in ways that are safe, fair, transparent, and accountable. It has moved from academic concern to regulatory requirement: the EU AI Act ([European Parliament, 2024](https://www.europarl.europa.eu/news/en/press-room/20240308IPR19015/artificial-intelligence-act-meps-adopt-landmark-law)), the US Executive Order on Safe, Secure, and Trustworthy AI ([White House, 2023](https://www.whitehouse.gov/briefing-room/presidential-actions/2023/10/30/executive-order-on-the-safe-secure-and-trustworthy-development-and-use-of-artificial-intelligence/)), and the Australian Government's AI Ethics Framework ([DISER, 2019](https://www.industry.gov.au/publications/australias-artificial-intelligence-ethics-framework)) all impose obligations on organisations developing or deploying AI.

Key responsible AI principles ([Jobin et al., 2019](https://www.nature.com/articles/s42256-019-0088-2)):

| Principle | Description |
|---|---|
| **Fairness** | AI systems should not discriminate unfairly against individuals or groups |
| **Transparency** | The behaviour and decision-making of AI systems should be explainable |
| **Accountability** | There must be clear human responsibility for AI system outcomes |
| **Privacy** | AI systems should respect individuals' privacy rights |
| **Safety** | AI systems should not cause harm |
| **Beneficence** | AI systems should benefit individuals and society |

### 10.4.1 Fairness and Bias in AI Coding Assistants

AI coding assistants can exhibit bias in several ways:

**Code quality disparity**: Research has found that AI coding tools perform better on code written in widely-used languages and paradigms. Code in less common languages, frameworks, or domains receives lower quality suggestions — creating a "rich get richer" dynamic where well-resourced projects benefit more from AI assistance ([Dakhel et al., 2023](https://arxiv.org/abs/2304.10778)).

**Representation in training data**: AI models trained on public code repositories inherit the demographics and conventions of those repositories. If the training data overrepresents certain coding styles, conventions, or languages, the model's suggestions will reflect those biases.

**Accessibility**: AI coding tools require reliable internet access, modern hardware, and often paid subscriptions. This creates barriers for developers in lower-income countries or those working in resource-constrained environments.

### 10.4.2 Transparency and Explainability

When AI systems make decisions or generate outputs that affect people, those affected often have a right to understand how the decision was made. For AI coding assistants, relevant questions include:

- What training data was used?
- How does the model decide what code to generate?
- When the model generates insecure code, can this be detected and explained?

Current AI coding assistants offer limited explainability. This is an active research area, and engineers should be cautious about deploying AI decision-making in contexts where explainability is legally or ethically required.

### 10.4.3 Accountability

The "accountability gap" in AI systems refers to the challenge of assigning responsibility when an AI system causes harm. For software engineers, the practical principle is:

**You are accountable for AI-generated code you ship.** The fact that an AI assistant generated a vulnerable function does not transfer responsibility to the AI vendor. The engineer who reviewed, accepted, and deployed the code is responsible.

This accountability principle reinforces the evaluation-driven approach of Chapter 7: you cannot disclaim responsibility for code you did not evaluate.

---

## 10.5 Organisational AI Governance

As AI tools proliferate in software teams, organisations need governance frameworks to manage the associated risks.

### 10.5.1 AI Use Policies

An AI use policy defines:
- Which AI tools are approved for use (and for what purposes)
- What data may and may not be sent to AI services
- How AI-generated code must be reviewed before production use
- How AI tool usage should be documented

**Example policy clauses:**

> "Engineers may use approved AI coding assistants (see the approved tools list) for code generation. All AI-generated code must be reviewed by a human engineer before merging to the main branch."

> "No customer PII, authentication credentials, or proprietary algorithm details may be included in prompts to external AI services."

> "Engineers must disclose AI tool usage in pull request descriptions when AI-generated code constitutes more than 20% of the change."

### 10.5.2 Risk Tiering

The EU AI Act introduced a risk-tiered framework for AI systems ([European Parliament, 2024](https://www.europarl.europa.eu/news/en/press-room/20240308IPR19015/artificial-intelligence-act-meps-adopt-landmark-law)):

| Risk Tier | Examples | Requirements |
|---|---|---|
| **Unacceptable risk** | Social scoring, real-time biometric surveillance | Prohibited |
| **High risk** | Medical devices, hiring decisions, credit scoring | Conformity assessment, transparency, human oversight |
| **Limited risk** | Chatbots, deepfakes | Transparency obligations |
| **Minimal risk** | AI coding assistants, spam filters | Voluntary codes of conduct |

For most software development use cases, AI coding assistants fall in the "minimal risk" tier. However, if you are *building* a high-risk AI system (medical diagnosis, credit scoring, automated hiring), significantly stricter requirements apply.

### 10.5.3 Documentation and Audit Trails

Responsible AI deployment requires documentation:
- **Model cards** ([Mitchell et al., 2019](https://arxiv.org/abs/1810.03993)): Structured documents describing an AI model's intended use, limitations, evaluation results, and ethical considerations
- **Datasheets for datasets** ([Gebru et al., 2018](https://arxiv.org/abs/1803.09010)): Structured documents describing a dataset's composition, collection process, and known limitations
- **System cards**: Documentation of a deployed AI system, including the models used, their risk assessments, and mitigation measures

---

## 10.6 Privacy Regulation and AI-Generated Code

Privacy regulations impose obligations that interact directly with AI-generated code. Engineers who generate data-handling code with AI tools must understand whether the output is compliant.

### 10.6.1 Key Regulations

**GDPR (General Data Protection Regulation)** — applies to any organisation that processes personal data of EU residents, regardless of where the organisation is located ([EU Regulation 2016/679](https://gdpr.eu/)).

Key obligations relevant to AI-generated code:
- **Data minimisation**: Collect only the data you need. AI-generated code that logs request bodies may inadvertently collect PII.
- **Purpose limitation**: Use data only for the purpose collected. AI-generated analytics code may aggregate data in ways that exceed the original purpose.
- **Right to erasure ("right to be forgotten")**: Code must support deleting a user's personal data on request. AI-generated CRUD code frequently omits this.
- **Data portability**: Code must support exporting a user's personal data in a structured format.
- **Lawful basis**: You need a lawful basis (consent, contract, legitimate interest) to process personal data. AI-generated signup flows may not implement consent collection correctly.

**CCPA (California Consumer Privacy Act)** — similar to GDPR in scope, applies to businesses collecting personal information of California residents ([California Attorney General](https://oag.ca.gov/privacy/ccpa)).

**Australian Privacy Act 1988** — applies to Australian Government agencies and organisations with annual turnover over $3 million ([OAIC](https://www.oaic.gov.au/privacy/the-privacy-act)).

### 10.6.2 Worked Scenario: AI-Generated User Deletion Endpoint

A common GDPR compliance gap in AI-generated code is the missing right-to-erasure implementation.

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

This specification produces code that satisfies the right-to-erasure obligation. The gap between the two versions illustrates why privacy compliance cannot be delegated to AI without privacy-aware specifications.

### 10.6.3 PII in AI Prompts

Sending personal data to external AI APIs creates its own compliance risk. GDPR Article 28 requires a Data Processing Agreement (DPA) with any third party that processes personal data on your behalf. Most major AI providers offer DPAs, but these must be executed before sending personal data.

**Do not send to external AI APIs (without a DPA and privacy review):**
- Names, email addresses, phone numbers
- IP addresses (considered personal data under GDPR)
- User-generated content that may contain PII
- Authentication tokens or session identifiers

**Automated PII detection before AI prompts:**
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

## 10.7 Tutorial: License Compliance Audit and Responsible AI Checklist

### 10.7.1 License Compliance Audit with pip-licenses

```bash
pip install pip-licenses

# List all dependencies and their licenses
pip-licenses --format=table

# Export to CSV for review
pip-licenses --format=csv --output-file=licenses.csv

# Check for copyleft licenses that may require disclosure
pip-licenses --fail-on="GPL;AGPL" --format=table
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

### 10.7.2 Responsible AI Checklist for the Course Project

```python
# responsible_ai_audit.py
import anthropic

client = anthropic.Anthropic()

RESPONSIBLE_AI_CHECKLIST = """
Fairness:
- [ ] Have we considered who may be disadvantaged by AI-generated code quality disparities?
- [ ] Have we tested the system with diverse inputs, not just the "happy path"?

Transparency:
- [ ] Is it documented which parts of the codebase are AI-generated?
- [ ] Are AI tools used in this project disclosed in project documentation?

Accountability:
- [ ] Has all AI-generated code been reviewed by a human engineer?
- [ ] Is there clear ownership of each component, including AI-generated ones?

Privacy:
- [ ] Have we verified that no PII or credentials were included in AI prompts?
- [ ] Does the system comply with applicable privacy regulations (GDPR, Privacy Act)?

Security:
- [ ] Has AI-generated code undergone security review (Bandit, manual review)?
- [ ] Have we run GitLeaks to ensure no credentials are in the repository?

Licensing:
- [ ] Have all dependencies been audited for licence compatibility?
- [ ] Is it clear that AI-generated code does not reproduce copylefted code?
"""


def generate_responsible_ai_report(project_description: str) -> str:
    """Generate a responsible AI assessment for a project."""
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""You are a responsible AI auditor. Based on the project description
below, provide a brief responsible AI risk assessment. For each of the six principles
(Fairness, Transparency, Accountability, Privacy, Safety, Beneficence), identify:
1. The primary risk for this project
2. A specific mitigation recommendation

Project:
{project_description}""",
            }
        ],
    )
    return response.content[0].text


if __name__ == "__main__":
    project = """
    Task Management API for software development teams.
    - Built with Python and FastAPI
    - Uses AI coding assistants for feature development (chapters 5-8 of this course)
    - Stores user data including email addresses and work activity
    - Will be deployed as a SaaS product to paying customers
    """

    print("RESPONSIBLE AI ASSESSMENT")
    print("=" * 60)
    print(generate_responsible_ai_report(project))
    print()
    print("SELF-AUDIT CHECKLIST")
    print("=" * 60)
    print(RESPONSIBLE_AI_CHECKLIST)
```

