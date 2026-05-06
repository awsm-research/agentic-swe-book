# Chapter 9 — Agent Security

Examples extracted from Chapter 9 (prompt injection, confused deputy,
agent attack vectors, defensive architecture).

## Files

| File | Demonstrates |
|---|---|
| `malicious_code_comment.py` | Indirect prompt injection embedded in a code comment (§9.3.3) |
| `safe_user_input.py` | Structured message roles + length validation pattern (§9.3.4) |
| `sanitise_for_agent.py` | Trust-boundary wrapper for external content (§9.6.3) |
| `structured_output.py` | Pydantic schema constrains agent output (§9.7.2) |
| `test-runner.md` | Maliciously-modified subagent config (§9.5.3) |
| `deployer.md` | Restricted-permission subagent config (§9.6.2) |

## How to run

These are illustrative snippets. `safe_user_input.py` requires `pip install
anthropic` and an API key; the others are read-only references.
