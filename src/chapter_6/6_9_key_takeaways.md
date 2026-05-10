## 6.9 Key Takeaways

1. **A tool does not confer judgment.** Liu et al. (2023) found that 32.2% of AI-generated code samples were functionally incorrect; Perry et al. (2022) found that developers using AI produced more insecure code with greater confidence. Agentic tools amplify existing engineering capability — they do not substitute for it.

2. **An AI coding agent is not an LLM.** It is an LLM connected to tools, skills, connectors, and memory that allow it to take multi-step actions in the world. The difference is consequential: agents can make irreversible changes that require careful oversight.

3. **Terminal agents and AI-native IDEs serve different use cases.** Claude Code and Gemini CLI suit complex, flexible, terminal-centric work. Cursor and Windsurf suit sustained feature work where visual context alongside the AI conversation speeds verification. Neither is universally superior.

4. **The four components of an agent are tools, skills, connectors, and memory.** Tools are atomic actions. Skills are reusable multi-step capabilities. Connectors link the agent to external systems. Memory determines what persists across steps and sessions.

5. **The Agentic SDLC is Spec → Generate → Verify → Refine.** Generation is fast and cheap; specification and verification are where engineering judgment concentrates. Investing in specification quality is more efficient than iterating through poor generations.

6. **Common anti-patterns include prompt-and-pray, confidence by plausibility, and ownership transfer.** All three result from treating AI output as trustworthy by default rather than as a first draft requiring systematic verification.

7. **The 10x productivity claim is partially true and easily misread.** AI coding agents produce large gains for tasks they handle well — boilerplate, tests, documentation. They produce modest gains for tasks requiring deep judgment. The proportion of each in a given role determines the realistic productivity impact.

8. **Significant risks include overreliance, accountability gaps, IP and licence exposure, and prompt injection.** None of these are reasons to avoid agentic tools — they are reasons to use them with engineered controls.

9. **Accountability does not transfer to the AI.** The engineer who commits AI-generated code is responsible for that code. Review before commit is not optional.

---

### Review Questions

1. A team lead proposes giving a junior developer access to Claude Code to implement a new payment processing feature autonomously, with a final code review at the end. Using the concepts from this chapter — agent components, the Agentic SDLC, and human responsibility — identify three specific risks in this proposal and recommend concrete changes to the workflow that would mitigate each risk.

2. The anti-pattern "confidence by plausibility" describes engineers accepting AI output because it looks correct, rather than because it has been verified to be correct. Design a verification checklist for AI-generated authentication code. What specific categories of error would your checklist catch that automated tests might not?

3. Your team is considering adopting an AI-native IDE (Cursor or Windsurf) versus a terminal-based agent (Claude Code). The project is a 200-KLOC Python monolith with a comprehensive test suite and no AI tooling currently. What questions would you ask to determine which approach is more appropriate, and what evidence would lead you toward each choice?

4. A developer uses an AI agent to implement a database migration. The agent runs the migration against the staging database, observes success, and reports the task complete. The developer commits and deploys. The migration silently drops a column used by a feature not covered in the test suite. Who is responsible, and what process changes would have prevented the incident?

---
