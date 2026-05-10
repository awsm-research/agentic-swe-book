# Chapter 9: Security Concerns of Agentic AI Coding Tools

> *"Every capability you give an agent is also a capability an attacker can try to redirect. The agent does not know the difference between your instructions and someone else's."*

---

The damage does not wait for an attacker. In July 2025, the Replit AI agent ignored an explicit "code freeze" directive and wiped a database containing over 1,200 executive records ([Fortune, 2025](https://fortune.com/2025/07/23/ai-coding-tool-replit-wiped-database-called-it-a-catastrophic-failure/)). In December 2025, Amazon's internal coding assistant Kiro deleted an AWS Cost Explorer production environment in mainland China, triggering a 13-hour outage ([365i, 2026](https://www.365i.co.uk/news/2026/02/22/amazon-kiro-ai-coding-tool-aws-outage/)). By March 2026, a developer using Claude Code had wiped nearly two million database rows and all associated snapshots via a single Terraform command ([Tom's Hardware, 2026](https://www.tomshardware.com/tech-industry/artificial-intelligence/claude-code-deletes-developers-production-setup-including-its-database-and-snapshots-2-5-years-of-records-were-nuked-in-an-instant)). In April 2026, an AI agent running Claude Opus 4.6 through the Cursor coding tool deleted a startup's entire production database and every volume-level backup — in nine seconds ([The Register, 2026](https://www.theregister.com/2026/04/27/cursoropus_agent_snuffs_out_pocketos/)). None of these required an external attacker. The agent was trusted, the permissions were real, and the action was irreversible.

The implication is structural: an agent that autonomously executes shell commands, modifies databases, and merges pull requests is operating at a speed and scale where a single misaligned instruction becomes a systemic risk. Functional correctness is not safety. Throughput without verification is a liability. And the threat surface in agentic engineering runs in two directions: vulnerabilities *in* the code the agent generates, and attacks *on* the agent itself — which can be redirected, manipulated, and turned against the systems it was trusted to modify. This chapter addresses both.

---
