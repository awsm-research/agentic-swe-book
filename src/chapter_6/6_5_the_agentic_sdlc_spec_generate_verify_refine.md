## 6.5 The Agentic SDLC: Spec → Generate → Verify → Refine

The traditional SDLC — Requirements, Design, Implementation, Testing, Deployment — was designed around human execution speeds and human cognitive bottlenecks. When a developer writes a thousand lines of code per day, the bottleneck is implementation. When an agent writes a thousand lines in three minutes, the bottleneck shifts entirely.

The *Agentic SDLC* restructures the workflow around the new bottleneck: specification quality and verification rigour.

```
Spec → Generate → Verify → Refine
  ↑                              │
  └──────────────────────────────┘
```

This loop is iterative and fast — a single round typically takes minutes. The engineer's time is concentrated in the Spec and Verify phases. Generation is nearly instantaneous. Refinement feeds corrections back into the specification.

### Spec

*Specification* is the act of describing precisely and completely what the agent should produce. In the Agentic SDLC, specification is the primary engineering activity. Vague inputs produce plausible but incorrect outputs. The quality of your specification is the binding constraint on the quality of what is generated.

A complete specification for an AI agent includes:

- **Context**: What is this component? Where does it fit in the system?
- **Inputs and outputs**: What does the function receive? What must it return?
- **Behaviour rules**: At least five concrete behavioural requirements
- **Constraints**: What must the function explicitly NOT do?
- **Examples**: Concrete input-output pairs covering the normal case, edge cases, and error cases
- **Quality attributes**: Performance bounds, security requirements, style conventions

An underspecified prompt ("add validation to the login endpoint") produces code that technically adds validation but misses the cases the engineer cared about. A fully specified prompt produces code that can be verified against the specification directly.

### Generate

*Generation* is the act of invoking the agent with the specification to produce code, tests, documentation, or other artefacts. In the Agentic SDLC, generation is largely mechanical — the intellectual work is in the phases before and after it.

Key decisions at this phase:
- **Which model**: Match capability to task complexity — capable models for security-critical or complex reasoning tasks, faster models for boilerplate and scaffolding
- **Which agent**: Terminal agent or AI-native IDE, depending on task and context
- **What context to include**: Which files, conventions, and background does the agent need?

The common mistake is to treat generation as the primary activity. Engineers who spend most of their time crafting prompts to coax better generation are inverting the model. The specification should be thorough enough that generation is routine.

### Verify

*Verification* is the act of determining whether the generated output meets the specification. This is where most engineering judgment lives in the Agentic SDLC.

Verification is not optional and cannot be delegated to the agent itself. An agent asked to check its own output will often confirm that the output is correct even when it is not — it is evaluating against the same implicit model that produced the error ([Huang et al., 2023](https://arxiv.org/abs/2310.01798)). Verification requires a human with the engineering knowledge to recognise what correct looks like.

A structured verification checklist for AI-generated code:

| Category | Questions |
|---|---|
| **Functional correctness** | Does the code do what the specification says, for all specified cases? |
| **Edge cases** | Does it handle empty inputs, null values, boundary conditions? |
| **Security** | Does it introduce injection risks, broken auth, or unsafe defaults? |
| **Error handling** | Are errors surfaced, not silently swallowed? |
| **Type correctness** | Do types match? Does the type checker pass? |
| **Test coverage** | Does the generated test suite actually test the specified behaviours? |
| **Conventions** | Does the code follow the project's style, naming, and structure conventions? |
| **No accidental side effects** | Does the code modify state it was not supposed to touch? |

Automated checks — test suites, linters, type checkers, security scanners — are the first line of verification. They are necessary but not sufficient. Many specification violations pass automated checks because the test suite tests what the code does, not what the specification required.

An important nuance: agents can assist with verification as well as generation. A separate agent configured for security review can audit AI-generated code for vulnerability patterns without the cognitive overhead of the engineer who wrote the original specification ([Roychoudhury, 2025](https://arxiv.org/abs/2508.17343)). However, this only works when the verification agent has access to what Roychoudhury terms *intent inference* — an explicit representation of what the code was supposed to do, grounded in the specification or in program structure analysis — rather than simply re-reading the generated code and guessing. Verification-by-agent without a clear specification to verify against is the same problem as generation-without-specification, one layer deeper.

### Refine

*Refinement* is the act of returning to the specification with information from the verification step and adjusting before regenerating. Refinement is how the loop closes.

Common refinement triggers:

- A test fails: add the failing case as an explicit example in the specification
- The agent used a deprecated library: add a constraint ("do not use X, use Y")
- The output misunderstood a domain concept: add a clarifying definition
- The generated code is technically correct but violates a convention: add the convention to the context

The discipline of refinement is to *improve the specification*, not just re-run the agent with the same input hoping for a different result. Regenerating without refining is the most common time-wasting pattern in agentic workflows.

---
