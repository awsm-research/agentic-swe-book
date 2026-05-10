# Chapter 8: Security of AI-Generated Code

> *"Security is not a product, but a process."*
> — Bruce Schneier

---

Veracode's 2025 GenAI Code Security Report tested more than 100 large language models across security-sensitive coding tasks and found that 45% of AI-generated code samples introduce at least one OWASP Top 10 vulnerability — and that AI-generated code contains 2.74 times more security flaws than human-written equivalents ([Veracode, 2025](https://www.veracode.com/resources/analyst-reports/2025-genai-code-security-report/)). The models improved at producing syntactically correct, functional code; they did not improve at producing secure code. Georgia Tech's Vibe Security Radar, launched in May 2025 to formally track CVEs attributable to AI coding tools, documented 78 confirmed AI-linked vulnerabilities through March 2026 — 43 of them rated Critical or High severity — with the pace accelerating sharply: March 2026 alone recorded 35 CVEs, more than the entirety of the second half of 2025 combined ([Georgia Tech, 2026](https://research.gatech.edu/bad-vibes-ai-generated-code-vulnerable-researchers-warn)). The pattern is structural, not incidental. An AI assistant that generates hundreds of lines per session, at a pace no manual reviewer can match, turns every untriaged output into a potential entry point. Functional correctness is not security. Throughput without verification is a liability.

---
