## 6.4 AI as the New Teammate

Hassan's central argument is that the correct mental model for AI coding tools is not *tool* but *teammate* — a collaborator with specific capabilities, blind spots, and tendencies that an effective engineer must learn to work with ([Hassan, 2025](https://agenticse-book.github.io/pdf/AgenticSE_Book.pdf)).

The tool metaphor leads engineers to treat AI as passive: you invoke it, it does a thing, you evaluate the output. The teammate metaphor leads engineers to think about communication, context, delegation, and feedback loops. A good teammate is not one who executes instructions blindly; it is one who understands the goal, flags when the instructions conflict with the goal, and asks for clarification before going wrong.

**Context matters as much as instructions.** Compare two ways to kick off the same task:

> *"Add input validation to the user registration endpoint."*

> *"Add input validation to the `/api/register` endpoint in `auth/views.py`. The project uses Pydantic v2 for validation — see `schemas/user.py` for existing patterns. Reject emails that are not RFC 5322 compliant, passwords under 12 characters, and usernames containing special characters other than hyphens and underscores. Do not touch the rate-limiting middleware in `auth/middleware.py`. Tests live in `tests/test_auth.py`."*

The first prompt produces code that validates *something*. The second produces code that validates *exactly what you need*. The difference is not in the model — it is in the brief. Effective AI-native engineers invest in context files (`CLAUDE.md`, `.cursorrules`) that provide this background automatically before every task.

**Feedback is iterative.** You would not expect a teammate to get a complex task right on the first attempt. The Spec → Generate → Verify → Refine loop (see Section 6.5) is the professional workflow for collaborating with an AI teammate — not a workaround for the AI's limitations, but the natural structure of iterative collaborative work.

**Strengths and blind spots are learnable.** AI coding agents are reliably strong at: boilerplate generation, test scaffolding, translating between languages, finding related code, explaining unfamiliar codebases, and writing documentation. They are reliably weak at: multi-file refactors without explicit context, maintaining invariants across a long session, security reasoning without explicit prompting, and understanding implicit organisational conventions. Knowing the map of strengths and weaknesses allows you to delegate effectively and verify precisely where it matters.

**Responsibility does not transfer.** A teammate's mistake on a project does not absolve the person who assigned the work. The same holds for AI. If an agent introduces a security vulnerability and you commit it without review, the vulnerability is yours. Section 6.8 returns to this in detail.

---
