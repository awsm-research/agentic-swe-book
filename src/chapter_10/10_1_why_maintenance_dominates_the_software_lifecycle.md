## 10.1 Why Maintenance Dominates the Software Lifecycle

Software engineering textbooks devote most of their pages to building new systems. Industry spends most of its money keeping old ones running. Empirical studies dating back to Lientz and Swanson's 1980 survey put post-deployment maintenance at 60–80% of total software cost over a system's lifetime ([Lientz & Swanson, 1980](https://dl.acm.org/doi/book/10.5555/539249)). Sommerville's 2016 textbook puts the figure at the high end of that range. The numbers have not improved in forty years — they have got worse, because systems live longer and integrate with more dependencies than they used to.

The British computer scientist Manny Lehman articulated why maintenance is unavoidable in his 1980 *Laws of Software Evolution* ([Lehman, 1980](https://ieeexplore.ieee.org/document/1456074)). Three of the laws matter for our purposes:

- **Continuing change** — a system used in the real world must be continually adapted, or it becomes progressively less useful.
- **Increasing complexity** — as a system evolves, its complexity rises unless explicit work is done to reduce it.
- **Declining quality** — the perceived quality of a system declines unless it is rigorously maintained and adapted to a changing environment.

Lehman's laws have a quiet implication: doing nothing is not stable. A codebase left alone gets worse, because the world around it keeps moving. Operating systems upgrade. Browsers deprecate APIs. Dependencies publish breaking changes. Regulators introduce new compliance requirements. Code that was correct in 2018 may be insecure, slow, or non-compliant in 2026 — without anyone editing a single line.

### The AI Inversion

For most of the field's history, the ratio of writing to reading code was roughly 1:10 — engineers spent ten times longer reading existing code than writing new code. Coding agents have inverted the writing speed, but they have done nothing to change the reading and reviewing burden. If an agent can produce a thousand lines of code in five minutes, the question is no longer "can we build it?" but "can we maintain it?". Every line generated becomes a future obligation. Knight Capital's USD 440 million loss came from forgetting to delete eight-year-old code; agentic systems can produce that volume of forgotten code in an afternoon.

---
