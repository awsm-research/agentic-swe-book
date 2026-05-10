## 22.7 LangGraph: Agents as State Machines

---

The ReAct loop describes how an agent reasons and acts. LangGraph provides a concrete framework for implementing that loop and the broader orchestration logic of multi-agent systems.

LangGraph models an agent system as a directed graph of nodes and edges — a state machine in which the state represents the agent's current knowledge, the nodes represent actions or decisions, and the edges represent transitions between them.

A **node** in LangGraph is a unit of computation. It receives the current state, performs an operation — a language model call, a tool invocation, a validation check, a human approval step — and returns an updated state. Nodes are the atoms of agent logic. They are independently testable, observable, and replaceable. A node that calls a clinical database query tool is distinct from a node that reasons over the returned results, which is distinct from a node that formulates the response. Separating these into distinct nodes rather than embedding them in a single monolithic inference step makes each step auditable and each failure localised.

An **edge** in LangGraph is a transition rule. A standard edge always routes from one node to the next: after the reasoning node, always call the tool-execution node. A **conditional edge** routes to different nodes depending on the current state. If the tool returned a valid result, proceed to the summarisation node. If the tool returned an error, proceed to the error-handling node. If the iteration count exceeds the maximum, proceed to the termination node. Conditional edges are where the agent's safety logic lives: they encode the termination conditions, circuit breakers, and error-handling paths that prevent the agent from looping indefinitely or acting on invalid data.

**State persistence** in LangGraph means that the agent's state can be checkpointed between nodes and stored externally. If the agent's execution is interrupted — by a system failure, a timeout, or a human review step that requires asynchronous approval — the state can be recovered and execution can resume from the last checkpoint. This is an essential property for long-running clinical workflows: a patient care pathway that spans multiple sessions, requires clinician sign-off at defined points, and must be auditable across its full history cannot be implemented as a single stateless inference.

The value of modelling agents as state machines is not merely organisational tidiness. It makes agent behaviour formally describable: you can specify which states are reachable from which other states, which transitions require human approval, and which nodes have access to which tools. This formal structure is the foundation of systematic testing — you can enumerate the paths through the graph and write tests that verify agent behaviour on each critical path, rather than relying on end-to-end evaluation that may not exercise rare but consequential paths.

---
