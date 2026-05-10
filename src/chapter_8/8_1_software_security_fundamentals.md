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
