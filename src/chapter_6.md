# Chapter 6: Agentic Software Engineering: A New Paradigm

> *"The question is not whether AI will change software engineering. It already has. The question is whether you are shaping that change or being shaped by it."*

---

## Learning Objectives

By the end of this chapter, you will be able to:

1. Distinguish agentic software engineering from AI-assisted development.
2. Explain what an AI coding agent is and how it differs from a copilot or chat assistant.
3. Describe the Agentic SDLC and its four phases: Spec, Generate, Verify, Refine.
4. Identify the key components of an agent: planning, tool use, memory, and reflection.
5. Explain the purpose of MCP (Model Context Protocol) and how it gives agents tools and context.
6. Describe A2A (Agent-to-Agent) coordination and orchestrator-subagent patterns.
7. Select an appropriate agent and model for a given engineering task.
8. Apply the agentic lens to re-examine your course project specification.

---

## 6.1 Two Ways of Working with AI

Before 2021, AI's role in software development was largely confined to autocomplete suggestions, simple code search, and static analysis. The release of GitHub Copilot changed this: for the first time, AI could generate contextually relevant code at the function level from a comment or function signature.

Most developers initially used these tools as *accelerators* — they wrote the specification, the design, the tests, and then used AI to fill in boilerplate or suggest implementations for functions they already had in mind. This is *AI-assisted development*: the engineer's workflow is unchanged, but AI speeds up some steps.

*AI-native engineering* is a different posture. It recognises that AI has changed not just the speed of some steps, but the nature of the engineer's job itself. In AI-native engineering:

- **Specifications become the primary engineering artefact** — what you write for the AI is as important as what the AI writes back
- **Generation is a commodity** — producing code is no longer the bottleneck
- **Verification becomes the critical skill** — determining whether generated code is correct, secure, and appropriate requires deep engineering judgment
- **The SDLC is restructured** around the capabilities and failure modes of AI systems

This is not a prediction about some future state. It is a description of how leading software teams are working today ([Khlaaf et al., 2022](https://arxiv.org/abs/2212.09251)).

---

## 6.2 The Evolution of AI Coding Tools

Understanding where current tools came from helps calibrate what they can and cannot do.

### 6.2.1 Copilots (2021–present)

GitHub Copilot, powered by OpenAI Codex ([Chen et al., 2021](https://arxiv.org/abs/2107.03374)), was the first widely deployed AI coding tool. It operates in-editor, completing code as the developer types. It works well for:

- Boilerplate and repetitive patterns
- Simple algorithms with clear names
- Common library API usage
- Translating between languages

It works poorly for:
- Multi-file context
- Long-range dependencies
- System-level design
- Novel or domain-specific logic

### 6.2.2 Chat-Based Assistants (2022–present)

ChatGPT, Claude, and Gemini introduced multi-turn conversation with AI. Engineers could now describe a problem in natural language, receive an explanation or solution, and iterate through dialogue. Chat interfaces handle more context than inline completion and support discussion of design decisions.

### 6.2.3 AI Coding Agents (2024–present)

AI coding agents — such as Claude Code, Devin ([Cognition, 2024](https://cognition.ai/blog/introducing-devin)), and Cursor in agent mode — represent the next step. An agent is not just responding to prompts; it is *acting in the world*:

- It can read and write files
- It can run code and tests
- It can browse the web and read documentation
- It can use APIs and external tools
- It can plan a multi-step task and execute each step autonomously

This changes the nature of human-AI collaboration significantly. Rather than the engineer making every decision and using AI to execute individual steps, the engineer can delegate a whole task to an agent, monitor its progress, and intervene when it goes wrong.

---

## 6.3 The Agentic SDLC: Spec → Generate → Verify → Refine

The traditional SDLC (Requirements → Design → Implementation → Testing → Deployment) maps awkwardly onto AI-native workflows. A more useful model for AI-native development is:

```
Spec → Generate → Verify → Refine
  ↑                              │
  └──────────────────────────────┘
```

This cycle is iterative and fast — a single round can take minutes rather than days.

### 6.3.1 Spec

*Specification* is the act of describing, precisely and completely, what you want the AI to produce. In AI-native engineering, specification is the primary engineering activity — not implementation.

A good specification for AI includes:

- **Context**: What is the purpose of this component? What does it fit into?
- **Inputs and outputs**: What does the function receive? What should it return?
- **Constraints**: What invariants must hold? What should the function explicitly NOT do?
- **Examples**: What are the expected input-output pairs for key cases?
- **Quality attributes**: What performance, security, or style requirements apply?

The quality of your specification directly determines the quality of what is generated. Vague inputs produce vague outputs. This is the central insight of prompt engineering, covered in depth in Chapter 5.

### 6.3.2 Generate

Generation is the act of invoking the AI with your specification to produce code, tests, documentation, or other artefacts. In the AI-native paradigm, this step is largely mechanical — the creative and intellectual work is in the specification and verification phases.

Key decisions at the generate step:
- **Which model to use**: Different models have different strengths, costs, and context windows
- **Temperature and sampling**: Lower temperatures produce more deterministic output; higher temperatures produce more varied output
- **Context to include**: What files, documentation, or examples should accompany the specification?

### 6.3.3 Verify

Verification is the act of determining whether the generated output meets the specification. This is where most of the engineering judgment in AI-native development lives.

Verification is covered in depth in Chapter 6. At a high level, it involves:

- Running automated tests
- Static analysis and type checking
- Manual code review
- Behavioural testing against real or synthetic data
- Security review

Crucially, verification must happen *before* the generated code is trusted. AI-generated code can pass visual inspection while containing subtle bugs, security vulnerabilities, or logical errors that only surface under specific conditions.

### 6.3.4 Refine

If verification reveals problems, refinement involves returning to the specification (to add constraints or correct misunderstandings) and regenerating. Refinement may involve:

- Adding failing test cases to the specification ("the function should return X when given Y")
- Adding explicit constraints that the AI violated ("do not use X, use Y instead")
- Breaking the specification into smaller, more tractable pieces
- Changing the approach entirely

The Spec → Generate → Verify → Refine loop typically runs multiple times before a satisfactory result is reached. The discipline is in specification quality and verification rigour, not in generating more.

---

## 6.4 What Is an AI Coding Agent?

An AI coding agent is a system in which a large language model can not only generate text, but also take *actions* in the world — reading and writing files, executing code, calling APIs, and browsing the web — in service of a multi-step goal.

The term "agent" comes from AI research ([Russell & Norvig, 2020](https://aima.cs.berkeley.edu/)), where an agent is any system that perceives its environment and takes actions to achieve goals. In the context of AI coding, the environment is the software development environment (the codebase, the terminal, the browser).

### 6.4.1 Tool Use

The most fundamental capability that distinguishes an agent from a chatbot is *tool use* — the ability to invoke external functions and incorporate their results into the agent's reasoning.

Common tools available to coding agents:

| Tool | Description |
|---|---|
| `read_file(path)` | Read the contents of a file |
| `write_file(path, content)` | Write content to a file |
| `run_command(cmd)` | Execute a shell command and return the output |
| `search_web(query)` | Search the web and return results |
| `fetch_url(url)` | Fetch the contents of a URL |
| `call_api(endpoint, params)` | Make an HTTP API call |

When an agent has access to these tools, it can autonomously investigate a codebase, identify a bug, write a fix, run the tests to verify it, and commit the change — all without human intervention at each step.

### 6.4.2 Planning

Planning is the ability to break a high-level goal into a sequence of sub-tasks and execute them in order, adapting the plan as new information is discovered.

A naive agent executes tasks sequentially without reflection. A more sophisticated agent uses a *plan-execute-observe* loop:

```
Goal: "Add input validation to the task creation endpoint"

Plan:
  1. Read the current task creation endpoint code
  2. Read the existing tests for this endpoint
  3. Identify which input fields currently lack validation
  4. Write validation logic for each field
  5. Write tests for the new validation
  6. Run the tests to verify

Execute step 1 → Observe result → Update plan if needed → Execute step 2 → ...
```

Modern agents use techniques like ReAct (Reason + Act) ([Yao et al., 2022](https://arxiv.org/abs/2210.03629)) to interleave reasoning and action, producing more reliable multi-step behaviour.

### 6.4.3 Memory

Agents need different types of memory to function effectively across long tasks:

- **In-context memory**: The current conversation history and tool results — limited by the model's context window
- **External memory**: Files, databases, or vector stores that the agent can read and write — persistent across sessions
- **Semantic memory**: Compressed summaries of past interactions — allows the agent to operate over longer time horizons than the context window permits

Managing what information to put in context (and what to leave out) is a significant challenge in building effective agents. Too much context causes the model to "lose focus"; too little context causes it to make decisions without relevant information.

---

## 6.5 Choosing the Right Model

Not all AI models are equally suited to every task. Selecting the right model for a given purpose is an engineering decision with real consequences for quality, speed, and cost.

### 6.5.1 The Model Capability Spectrum

Modern AI providers offer models across a spectrum from small/fast/cheap to large/slow/capable. The Anthropic model family as of 2025:

| Model | Strengths | Context Window | Relative Cost | Best For |
|---|---|---|---|---|
| **Claude Haiku** | Speed, low latency | 200K tokens | Low | High-volume, simple tasks: docstring generation, lint fixes, short completions |
| **Claude Sonnet** | Balanced capability and speed | 200K tokens | Medium | Most engineering tasks: feature implementation, code review, test generation |
| **Claude Opus** | Maximum capability, complex reasoning | 200K tokens | High | Difficult tasks: architectural decisions, complex debugging, security analysis |

> **Check the current model list.** Model families evolve rapidly. Always verify available models and their capabilities at [https://docs.anthropic.com/en/docs/about-claude/models](https://docs.anthropic.com/en/docs/about-claude/models) before selecting a model for production use.

For OpenAI, the equivalent spectrum is GPT-4o-mini (fast/cheap) → GPT-4o (balanced) → o1/o3 (reasoning-heavy). For Google: Gemini Flash → Gemini Pro → Gemini Ultra. The selection principle is the same regardless of provider.

### 6.5.2 Matching Model to Task

```python
import anthropic

client = anthropic.Anthropic()

# Use a smaller, faster model for high-volume, simple tasks
def generate_docstring(function_code: str) -> str:
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",  # Fast, cheap — appropriate for docstrings
        max_tokens=256,
        messages=[{"role": "user", "content": f"Write a one-line docstring for:\n{function_code}"}],
    )
    return response.content[0].text


# Use a capable model for complex reasoning tasks
def security_review(code: str) -> str:
    response = client.messages.create(
        model="claude-opus-4-7",  # Full capability — security analysis needs it
        max_tokens=2048,
        messages=[{"role": "user", "content": f"Security review:\n{code}"}],
    )
    return response.content[0].text


# Use a balanced model for most feature development
def implement_feature(specification: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",  # Balanced — good quality at reasonable cost
        max_tokens=4096,
        messages=[{"role": "user", "content": specification}],
    )
    return response.content[0].text
```

### 6.5.3 Context Window Considerations

Context window size — the maximum amount of text a model can process in a single call — directly affects specification design. All current Claude models support 200K tokens (roughly 150,000 words), which is sufficient for most codebases. However, larger contexts:

- Cost more (most providers charge per token)
- Are processed more slowly
- May cause the model to "lose focus" on specific instructions buried in long context ([Liu et al., 2023](https://arxiv.org/abs/2307.03172))

**Practical guideline**: Keep specification prompts under 2,000 tokens for most code generation. Reserve large context for tasks that genuinely need it — understanding an entire module before refactoring, for example.

### 6.5.4 Cost Estimation

Rough cost estimation for common tasks (prices vary; check provider pricing pages for current rates):

| Task | Typical tokens | Model tier | Approx. cost per 1,000 tasks |
|---|---|---|---|
| Docstring generation | ~500 in + ~100 out | Small | < $0.10 |
| Function implementation | ~1,000 in + ~500 out | Medium | ~$1–3 |
| Security review | ~2,000 in + ~1,000 out | Large | ~$15–30 |
| Agent task (10 steps) | ~20,000 total | Medium | ~$10–20 |

For a 12-person team running 50 AI-assisted tasks per day, monthly API costs typically range from $50–500 depending on task mix and model selection — comparable to a single SaaS tool licence.

---

## 6.6 The Shifting Role of the Engineer

The emergence of AI coding agents does not eliminate the need for software engineers — but it does fundamentally change what engineers spend their time on.

### 6.6.1 What Changes

**Less time on**: Implementing boilerplate, writing routine CRUD code, translating designs into code, looking up API documentation, writing test scaffolding.

**More time on**: Defining the problem clearly, writing precise specifications, verifying generated outputs, architectural decisions, security review, stakeholder communication.

### 6.6.2 The Engineer as Principal

In agentic systems, the human engineer acts as a *principal* — the authority that defines goals, sets constraints, and approves outcomes. The agent acts as an *executor* — planning and carrying out the steps needed to achieve the goal.

This relationship requires a new set of skills:

- **Goal decomposition**: Breaking a complex goal into tasks small enough for an agent to handle reliably
- **Constraint specification**: Defining what the agent must NOT do, not just what it should do
- **Output verification**: Assessing whether the agent's output is correct, secure, and appropriate
- **Failure diagnosis**: Understanding why an agent went wrong and how to prevent recurrence

### 6.6.3 Skills That Endure

The foundational skills of software engineering — understanding algorithms, system design, testing, security, and communication — become *more* valuable in the AI-native era, not less. They are the skills needed to write good specifications, verify AI outputs, and diagnose agent failures.

Engineers who treat AI tools as magic boxes that produce correct code will be frustrated and vulnerable. Engineers who understand the capabilities and failure modes of AI systems will be significantly more productive.

---

## 6.7 Tutorial: Working with an AI Coding Agent End-to-End

This tutorial demonstrates the Agentic SDLC cycle using the Anthropic API to implement a feature for the course project.

### The Task

Add a `filter_tasks` function to the task service that filters tasks by status, priority, and assignee.

### Step 1: Write the Specification

```python
# spec: filter_tasks function
# 
# Context: Part of a task management API backend (Python 3.11, no framework)
# 
# Function signature:
#   filter_tasks(tasks, status=None, priority=None, assignee=None) -> list[Task]
#
# Behaviour:
# - Returns all tasks if no filters are provided
# - Filters by status if status is provided (exact match)
# - Filters by priority if priority is provided (exact match, integer 1-4)
# - Filters by assignee if assignee is provided (exact match on assignee email)
# - Multiple filters are ANDed (all must match)
# - Returns an empty list (not None) if no tasks match
# - Does NOT modify the input list
# - Raises TypeError if tasks is not a list
# - Raises ValueError if priority is provided but not in range 1-4
#
# Examples:
# filter_tasks([task1, task2], status="open") -> [task1] (if task1.status=="open")
# filter_tasks([task1], status="open", priority=2) -> [] (if task1.priority!=2)
# filter_tasks([]) -> []
```

### Step 2: Generate an Implementation

```python
import anthropic

client = anthropic.Anthropic()

specification = """
Implement a Python function `filter_tasks` with the following specification:
...
"""

response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    messages=[{"role": "user", "content": specification}],
)

print(response.content[0].text)
```

### Step 3: Verify the Output

Review the generated code for:

- [ ] Correct type hints on function signature and return type
- [ ] Does not modify the input list (uses a new list or generator)
- [ ] TypeError raised when tasks is not a list
- [ ] ValueError raised when priority is out of range
- [ ] Empty list returned (not None) when no matches
- [ ] All filter conditions ANDed correctly

Write tests to verify each behaviour before accepting the code.

### Step 4: Refine

If the generated code is missing the `TypeError` check, add this constraint to the specification:

```python
# Add to specification:
# - MUST raise TypeError (not just return []) if tasks is not a list
#   This is important because silent failures mask programmer errors
```

Regenerate and re-verify.

---

## 6.8 Human-in-the-Loop vs. Human-on-the-Loop

Not all agentic tasks warrant the same level of human involvement. Understanding the two dominant oversight postures — *human-in-the-loop* and *human-on-the-loop* — helps you match the level of supervision to the risk profile of the task.

### Human-in-the-Loop (HITL)

In a human-in-the-loop configuration, a human must explicitly approve each consequential action before the agent takes it. The agent pauses, presents its intended next step, and waits for the engineer to confirm, modify, or reject it.

This is the appropriate posture when:
- The actions are **irreversible** (deleting records, sending emails, deploying to production)
- The domain is **novel or high-stakes** (security-critical code, financial logic, medical data)
- The agent is **new or untested** and its reliability has not yet been established
- **Regulatory or audit requirements** mandate a documented human approval at each step

The cost of HITL is latency and cognitive load — the engineer must stay engaged throughout the task, which negates many of the throughput benefits of autonomous agents.

### Human-on-the-Loop (HOTL)

In a human-on-the-loop configuration, the agent executes autonomously while a human *monitors* its progress and retains the ability to intervene. The engineer is not required to approve each step, but receives notifications of significant events — tool calls with side effects, unexpected errors, or completion — and can halt the agent at any point.

This is the appropriate posture when:
- The actions are **reversible** (editing files in a version-controlled repository, writing tests)
- The agent is operating in a **well-defined, bounded domain** with clear success criteria
- **Automated verification** (test suites, linters, type checkers) can catch most errors before they propagate
- The team has **established trust** in the agent through prior use on similar tasks

The risk of HOTL is that subtle errors may propagate further before they are caught. This is mitigated by strong automated verification at the end of the agentic loop.

### Choosing the Right Posture

| Dimension | Human-in-the-Loop | Human-on-the-Loop |
|---|---|---|
| Action reversibility | Low (irreversible) | High (reversible) |
| Domain familiarity | New/unfamiliar | Well-understood |
| Agent maturity | Untested/new | Established track record |
| Verification coverage | Limited automated checks | Comprehensive test suite |
| Regulatory context | Audit/compliance required | Standard engineering workflow |
| Throughput cost | High (human bottleneck) | Low (minimal interruption) |

In practice, most teams operate on a sliding scale: HITL for production deployments and database migrations; HOTL for feature implementation, test generation, and documentation. As agent reliability in a specific domain improves and automated verification matures, the posture typically shifts from HITL toward HOTL.

A third posture — *fully autonomous* with no human oversight — is rarely appropriate in software engineering contexts, even for low-risk tasks. At minimum, the engineer should review the agent's output before it is committed or deployed. The goal is to reduce *friction*, not to eliminate *judgment*.

---

## Chapter Summary

This chapter introduced the paradigm shift from AI-assisted to AI-native software engineering and established the conceptual foundations you will build on throughout this course.

**Key ideas:**

- *AI-assisted development* uses AI to accelerate individual steps in an unchanged workflow. *AI-native engineering* restructures the workflow itself around AI capabilities and failure modes.
- The **Agentic SDLC** — Spec → Generate → Verify → Refine — replaces the traditional waterfall and maps better onto the iterative, fast-feedback nature of AI-assisted development. The critical human activities are specification and verification, not implementation.
- An **AI coding agent** extends a language model with tools (file access, code execution, API calls), planning, and memory. The Anthropic `tool_use` API is the mechanism through which this tool-calling behaviour is expressed in code: the model requests a tool call, your code executes it, and the result is returned to the model for further reasoning.
- **MCP (Model Context Protocol)** standardises how agents connect to external tools and data sources, eliminating bespoke integration code. **A2A (Agent-to-Agent)** standardises how agents communicate with each other, enabling composable multi-agent pipelines. Both protocols trade bespoke flexibility for interoperability at scale.
- **Model selection** is an engineering decision: match model capability and cost to task complexity. Use small models for high-volume simple tasks; reserve large models for tasks requiring deep reasoning.
- The engineer's role shifts from *implementer* to *principal*: defining goals, writing precise specifications, verifying outputs, and diagnosing failures. Foundational software engineering skills — algorithms, system design, testing, security — become *more* valuable, not less.
- **Human-in-the-loop** (approve each action) is appropriate for irreversible, high-stakes, or audited tasks. **Human-on-the-loop** (monitor and intervene) is appropriate when actions are reversible, verification is strong, and the agent has an established track record in the domain.

---

## Review Questions

**Conceptual**

1. Explain the difference between AI-assisted development and AI-native engineering. Give a concrete example of a task that would be handled differently under each approach, and explain why the engineer's activities differ between the two.

2. The chapter argues that verification — not generation — is "where most of the engineering judgment in AI-native development lives." Do you agree? What specific skills does effective AI output verification require that differ from reviewing human-written code?

3. Compare the MCP (Model Context Protocol) and A2A (Agent-to-Agent) protocols. What problem does each solve, and why is standardisation at the protocol level more valuable than each team building its own integration layer?

**Applied**

4. You are building an agent that monitors a production database, detects anomalies, and automatically rolls back suspicious transactions. Using the HITL/HOTL framework from Section 4.8, justify which oversight posture is appropriate for each phase of the agent's operation (detection, decision, rollback). What automated verification would you put in place to support your chosen posture?

5. Your team has been tasked with using the Agentic SDLC to add a password reset feature to the course project. Write a complete specification (Step 1 of the tutorial) for a `request_password_reset(email: str) -> None` function, suitable for use in a `client.messages.create` call. Your specification must include: context, function signature, behaviour (at least five rules), constraints (at least two things the function must NOT do), and three concrete input-output examples covering normal operation, a missing account, and an invalid email format. Then identify two specific behaviours you would check in the verification step that an AI is likely to implement incorrectly or omit.
