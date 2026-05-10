## 9.8 AI-Generated Code Security

Agentic engineering introduces a second dimension of security concern beyond attacks *on* the agent: security vulnerabilities *in* the code the agent generates. The full taxonomy of vulnerability patterns and detection techniques is covered in Chapter 8; this section focuses on how the *throughput and autonomy* of agentic workflows amplify those risks.

### 9.8.1 AI Code is Not Inherently Secure

Large language models are trained on large corpora of code, which includes a significant proportion of insecure code. Studies have found that LLMs reproduce known vulnerability patterns from their training data — including SQL injection, path traversal, hardcoded credentials, and insecure cryptographic usage ([Pearce et al., 2022](https://arxiv.org/abs/2108.09293)).

The risk is compounded in agentic workflows: if an agent generates 500 lines of code autonomously and those lines are merged without review, a single vulnerable function may go undetected. The throughput advantage of agentic engineering can become a security liability if the verification step is omitted or rushed.

### 9.8.2 Common Vulnerability Patterns in AI-Generated Code

| Vulnerability | Example AI-generated pattern | OWASP category |
|---|---|---|
| SQL injection | String concatenation in queries instead of parameterised queries | A03: Injection |
| Path traversal | `open(f"uploads/{filename}")` without sanitising `filename` | A01: Broken Access Control |
| Hardcoded secrets | `API_KEY = "sk-..."` in source code | A02: Cryptographic Failures |
| Insecure deserialization | `pickle.loads(user_data)` | A08: Software Integrity Failures |
| Missing authentication | Endpoints without auth checks when the surrounding code has them | A07: Auth Failures |
| Overly broad CORS | `allow_origins=["*"]` | A05: Security Misconfiguration |
| Weak cryptography | `md5` or `sha1` for password hashing | A02: Cryptographic Failures |
| Command injection | `subprocess.run(f"cmd {user_input}", shell=True)` | A03: Injection |
| Insufficient input validation | Missing length or type checks on user-supplied values | A03: Injection |

AI models often generate code that *works correctly for the happy path* while missing security controls that a security-conscious engineer would add. The model is optimising for functional plausibility, not security completeness.

Empirical evidence confirms the risk. Pearce et al. ([2022](https://arxiv.org/abs/2108.09293)) found that GitHub Copilot generated vulnerable code in approximately 40% of security-relevant scenarios. Perry et al. ([2022](https://arxiv.org/abs/2211.03622)) found that developers using AI assistants were *more* likely to introduce security vulnerabilities than those without AI assistance, in part because they were more likely to trust generated code without review.

**Countermeasure: embed security constraints in every specification.** Before asking an agent to generate security-sensitive code, include explicit constraints in the specification:

```

## Security Constraints
- Use parameterised queries; never concatenate user input into SQL
- Never use shell=True with user-controlled input
- Validate and sanitise all user inputs before processing
- Use bcrypt for password hashing (work factor >= 12); never use MD5 or SHA-1
- Do not log sensitive data (passwords, tokens, PII)
- All file paths from user input must be resolved and validated against an allowed directory
```

These constraints act as a checklist the agent works against when generating code, and as a checklist reviewers work against when verifying it.

### 9.8.3 Security Review as a First-Class Verification Step

Make security review a mandatory, non-skippable step in the Verify phase of the agentic SDLC — the throughput advantage disappears the moment a vulnerability ships to production.

Practical measures:

1. **Automated SAST**: Run static analysis security tools (Bandit for Python, Semgrep, CodeQL) on all agent-generated code as part of CI. Fail the pipeline on high-severity findings.
2. **Agent-assisted security review**: Use a security-specialised subagent (with read-only permissions) to review generated code before it is committed. This is meta but effective: AI is better than humans at spotting certain classes of vulnerability when given an explicit checklist.
3. **Human security review for sensitive paths**: Authentication, authorisation, payment processing, and data handling code should always receive human security review, regardless of origin.
4. **Dependency scanning**: AI agents often add dependencies without evaluating their security posture. Run `pip audit`, `npm audit`, or equivalent after any agent-generated code that adds dependencies.

---
