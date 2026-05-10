## 11.2 Release Engineering as a Discipline

The term *release engineering* was coined by John O'Duinn and others at Mozilla in the mid-2000s to describe the work of getting Firefox builds reproducibly out the door. Adams and van der Hoek's *Modern Release Engineering* is the canonical academic reference ([Adams & van der Hoek, 2016](https://ieeexplore.ieee.org/document/7383668)); the Google SRE book makes the operational case ([Beyer et al., 2016](https://sre.google/sre-book/release-engineering/)). The two sources converge on four properties a healthy release pipeline buys you.

| Property | What it means | What goes wrong without it |
|---|---|---|
| **Reproducibility** | The same source produces the same artefact, today and in six months | A bug reported against v1.4.2 cannot be reproduced because the build no longer compiles |
| **Traceability** | Every running binary can be mapped back to a commit, a build, and a builder | An incident postmortem cannot determine which change caused the outage |
| **Isolation** | Each environment runs the artefact you intended, not whatever was on disk | A staging fix accidentally activates in production via a shared config file |
| **Reversibility** | A bad release can be rolled back in seconds, not hours | A failing deploy becomes a failing deploy *and* a failing rollback |

These are not aspirational qualities — they are operational necessities. Knight Capital's USD 440 million loss (Chapter 10) was a failure of *isolation*: half the fleet ran the new code, half ran the old. The CrowdStrike incident was a failure of *reversibility*: machines in a boot loop could not download the fix, so recovery required physical access to each host. SolarWinds (2020) was a failure of *traceability*: the malicious build artefact was indistinguishable from a legitimate one because the build environment itself had been compromised.

Release engineering is the discipline that makes these four properties cheap. The rest of the chapter is the practical machinery for doing so.

---
