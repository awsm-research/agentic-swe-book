## 11.12 AI-Native Considerations — Agents That Package and Ship

Coding agents are good at producing release infrastructure that looks right. They are less good at producing release infrastructure that *is* right. The gap matters because release infrastructure is the last line of defence between a defect and a customer.

### Where Agents Reliably Mislead

Six recurring failure patterns in agent-generated packaging:

1. **Floating base images.** `FROM node:20` instead of `FROM node:20.11.1-alpine3.19@sha256:...`. The Dockerfile builds today; in three months the same Dockerfile produces a different image and your reproducibility is gone.
2. **Root user by default.** No `USER` directive, so the container runs as root. A vulnerability in the application becomes a kernel-adjacent compromise.
3. **Secrets in environment variables and `.env`.** The agent solves "the database needs a password" by putting the password in `.env` — and `.env` ends up committed because the agent did not also update `.gitignore`.
4. **Missing health checks.** Compose `depends_on` without `condition: service_healthy`; Dockerfiles without `HEALTHCHECK`; the orchestrator cannot tell ready from broken.
5. **One-stage builds.** The full build toolchain ships in the final image. A Node.js service that should be 150 MB is 1.2 GB and ships `gcc`, `python3`, and the build user's name.
6. **Generated CI manifests with broad permissions.** GitHub Actions workflows with `permissions: write-all` and `pull_request_target: ` triggers, which are textbook supply-chain risk. A 2023 Dependabot study found that more than a third of agent-suggested workflows had at least one of these patterns.

### Three Guardrails

Treat these as non-negotiable. Each catches a category that agents reliably miss.

- **Pinning is a contract.** The agent's Dockerfiles, lockfiles, and Compose files pass review only if every dependency is pinned by version *and* — for container images — by digest. CI fails the build if `:latest` or unpinned `node:20` appears anywhere.
- **Policy as code.** Run `hadolint` on every Dockerfile, `trivy image` on every produced image, and `checkov` or `conftest` on every Compose file, in CI. The agent does not get to decide what is acceptable; the policy file does. The cost is a few seconds per build; the saving is roughly the cost of one avoided incident per quarter.
- **A human-reviewed release manifest.** The boundary between "agent-written" and "production-shipped" is a human signing off on what is being released. The release manifest is short — version, commit, image digest, SBOM, change summary — and it is reviewed by a person, not a bot. This is the same pattern as code review, applied to the artefact rather than to the source.

### Why This Matters More Than It Used To

A human engineer writing a Dockerfile by hand produces one Dockerfile a week. A coding agent can produce twenty in a morning. The probability that *one of them* contains a release-engineering mistake — an unpinned base image, a missed health check, a leaked secret — does not stay at 10% per Dockerfile when the volume is twentyfold. The aggregate exposure scales linearly.

The CrowdStrike incident took down 8.5 million hosts because *one* configuration file was malformed and *one* release pipeline pushed it everywhere. The defect rate per file did not need to be high. It needed to be non-zero and uncaught. Agentic codebases do not lower the defect rate; they raise the volume. Release-engineering rigour is what keeps the resulting incident rate flat instead of climbing in proportion to the agent's output.

---
