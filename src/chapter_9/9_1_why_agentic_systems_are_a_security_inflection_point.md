## 9.1 Why Agentic Systems Are a Security Inflection Point

Software security has always been a discipline of controlling what systems can do — validating inputs, enforcing access control, isolating processes, auditing actions. The underlying principle has not changed: a system should be able to do exactly what it is designed to do, and nothing more.

What *has* changed with AI agents is the *attack surface* and the *blast radius* of a successful attack.

In a traditional web application, an attacker who finds a SQL injection vulnerability can read or modify the database. That is serious — but the boundary is the database. In an agentic system, an attacker who successfully influences the agent's behaviour may be able to:

- Read and exfiltrate any file the agent has access to
- Write malicious code into the codebase and commit it
- Push changes to a production branch
- Create GitHub issues or pull requests that appear to come from the agent's principal
- Call external APIs with the agent's credentials
- Spawn additional agents to amplify the attack

The agent's power — its ability to take multi-step, autonomous actions across multiple tools — is precisely what makes it dangerous when that power is misdirected. Security for agentic systems is a design constraint — one that must shape every architectural decision from the first line of configuration, not be retrofitted after the agent works.

---
