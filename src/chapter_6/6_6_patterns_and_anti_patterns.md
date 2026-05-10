## 6.6 Patterns and Anti-Patterns

Agentic software engineering has accumulated a short but instructive body of practice. Hassan (2025) identifies patterns that distinguish effective AI-native engineers from those who simply adopted new tools without changing their approach. Each pattern has a corresponding failure mode:

| Pattern | Anti-Pattern it corrects |
|---|---|
| Specification-first development | Prompt-and-pray |
| Verification-driven generation | Confidence by plausibility |
| Context file discipline | Context starvation |
| Incremental delegation | Overlong agentic sessions |
| Commit granularity | Ownership transfer |

### Patterns

**Specification-first development.** Write the complete specification before invoking the agent. Engineers who start typing a prompt and refine it as they go produce weaker output than engineers who think through the specification completely, then invoke the agent once.

**Verification-driven generation.** Write the verification criteria — test cases, behavioural requirements, security checks — before generating the implementation. This is the AI-native analogue of test-driven development: the tests define what "correct" means, so that when the agent generates an implementation you can immediately verify it.

**Context file discipline.** Maintain a project-level context file (`CLAUDE.md`, `.cursorrules`, or equivalent) that the agent reads before every task. Keep it current. An outdated context file that references a library the project no longer uses causes the agent to generate code using the wrong dependency — silently.

**Incremental delegation.** Start with smaller, well-bounded tasks and expand the delegation as you build confidence in the agent's output for your specific codebase. An agent that reliably generates correct tests for utility functions may still produce insecure code in authentication flows. Calibrate trust by task type, not globally.

**Commit granularity.** Commit AI-generated changes frequently and at a granularity that makes diffs reviewable. A single 2,000-line commit labelled "AI refactor" is unverifiable in practice. Fifty commits of 40 lines each, each with a clear message, are verifiable.

### Anti-Patterns

**Prompt-and-pray.** The engineer submits a vague prompt, receives output, ships it without systematic verification, and hopes the tests catch any issues. Tests catch syntactic and logical errors; they rarely catch specification mismatches, security weaknesses, or architectural violations.

**Confidence by plausibility.** AI-generated code looks correct because it is well-formatted, uses familiar patterns, and contains no obvious syntax errors. Plausibility is not correctness. The Stanford Copilot study is the controlled-trial version of this anti-pattern ([Perry et al., 2022](https://arxiv.org/abs/2211.03622)).

**Ownership transfer.** The engineer treats AI-generated code as the AI's code — "the agent wrote this, not me" — and applies less rigorous review than they would to their own work. This is both epistemically wrong (the engineer directed and accepted the output) and professionally dangerous (the engineer is responsible for what they commit, regardless of how it was generated).

**Context starvation.** The engineer invokes the agent with minimal context — no project conventions, no relevant file background, no architectural constraints — and then iterates through many rounds of refinement because the initial output was disconnected from the project's reality. The fix is to invest in context upfront, not to iterate expensively later.

**Overlong agentic sessions.** A developer asks an agent to implement a new authentication flow — "full OAuth2 integration with GitHub, including token refresh." The agent runs for 23 steps: reads the codebase, writes token storage code, adds callback handlers, modifies session middleware, generates tests. The tests pass. The developer commits. Two days later, in code review, a colleague spots that the token storage in step 4 wrote refresh tokens to a plain-text log file — and every subsequent step was built on that foundation. Unwinding it requires reworking 19 steps of layered changes.

The rule: establish a verification checkpoint after every 3–5 significant steps. Confirm the agent is still on track before continuing.

---
