## 22.6 Planning: When to Decompose, When to Act

---

Planning is the process by which an agent decomposes a complex goal into a sequence of subtasks before executing any of them. It differs from the ReAct Reason step in that it produces a full multi-step roadmap before any execution begins, whereas the Reason step produces one action at a time in response to the current observation.

The case for explicit planning is compelling in certain scenarios. When a task has clear sequential dependencies — step three cannot begin until step two is complete, and step two requires the output of step one — planning makes those dependencies explicit and prevents the agent from attempting steps in the wrong order. When a task involves multiple parallel subtasks that can be distributed to specialised sub-agents, planning allows the orchestrating agent to assign subtasks efficiently rather than executing them sequentially. When a task involves potentially expensive tool calls — external API requests with per-call costs, database operations with significant latency — planning allows the agent to identify unnecessary calls before making them.

The case against reflexive planning is equally compelling. Planning is itself a language model inference: it has latency and cost. For tasks that are sufficiently simple or well-precedented, the overhead of generating an explicit plan before acting can exceed the overhead of simply executing the ReAct loop directly. An agent that plans extensively before every task adds latency without adding reliability for the class of tasks where the ReAct loop's incremental approach is adequate.

The practical guidance is: use explicit planning when the task involves more than three or four sequential dependencies, when subtasks can be parallelised across agents, or when the cost of executing unnecessary tool calls significantly exceeds the cost of planning. Use the ReAct loop directly when the task is self-contained, the tool calls are cheap, and the goal can be verified incrementally. Most production agent systems use both strategies, routing tasks to a planner or directly to the ReAct loop based on task classification at the outset.

---
