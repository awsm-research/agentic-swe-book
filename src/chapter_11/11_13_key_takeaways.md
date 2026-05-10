## 11.13 Key Takeaways

1. **Production correctness is a property of the pipeline, not the code.** The CrowdStrike, Knight Capital, and SolarWinds incidents were all *correct code, broken delivery*. Closing the production gap is the job of release engineering.

2. **A version is a contract.** SemVer for libraries, CalVer for applications. ZeroVer, marketing versions, and floating tags break the contract and force consumers to pin defensively.

3. **Build, package, deploy are three distinct stages.** Conflating them — running `npm install` on the production host, editing config in place — destroys reproducibility, traceability, isolation, and reversibility in one move.

4. **Pin everything.** Lockfiles for libraries, digests for container images. Floating versions outsource your release engineering to strangers, as left-pad and colors.js made expensive to forget.

5. **An SBOM is a one-query answer to the next supply-chain incident.** Generate one on every build; cross-reference it against vulnerability databases in CI. xz-utils-shaped attacks become a Trivy report instead of a weekend.

6. **Containers are the dominant packaging format because they collapse dependency coordination into a build artefact.** That benefit is conditional on disciplined Dockerfile authorship — pinned bases, multi-stage builds, non-root users, health checks, signed images.

7. **Compose is for one host; that is enough for a great deal of production.** Compose buys you reproducible local development, integration testing, and small-scale production deployment. Larger deployments need an orchestrator; the principles of pinning, healthchecks, and immutable artefacts transfer unchanged.

8. **Deployment strategy determines the blast radius.** Rolling deploys are the default; canaries catch what staging does not; feature flags decouple deployment from release. CrowdStrike was an incident-of-staging-strategy as much as it was an incident-of-code.

9. **Production readiness is a checklist, not a vibe.** Liveness, readiness, structured logging, metrics, graceful shutdown, secrets management. Each item is a question an incident will eventually ask; the time to answer it is before the incident.

10. **AI-generated release infrastructure is the supply-chain risk of the next decade.** Pin, scan, sign, and require a human-reviewed release manifest. Agents make production-grade pipelines cheap; they do not make them free.

---

### Review Questions

1. Your team adopts a coding agent that produces a Dockerfile for a new Python service. The Dockerfile uses `FROM python:3.12`, runs `pip install -r requirements.txt` (no lockfile), copies the source, and ends with `CMD ["python", "main.py"]`. Identify five release-engineering defects in this Dockerfile, and explain the production failure mode each one will eventually cause.

2. A library you maintain ships a "patch" release that renames a public function. Within 48 hours, three downstream projects file bug reports because their builds are broken. Using SemVer's contract, explain (a) what rule was violated, (b) what the correct version number should have been, and (c) what your release pipeline could have done to catch the violation before publishing.

3. A teammate proposes deploying to production by SSH-ing to the host and running `git pull && docker compose up -d --build`. The argument is "it is simple, and we already trust the source repository." Identify which of the four release-engineering properties (reproducibility, traceability, isolation, reversibility) this approach loses, and describe a specific failure scenario for each.

4. The CrowdStrike incident pushed a malformed configuration file to all customers simultaneously. Design a deployment strategy that would have limited the blast radius to under 100,000 hosts, including what you would canary on, how long you would wait at each stage, and what signal would trigger a rollback. Be specific about the metrics you would watch.

5. An agent generates a Compose file for a `web + api + db` stack. The file omits health checks, uses `depends_on: [db]` (no condition), publishes `5432:5432` for the database, and stores the database password in `.env`, which has been committed. Write a code review comment for each defect that explains the *production failure mode*, not just the rule violated.

6. A vulnerability is announced in a transitive dependency three layers deep in your service. Compare two scenarios: (a) your team has pinned dependencies, generates SBOMs, and signs images; (b) your team uses floating versions, has no SBOM, and pulls images by tag. Walk through the first hour of incident response in each scenario and quantify, roughly, how long it takes to answer the question *are we vulnerable?*.

---
