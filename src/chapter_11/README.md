# Chapter 11: Software Versioning, Packaging, and Deployment

> *"You ship your org chart. You also ship your build pipeline."*
> — paraphrased from Conway's Law and every release engineer who has ever rolled back a Friday deploy

---

At 04:09 UTC on 19 July 2024, the cybersecurity firm CrowdStrike pushed a routine update to a configuration file used by its Falcon endpoint sensor on Windows. The file — a "channel file" with the extension `.sys` but no executable code — was malformed. Falcon's kernel-mode driver attempted to parse it on boot, dereferenced an invalid pointer, and triggered a bug-check. Approximately 8.5 million Windows hosts entered a continuous boot loop within seventy-eight minutes ([CrowdStrike, 2024](https://www.crowdstrike.com/falcon-content-update-remediation-and-guidance-hub/)). Delta Air Lines alone reported around USD 500 million in losses; hospitals diverted patients; emergency call centres in three US states went dark. The defective file was 42 kilobytes long. The release pipeline pushed it to every customer simultaneously, with no staged rollout, no canary, and no automatic rollback. The defect was tiny. The way it was shipped was the disaster.

---
