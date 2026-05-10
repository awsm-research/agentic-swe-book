## 9.4 The Confused Deputy Problem

### 9.4.1 The Classical Problem

The *confused deputy problem* ([Hardy, 1988](https://dl.acm.org/doi/10.1145/54289.871709)) is a well-known security concept: a privileged program (the "deputy") is tricked by an unprivileged caller into using its privileges on the caller's behalf, doing something the caller could not have done directly.

A classic example: a compiler with write access to a billing file is asked by a user to compile a program, but the user names the output file as the billing file. The compiler, which has permission to write billing files, overwrites it — not because it was instructed to by an authorised principal, but because it used its privilege based on untrusted input.

### 9.4.2 Agents as Confused Deputies

AI agents are extremely good confused deputies. They hold credentials, tool access, and permissions granted by the legitimate user. When an indirect prompt injection attack succeeds, the agent uses those legitimate privileges to execute the attacker's instructions.

```
Legitimate permission: Agent may create GitHub pull requests
Attacker's goal:       Create a PR containing a backdoor in the authentication code
Attack vector:         Malicious instruction embedded in a web page the agent browses
Result:                Agent creates a PR containing a backdoor — legitimately signed,
                       from a trusted account, with the agent's usual commit style
```

The PR will arrive looking exactly like one the developer requested. Code review by a human would be required to detect it — which is why human-in-the-loop review for high-consequence actions is a required architectural control, not an optional safeguard.

### 9.4.3 Ambient Authority and POLA

The confused deputy problem is fundamentally caused by *ambient authority* — the agent has permissions simply by virtue of running, regardless of whether any specific action has been authorised by the legitimate principal. The principle of least privilege (POLA — Principle Of Least Authority) directly addresses this.

In an agentic context, POLA means:
- Grant each agent and subagent only the permissions needed for its specific task
- Grant permissions for the duration of a task, not permanently
- Require explicit user confirmation before any irreversible action
- Log every permission use so that deviations are detectable

Chapter 6 showed how to implement this technically via subagent `tools` allowlists and `permission_mode`. This chapter explains *why* those controls matter from a security standpoint: they reduce the blast radius of a confused deputy attack to only the tools the compromised agent was allowed to use.

---
