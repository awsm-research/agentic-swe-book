## 11.10 Deployment Strategies and Risk

A working artefact and a working topology still need to *replace* the version that is running. The strategy you choose for that replacement determines the blast radius when something is wrong.

| Strategy | Mechanism | Downtime | Rollback speed | Risk profile |
|---|---|---|---|---|
| **Recreate** | Stop old, start new | Yes (seconds to minutes) | Slow — restart old | Internal tools, off-hours |
| **Rolling** | Replace instances one at a time | None | Medium — roll back one at a time | Default for most stateless services |
| **Blue-Green** | Run two full environments; swap traffic | None | Instant — swap back | High-stakes, infrequent releases |
| **Canary** | Send 1% / 5% / 25% of traffic to the new version | None | Instant for affected slice | Risky changes, large user base |
| **Feature flag** | Deploy code dark; enable per-user at runtime | None | Instant per-user | Decoupling deploy from release |

Three observations matter more than the table itself.

**Deployment is not the same as release.** A deployment ships code to production. A release exposes that code to users. Feature flags decouple the two: ship the code dark, validate that nothing is on fire, then turn it on for 1% of users, then 10%, then everyone. Most outages from "the deploy" are actually outages from "the release" — and a flag flip is an order of magnitude faster to revert than a redeploy.

**Canaries catch what staging does not.** Staging environments have synthetic traffic, a single test user, and a snapshot of production data from last Tuesday. Real users are weirder. A 1% canary exposes the new version to 1% of *real* traffic — the long-tail edge cases, the unexpected user-agent strings, the malformed Unicode in someone's display name. CrowdStrike's outage would have been an 85,000-host incident with a 1% canary instead of an 8.5-million-host incident.

**Rollback is a feature, not an afterthought.** If your deploy process cannot revert to the previous version in under five minutes, you do not have a deploy process — you have a one-way door. The first deploy of any new system should be followed immediately by a *rollback drill*: deliberately deploy a known-broken version, then revert. If the drill takes an hour, fix the process before shipping anything that matters.

---
