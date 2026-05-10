## 6.1 What Is Agentic Software Engineering?

*Agentic software engineering* is the practice of directing AI coding agents — autonomous systems that can plan, execute, and verify multi-step development tasks — as a central mode of producing and maintaining software. It is not a tool category or a product feature. It is a change in how the work of software engineering is organised.

The distinction from earlier forms of AI-assisted development is one of degree that becomes a difference in kind. A developer using GitHub Copilot still makes every decision: they read the suggestion, accept or reject it, move to the next line. The AI accelerates keystrokes. The developer's workflow is otherwise unchanged. An agentic workflow is different: the developer writes a specification, delegates the implementation to an agent that reads files, runs tests, and iterates autonomously, and then reviews the result. The bottleneck has moved from *writing* to *specifying and verifying*.

This shift has been underway since at least 2024, when tools like Devin ([Cognition, 2024](https://cognition.ai/blog/introducing-devin)), Claude Code (Anthropic, 2024), and Cursor demonstrated that an LLM with access to a shell and a file system could resolve real-world software issues with meaningful autonomy. SWE-bench — a benchmark of GitHub issues drawn from popular Python projects — provided a standardised measure: the fraction of issues an agent could fix without human intervention. Early scores in 2024 were below 20%. By mid-2025, leading agents exceeded 50% ([SWE-bench Leaderboard, 2025](https://www.swebench.com/)). The capability curve is steep.

*Agentic software engineering*, properly understood, is the discipline of working with these agents in a way that captures the productivity gains while enforcing the engineering standards that prevent the gaps from being amplified.

---
