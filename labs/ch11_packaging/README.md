# Chapter 11 — Packaging and Deployment

Standalone snippets from Chapter 11 (Section 11.7 Dockerfile anatomy, Section
11.9 three-tier Compose example). The fully runnable bookshop stack lives in
`../tut11_compose/`.

## Files

| File | Source |
|---|---|
| `Dockerfile.example` | Multi-stage Dockerfile illustration (§11.7) |
| `compose.example.yaml` | Three-tier Compose file with placeholder digests (§11.9) |
| `env.example` | `.env` template for Compose substitution |

The digests in these files are placeholders (`@sha256:e4ab...`, `@sha256:1f1f...`).
They are intentionally illustrative — the full tutorial-11 lab uses digests
that students substitute via `docker inspect`.
