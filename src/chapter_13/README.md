# Chapter 13: The SE4AI Landscape — Software, Roles, and the New Discipline

> *"The most dangerous assumption you can make about an AI system is that it behaves like software."*
> — Kla Tantithamthavorn

---

In October 2019, a team of researchers at the University of California Berkeley published a paper in *Science* that should have been a crisis in software engineering ([Obermeyer et al., 2019](https://doi.org/10.1126/science.aax2342)). They had audited a commercial healthcare algorithm used by hundreds of US hospitals to allocate care management resources to patients with complex needs. The algorithm was technically correct: it predicted healthcare costs with high accuracy. The engineering team had done everything right by the standards of their discipline — the model was tested, validated, and deployed through a conventional software release process. The problem was that healthcare cost is a racially biased proxy for healthcare need. Black patients, who face greater barriers to accessing care, incur lower costs for the same severity of illness. The algorithm, faithfully optimising for costs, systematically underestimated the health needs of Black patients and directed resources away from them at scale. The researchers estimated that the bias reduced the proportion of Black patients identified for extra care from 46.5% to 17.7% — not because of a bug, not because of a data pipeline failure, but because the software engineering process had no mechanism for asking whether the metric being optimised was the right one.

This is the central problem that this part of the book addresses. The traditional software engineering discipline described in Chapters 1 through 12 is a mature field with well-developed practices for building systems that are correct, reliable, and maintainable. Those practices were designed for a world in which software does what it is told. Machine learning systems, large language model applications, and autonomous agents do not do what they are told — they do what they learn, what they infer, and what they decide. That difference requires a new layer of engineering discipline: SE4AI.

---
