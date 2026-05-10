## 10.8 AI-Assisted Maintenance

Coding agents are unusually well-suited to maintenance work — and unusually dangerous when used without guardrails.

### Reading Legacy Code

The first useful agentic task on a legacy system is exposition, not modification. Asking an agent to summarise a module, draw the call graph, list the invariants, or trace a request through the system surfaces structure that the original authors never documented. The output is a draft, not a finding — every claim must be checked against the code — but the draft is faster to verify than the codebase is to read cold.

### Characterisation Tests Before Refactoring

Michael Feathers' *Working Effectively with Legacy Code* defines legacy code as code without tests ([Feathers, 2004](https://www.oreilly.com/library/view/working-effectively-with/0131177052/)). His core technique is the *characterisation test* — a test that pins down what the existing code currently does, without making any claim about what it should do. Once behaviour is pinned, the code can be refactored with a regression safety net.

This is exactly the workflow agents accelerate. A prompt of the form *"Generate characterisation tests for this module that exercise every public method with at least three input variants, asserting on the current return values"* produces a test suite in minutes that would take a careful human a day. The catch is that the tests must be reviewed — agents will sometimes assert on whatever the code happens to do today, including bugs. The tests pin the bug as well as the behaviour. Some of those tests need to fail, deliberately, before the refactor begins.

### Generating Refactor Variants

A productive pattern is to ask an agent for *three* refactor variants of the same function, optimising for different qualities — readability, performance, testability — and then evaluate them against the characterisation test suite. The variant that passes all the tests, reduces complexity, and reads cleanly wins. The other two are discarded. This is more disciplined than asking for *the* refactor, because it forces the reviewer to evaluate trade-offs explicitly.

### Migration Scripts and Bulk Chores

Agents do well at the unglamorous work that humans avoid: language version migrations, framework upgrades, type-annotation backfill, docstring generation, bulk renaming. The risk is uniform — agents replicate small mistakes consistently — so the verification strategy must be uniform too: run the test suite after every batch, not at the end.

### The Anti-Pattern

The most damaging way to use an agent in maintenance is to ask it to *clean up* a module without a regression safety net. The agent will produce code that looks better, passes the type-checker, and silently changes behaviour. Without characterisation tests, the change reaches production. The bug is then attributed to the agent, but the failure was the workflow.

---
