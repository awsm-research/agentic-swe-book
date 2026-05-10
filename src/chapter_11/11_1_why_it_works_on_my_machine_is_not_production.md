## 11.1 Why "It Works on My Machine" Is Not Production

Most production incidents are not caused by code that was wrong. They are caused by code that was correct on the developer's laptop and behaved differently somewhere else. The CrowdStrike outage is an extreme version of this pattern: the channel file passed CrowdStrike's internal validation, was correctly signed, and loaded without complaint on the engineer's test machine. It crashed every Windows kernel that mounted it in production.

The distance between *runs on my machine* and *runs in production* is what release engineering exists to manage. That distance has several axes, and each one is a place where a deploy can go wrong:

- **Environment drift** — the production OS is a different version, has different libraries installed, or runs at higher load than the developer's machine.
- **Dependency drift** — a library version that was pulled at build time is no longer the version present at deploy time.
- **Configuration drift** — secrets, feature flags, and tuning parameters differ between environments and are not version-controlled with the code.
- **Data drift** — production data has shapes the developer never saw: empty strings, multi-byte characters, rows older than the schema migration that was supposed to backfill them.
- **Topology drift** — production runs many instances behind a load balancer, with retries, timeouts, and partial failures that single-process testing never exercises.

A single untested combination of these — an unstaged channel file, a Postgres minor version that auto-upgraded the production volume, a Node base image that silently flipped from `node:20` to `node:22` — is enough to take down a service.

### The Production Gap

Call the union of these axes the *production gap*. The job of a release pipeline is to close the gap, or at least to surface it before customers do. Every practice in this chapter — versioning, lockfiles, immutable artefacts, containers, Compose files, canary deploys — is a tool for shrinking one of those axes. None of them shrinks all five. A team that masters Docker but ignores deployment strategy will still ship CrowdStrike-shaped incidents; a team with a flawless canary process but unpinned base images will still wake up to a Postgres major-version surprise on Monday morning.

The chapter is organised as a walk down those axes, in the order an artefact travels: build, package, deploy, operate.

---
