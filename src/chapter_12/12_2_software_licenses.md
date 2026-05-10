## 12.2 Software Licenses

A software licence is a legal instrument through which a copyright holder grants others permission to use, copy, modify, and/or distribute their software under specified conditions.

### 12.2.1 Proprietary Licenses

Proprietary licences retain all rights for the copyright holder. Users may run the software but cannot view the source code, modify it, or redistribute it. Examples: Microsoft Windows, Adobe Photoshop, most commercial SaaS products.

### 12.2.2 Open Source Licenses

Open source licences grant users the freedom to use, study, modify, and distribute the software. The [Open Source Initiative](https://opensource.org/osd) (OSI) maintains the definitive list of approved open source licences.

Open source licences fall broadly into two categories:

**Permissive licences** allow the software to be used in almost any way, including incorporation into proprietary software:

| Licence | Key Conditions | Common Use Cases |
|---|---|---|
| MIT | Include copyright notice | Most popular for libraries |
| Apache 2.0 | Include copyright notice; patent grant | Corporate-friendly projects |
| BSD (2/3-clause) | Include copyright notice | BSD-origin software |

**Copyleft licences** require that derivative works be distributed under the same licence:

| Licence | Key Conditions | Common Use Cases |
|---|---|---|
| GPL v2/v3 | Derivative works must be GPL | Linux kernel, GNU tools |
| LGPL | Weaker copyleft; allows linking without GPL obligation | Libraries intended for wide use |
| AGPL | GPL + network use triggers copyleft | SaaS applications |

**The copyleft risk**: If your proprietary application incorporates AGPL-licensed code, the AGPL requires you to release your application's source code. Mixing GPL-licensed libraries into a proprietary codebase creates licence compatibility problems.

### 12.2.3 Creative Commons

Creative Commons licences are primarily for non-software creative works (documentation, datasets, design assets). They are not appropriate for software source code — use an OSI-approved licence instead.

### 12.2.4 Choosing a License

For open source projects:
- **MIT or Apache 2.0**: Maximise adoption; allow use in proprietary software
- **GPL**: Ensure all derivatives remain open source
- **AGPL**: Ensure even SaaS deployments that use the software release modifications

For internal/proprietary projects: use a proprietary licence (explicitly state no licence is granted if you want to be clear).

**No licence = all rights reserved**: If you publish code without a licence, copyright law gives no-one the right to use it, even if it is publicly visible.

### 12.2.5 Real-World Licensing Case Studies

**Case 1: The AGPL Trap — MongoDB and Elastic**

MongoDB originally used the AGPL licence for its core database. When MongoDB's commercial competitiveness was threatened by cloud providers offering MongoDB-as-a-service without contributing back, MongoDB switched to the Server Side Public License (SSPL), which extends the AGPL copyleft to *all* software used to offer the database as a service. Elastic made a similar move with Elasticsearch in 2021.

*Lesson for engineers*: If your SaaS product depends on an AGPL or SSPL component, the copyleft may require you to release your entire application's source code. Check licences before adopting new dependencies.

**Case 2: The GPL Enforcement — BusyBox and Android**

The Software Freedom Conservancy has pursued numerous enforcement actions against device manufacturers shipping Linux (GPL v2) and BusyBox (GPL v2) without distributing corresponding source code, as required by the GPL. High-profile cases include actions against Best Buy, Samsung, and several router manufacturers.

*Lesson for engineers*: GPL compliance for embedded or distributed software (firmware, IoT devices) requires distributing the source code or making it available on written request. Many organisations fail this requirement and only discover the problem during acquisition due diligence.

**Case 3: The GitHub Copilot Class Action**

In 2022, a class action lawsuit was filed against GitHub, Microsoft, and OpenAI alleging that Copilot reproduces copyrighted code from training data — including code under licences that require attribution and source disclosure — without attribution ([Doe v. GitHub, 2022](https://githubcopilotlitigation.com/)). As of 2024–2025, this litigation is ongoing.

*Lesson for engineers*: AI tools trained on copyrighted code may reproduce that code verbatim. Several organisations (Samsung, Apple, JPMorgan) have restricted or banned external AI coding tools to mitigate this risk. Understand your organisation's policy before using AI tools with proprietary code.

**Case 4: The Copyleft Compatibility Matrix**

Not all open source licences are compatible with each other. The following matrix summarises common compatibility issues:

| Combining | With GPL v3 | With Apache 2.0 | With MIT |
|---|---|---|---|
| **GPL v3** | Compatible | Compatible (Apache can be relicensed under GPL v3) | Compatible |
| **Apache 2.0** | Compatible | Compatible | Compatible |
| **GPL v2 only** | **Incompatible** | **Incompatible** | Compatible |
| **AGPL v3** | Compatible | Compatible | Compatible |

The GPL v2 / GPL v3 incompatibility matters because the Linux kernel (GPL v2 only) cannot legally incorporate code from GPL v3 projects. This has practical consequences for kernel modules and embedded Linux distributions.

*Lesson for engineers*: Before incorporating a library, check that its licence is compatible with your project's licence and all other dependencies. Tools like [FOSSA](https://fossa.com/) and [TLDR Legal](https://tldrlegal.com/) can help.

---
