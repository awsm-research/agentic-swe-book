# Chapter 23: Multi-Agent Systems — Orchestration and Failure Containment

> *"The whole is more than the sum of its parts — but so is the failure."*
> — adapted from Aristotle

---

At 2:32 p.m. on 6 May 2010, the Dow Jones Industrial Average fell nearly a thousand points in minutes — the largest single-day point drop in its history at the time — and then recovered almost entirely within twenty minutes. No single cause was responsible. What investigators from the U.S. Securities and Exchange Commission and the Commodity Futures Trading Commission eventually documented was a cascade: a large sell order triggered automated trading systems, whose responses triggered other automated systems, whose responses triggered yet more, each one behaving rationally according to its own local rules while collectively amplifying an instability that no individual system had created and none could arrest (CFTC-SEC Joint Report, 2010). The Flash Crash was not a software bug. It was a multi-agent system failure — and it is the canonical demonstration of what happens when autonomous agents interact without adequate orchestration, shared state management, or failure containment.

---
