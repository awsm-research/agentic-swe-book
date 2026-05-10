## 12.4 Responsible AI Principles

Responsible AI has moved from academic concern to regulatory requirement: the EU AI Act ([European Parliament, 2024](https://www.europarl.europa.eu/news/en/press-room/20240308IPR19015/artificial-intelligence-act-meps-adopt-landmark-law)), the US Executive Order on Safe, Secure, and Trustworthy AI ([White House, 2023](https://www.whitehouse.gov/briefing-room/presidential-actions/2023/10/30/executive-order-on-the-safe-secure-and-trustworthy-development-and-use-of-artificial-intelligence/)), and the Australian Government's AI Ethics Framework ([DISER, 2019](https://www.industry.gov.au/publications/australias-artificial-intelligence-ethics-framework)) all impose obligations on organisations developing or deploying AI.

Key responsible AI principles ([Jobin et al., 2019](https://www.nature.com/articles/s42256-019-0088-2)):

| Principle | Description |
|---|---|
| **Fairness** | AI systems should not discriminate unfairly against individuals or groups |
| **Transparency** | The behaviour and decision-making of AI systems should be explainable |
| **Accountability** | There must be clear human responsibility for AI system outcomes |
| **Privacy** | AI systems should respect individuals' privacy rights |
| **Safety** | AI systems should not cause harm |
| **Beneficence** | AI systems should benefit individuals and society |

### 12.4.1 Fairness and Bias in AI Coding Assistants

AI coding assistants can exhibit bias in several ways:

**Code quality disparity**: Research has found that AI coding tools perform better on code written in widely-used languages and paradigms. Code in less common languages, frameworks, or domains receives lower quality suggestions — creating a "rich get richer" dynamic where well-resourced projects benefit more from AI assistance ([Dakhel et al., 2023](https://arxiv.org/abs/2304.10778)).

**Representation in training data**: AI models trained on public code repositories inherit the demographics and conventions of those repositories. If the training data overrepresents certain coding styles, conventions, or languages, the model's suggestions will reflect those biases.

**Accessibility**: AI coding tools require reliable internet access, modern hardware, and often paid subscriptions. This creates barriers for developers in lower-income countries or those working in resource-constrained environments.

### 12.4.2 Transparency and Explainability

When AI systems make decisions or generate outputs that affect people, those affected often have a right to understand how the decision was made. For AI coding assistants, relevant questions include:

- What training data was used?
- How does the model decide what code to generate?
- When the model generates insecure code, can this be detected and explained?

Current AI coding assistants offer limited explainability. This is an active research area, and engineers should be cautious about deploying AI decision-making in contexts where explainability is legally or ethically required.

### 12.4.3 Accountability

The "accountability gap" in AI systems refers to the challenge of assigning responsibility when an AI system causes harm. For software engineers, the practical principle is:

**You are accountable for AI-generated code you ship.** The fact that an AI assistant generated a vulnerable function does not transfer responsibility to the AI vendor. The engineer who reviewed, accepted, and deployed the code is responsible.

This accountability principle reinforces the evaluation-driven approach of Chapter 7: you cannot disclaim responsibility for code you did not evaluate.

---
