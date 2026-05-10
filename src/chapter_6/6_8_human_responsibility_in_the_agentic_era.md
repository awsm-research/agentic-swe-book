## 6.8 Human Responsibility in the Agentic Era

The human engineer retains full responsibility for everything that is committed, deployed, or shipped — regardless of how it was produced.

This is not a philosophical position. It is the practical reality of how accountability works in engineering organisations and in law. When a software defect causes harm, the investigation asks who designed, built, tested, and deployed the system. The answer is the humans and the organisation — not the tools they used. This was true when the tool was a compiler, a framework, or a cloud provider. It remains true when the tool is an AI agent.

Roychoudhury et al. (2025) frame this directly in their analysis of agentic SE systems: the central challenge is not capability but *trust* — establishing the conditions under which engineers and organisations can place justified confidence in AI-generated outputs ([Roychoudhury et al., 2025](https://arxiv.org/abs/2502.13767)). Trust is not granted by default. It is earned through verification discipline, bounded delegation, and accumulated evidence of reliable behaviour in specific contexts. An agent that has produced correct, secure authentication code fifty times on a project earns a degree of trust for that task type. That trust does not generalise to database migrations, production deployments, or security-critical logic the agent has not been tested against.

This has three concrete implications for agentic practice:

**Review everything before it is committed.** The agent's output is a first draft, not a final product. The engineer's review is what transforms it from a generated artefact into code the engineer stands behind. This review should be at least as thorough as a review of code written by a junior teammate — someone competent but fallible, whose work you are co-signing by approving.

**Understand what you are committing.** Committing code you do not understand is not acceptable regardless of its origin. An engineer who cannot explain what a function does, why it uses a particular approach, and what its failure modes are, has not adequately verified the output. If the agent produces code you do not understand, the right response is to ask the agent to explain it, to read the relevant documentation, and to ensure you understand it before committing — not to trust that it looks plausible.

**Set appropriate delegation boundaries.** Not every task should be fully delegated. Determine which actions in your agentic workflow are irreversible (database migrations, production deployments, external API calls that have side effects) and require explicit human approval before the agent takes them. Reversible actions in a version-controlled environment — editing files, generating tests, updating documentation — can be delegated with human review at the end. Irreversible actions require human-in-the-loop approval at the point of action.

The tool does not make the engineer. Jensen Huang was right that the barrier to producing code has fallen. The barrier to producing *correct, secure, maintainable* code has not moved. That barrier has always been engineering judgment, and it remains so.

---
