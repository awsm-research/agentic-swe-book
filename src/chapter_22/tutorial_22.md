## 22.11 Tutorial: Building MedAgent with LangGraph

You are a software engineer on the hospital's clinical informatics team. The radiology department loved the MedChat chatbot you shipped last sprint, but the chief radiologist wants something more autonomous: a single agent that can pull up a patient's test results, check whether their current medications interact dangerously, and then write a structured clinical summary — all without a human clicking through three separate screens. Your job is to build **MedAgent v1**: a ReAct agent powered by LangGraph that orchestrates three read-only tools in a continuous reasoning loop, stops itself before it can run forever, and produces a structured clinical note for each patient case.

**Concepts covered:** LangGraph `StateGraph`, ReAct pattern, LangChain `@tool` decorator, Pydantic tool schemas, `ToolNode`, conditional edges, in-context memory, recursion limit, tool error handling

**Format:** Individual or pairs | **Duration:** ~2 hours | **Tool:** Python · langgraph · langchain · langchain-openai · pydantic · python-dotenv

---

### Outline

- [Learning Objectives](#learning-objectives)
- [Prerequisites](#prerequisites)
- [Part A: Tools and the ReAct Graph](#part-a-tools-and-the-react-graph-60-min)
- [Part B: Running and Controlling the Agent](#part-b-running-and-controlling-the-agent-60-min)
- [References](#references)

---

### Learning Objectives

1. Explain the ReAct (Reason + Act) loop and trace it through a LangGraph execution.
2. Implement LangChain tools with Pydantic input schemas and structured error returns.
3. Build a `StateGraph` with `ToolNode`, conditional edges, and an entry point.
4. Configure a recursion limit to prevent infinite agent loops.
5. Attach a system prompt that scopes the agent's role and enforces output format.
6. Run end-to-end patient scenarios and read the full reasoning trace.

---

### Prerequisites

Install the required packages:

```bash
pip install langgraph langchain langchain-openai pydantic python-dotenv
```

Verify your environment:

```bash
python -c "import langgraph, langchain, openai, pydantic; print('OK')"
```

You need an OpenAI API key. Create a `.env` file in the project root:

```bash
echo "OPENAI_API_KEY=sk-..." > medagent/.env
```

> **Why `gpt-4o-mini`?** It supports parallel tool calling, is cost-efficient for tutorials, and produces reliable JSON for tool call arguments. You can swap in `gpt-4o` for production.

---

### Part A: Tools and the ReAct Graph *(~60 min)*

#### Step 1: Create the project structure

```bash
mkdir -p medagent
cd medagent
touch tools.py agent.py mock_data.py .env requirements.txt
```

Add dependencies to `requirements.txt`:

```
langgraph>=0.2.0
langchain>=0.3.0
langchain-openai>=0.2.0
pydantic>=2.0.0
python-dotenv>=1.0.0
```

#### Step 2: Write `mock_data.py`

This module simulates the hospital's database. In a real deployment you would replace each dict lookup with a SQL query or REST call — the tool interface stays identical.

```python
# medagent/mock_data.py

PATIENTS = {
    "P001": {
        "name": "Alice Martínez",
        "age": 67,
        "diagnosis": "Type 2 Diabetes, Hypertension",
        "current_medications": ["metformin", "lisinopril", "aspirin"],
    },
    "P002": {
        "name": "Bernard Okafor",
        "age": 54,
        "diagnosis": "Atrial Fibrillation, Chronic Kidney Disease Stage 3",
        "current_medications": ["warfarin", "digoxin", "furosemide"],
    },
    "P003": {
        "name": "Chen Wei",
        "age": 41,
        "diagnosis": "Rheumatoid Arthritis",
        "current_medications": ["methotrexate", "folic_acid", "ibuprofen"],
    },
}

LAB_RESULTS = {
    "P001": [
        {
            "test_name": "HbA1c",
            "value": 8.2,
            "unit": "%",
            "date": "2025-05-01",
            "normal_range": "4.0-5.6",
            "status": "HIGH",
        },
        {
            "test_name": "eGFR",
            "value": 72,
            "unit": "mL/min/1.73m²",
            "date": "2025-05-01",
            "normal_range": ">60",
            "status": "NORMAL",
        },
        {
            "test_name": "Blood Pressure",
            "value": "158/94",
            "unit": "mmHg",
            "date": "2025-05-03",
            "normal_range": "<130/80",
            "status": "HIGH",
        },
    ],
    "P002": [
        {
            "test_name": "INR",
            "value": 3.8,
            "unit": "ratio",
            "date": "2025-05-02",
            "normal_range": "2.0-3.0",
            "status": "HIGH",
        },
        {
            "test_name": "Serum Creatinine",
            "value": 1.9,
            "unit": "mg/dL",
            "date": "2025-05-02",
            "normal_range": "0.7-1.3",
            "status": "HIGH",
        },
        {
            "test_name": "Digoxin Level",
            "value": 2.4,
            "unit": "ng/mL",
            "date": "2025-05-02",
            "normal_range": "0.5-2.0",
            "status": "HIGH",
        },
    ],
    "P003": [
        {
            "test_name": "ALT",
            "value": 62,
            "unit": "U/L",
            "date": "2025-05-04",
            "normal_range": "7-56",
            "status": "HIGH",
        },
        {
            "test_name": "WBC",
            "value": 3.1,
            "unit": "10³/µL",
            "date": "2025-05-04",
            "normal_range": "4.5-11.0",
            "status": "LOW",
        },
        {
            "test_name": "CRP",
            "value": 28,
            "unit": "mg/L",
            "date": "2025-05-04",
            "normal_range": "<5",
            "status": "HIGH",
        },
    ],
}

# Keyed by frozenset so order of drugs doesn't matter — see tools.py for lookup logic
DRUG_INTERACTIONS = {
    ("warfarin", "aspirin"): {
        "severity": "MAJOR",
        "description": "Concurrent use significantly increases bleeding risk. Monitor INR closely.",
    },
    ("warfarin", "ibuprofen"): {
        "severity": "MAJOR",
        "description": "NSAIDs inhibit platelet aggregation and may increase anticoagulant effect.",
    },
    ("methotrexate", "ibuprofen"): {
        "severity": "MODERATE",
        "description": "NSAIDs may reduce methotrexate clearance, increasing toxicity risk.",
    },
    ("digoxin", "furosemide"): {
        "severity": "MODERATE",
        "description": "Furosemide-induced hypokalaemia potentiates digoxin toxicity.",
    },
    ("metformin", "lisinopril"): {
        "severity": "MINOR",
        "description": "Combination may enhance hypoglycaemic effect; monitor blood glucose.",
    },
}
```

#### Step 3: Write `tools.py`

Each tool uses the `@tool` decorator with a Pydantic `args_schema`. Tools return plain strings — never raise exceptions. If a tool raises, LangGraph propagates it as an unhandled graph error; returning a structured error string lets the agent reason about the failure and try a different approach.

```python
# medagent/tools.py

from langchain_core.tools import tool
from pydantic import BaseModel, Field
from mock_data import PATIENTS, LAB_RESULTS, DRUG_INTERACTIONS


# ── Input schemas ──────────────────────────────────────────────────────────────

class PatientLookupInput(BaseModel):
    patient_id: str = Field(description="The patient identifier, e.g. 'P001'")


class LabResultsInput(BaseModel):
    patient_id: str = Field(description="The patient identifier, e.g. 'P001'")


class DrugInteractionInput(BaseModel):
    drug_a: str = Field(description="First drug name (lowercase, underscores for spaces)")
    drug_b: str = Field(description="Second drug name (lowercase, underscores for spaces)")


# ── Tool implementations ───────────────────────────────────────────────────────

@tool(args_schema=PatientLookupInput)
def lookup_patient_records(patient_id: str) -> str:
    """Look up a patient's demographics and current medications by patient ID.
    Returns patient name, age, diagnosis, and list of current medications."""
    patient = PATIENTS.get(patient_id.upper())
    if patient is None:
        return f"ERROR: Patient '{patient_id}' not found. Valid IDs are: {list(PATIENTS.keys())}"
    meds = ", ".join(patient["current_medications"])
    return (
        f"Patient ID: {patient_id.upper()}\n"
        f"Name: {patient['name']}\n"
        f"Age: {patient['age']}\n"
        f"Diagnosis: {patient['diagnosis']}\n"
        f"Current medications: {meds}"
    )


@tool(args_schema=LabResultsInput)
def get_lab_results(patient_id: str) -> str:
    """Retrieve the most recent laboratory test results for a patient.
    Returns a list of tests with values, units, reference ranges, and status flags."""
    results = LAB_RESULTS.get(patient_id.upper())
    if results is None:
        return f"ERROR: No lab results found for patient '{patient_id}'."
    lines = [f"Lab results for {patient_id.upper()}:"]
    for r in results:
        lines.append(
            f"  [{r['status']}] {r['test_name']}: {r['value']} {r['unit']} "
            f"(normal: {r['normal_range']}) — {r['date']}"
        )
    return "\n".join(lines)


@tool(args_schema=DrugInteractionInput)
def search_drug_interactions(drug_a: str, drug_b: str) -> str:
    """Check whether two drugs have a known interaction.
    Returns severity (MAJOR/MODERATE/MINOR/NONE) and a clinical description."""
    key_a = (drug_a.lower(), drug_b.lower())
    key_b = (drug_b.lower(), drug_a.lower())
    interaction = DRUG_INTERACTIONS.get(key_a) or DRUG_INTERACTIONS.get(key_b)
    if interaction is None:
        return f"No known interaction between '{drug_a}' and '{drug_b}' in the database."
    return (
        f"Interaction: {drug_a} + {drug_b}\n"
        f"Severity: {interaction['severity']}\n"
        f"Description: {interaction['description']}"
    )


tools = [lookup_patient_records, get_lab_results, search_drug_interactions]
```

> **Why return error strings instead of raising exceptions?** When a tool raises, `ToolNode` catches it and injects an error `ToolMessage` by default — but only in newer LangGraph versions. Returning a descriptive error string is portable, keeps the agent in control, and lets you test tool outputs deterministically.

#### Step 4: Write `agent.py`

```python
# medagent/agent.py

import os
from dotenv import load_dotenv
from typing import Annotated, TypedDict
import operator

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from tools import tools

load_dotenv()

# ── State schema ───────────────────────────────────────────────────────────────
# Annotated[list, operator.add] tells LangGraph to *append* new messages
# rather than replace the whole list on each node return.

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]


# ── LLM setup ─────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are MedAgent, a read-only clinical decision-support assistant.

Your role:
- Look up patient records and lab results using the provided tools.
- Check drug interactions for a patient's current medication list.
- Summarise findings in a structured clinical note.

Constraints:
- You may ONLY use the tools provided. Do not invent patient data.
- You have read-only access. You cannot order tests, prescribe medications, or modify records.
- If a tool returns an error, report it clearly rather than guessing.

Output format for the final clinical summary:
### Clinical Summary
**Patient:** <name> (<ID>)
**Date:** <today>

#### Abnormal Lab Results
<bullet list>

#### Drug Interaction Flags
<bullet list, or "None identified">

#### Recommendation
<1-3 sentences for the treating clinician>
"""

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(tools)


# ── Graph nodes ────────────────────────────────────────────────────────────────

def call_model(state: AgentState) -> dict:
    """Invoke the LLM with the current message history."""
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


def should_continue(state: AgentState) -> str:
    """Route to 'tools' if the last message contains tool calls, otherwise end."""
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return END


# ── Graph construction ─────────────────────────────────────────────────────────

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("agent", call_model)
    graph.add_node("tools", ToolNode(tools))

    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")

    return graph.compile()


app = build_graph()


# ── Helper: run one query ──────────────────────────────────────────────────────

def run_query(question: str, recursion_limit: int = 10) -> str:
    """Run a single question through MedAgent and return the final answer."""
    initial_state = {
        "messages": [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=question),
        ]
    }
    config = {"recursion_limit": recursion_limit}
    try:
        result = app.invoke(initial_state, config=config)
    except Exception as exc:
        return f"[Agent stopped] {exc}"

    # The last message is always the final AI response
    return result["messages"][-1].content
```

> **Why `operator.add` on messages?** Each node returns only the *new* messages it produced. LangGraph merges them into the state by appending (not replacing). Without this annotation, every node return would overwrite the entire history, breaking the conversation context.

---

### Part B: Running and Controlling the Agent *(~60 min)*

#### Step 1: Run your first complete workflow

Create `run.py` in the `medagent/` directory:

```python
# medagent/run.py

from agent import app, run_query, SYSTEM_PROMPT
from langchain_core.messages import SystemMessage, HumanMessage

# ── Scenario 1: Lab review + drug interaction check ───────────────────────────
question_1 = (
    "Patient P001 came in for a routine check. "
    "Please review their lab results and check for drug interactions "
    "between all pairs of their current medications. "
    "Produce a clinical summary."
)

print("=" * 70)
print("SCENARIO 1:", question_1)
print("=" * 70)
answer = run_query(question_1)
print(answer)
```

Run it:

```bash
cd medagent
python run.py
```

#### Step 2: Print the full ReAct reasoning trace

Add a trace-printing helper to `run.py` so you can see every step:

```python
# medagent/run.py  (append below the first scenario)

from langchain_core.messages import AIMessage, ToolMessage

def print_trace(result_state: dict):
    """Pretty-print every message in the agent's reasoning trace."""
    print("\n--- FULL REASONING TRACE ---")
    for i, msg in enumerate(result_state["messages"]):
        role = type(msg).__name__
        if isinstance(msg, AIMessage):
            if msg.tool_calls:
                calls = [f"{tc['name']}({tc['args']})" for tc in msg.tool_calls]
                print(f"[{i}] AGENT → TOOL CALLS: {calls}")
            else:
                print(f"[{i}] AGENT → FINAL ANSWER:\n{msg.content[:300]}")
        elif isinstance(msg, ToolMessage):
            print(f"[{i}] TOOL RESULT ({msg.name}):\n  {msg.content[:200]}")
        else:
            print(f"[{i}] {role}: {str(msg.content)[:100]}")


from agent import app, SYSTEM_PROMPT

initial_state = {
    "messages": [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=question_1),
    ]
}
config = {"recursion_limit": 10}
full_result = app.invoke(initial_state, config=config)
print_trace(full_result)
```

Run again and observe the ReAct loop in the output:

```
[0] SystemMessage: You are MedAgent ...
[1] HumanMessage: Patient P001 came in ...
[2] AGENT → TOOL CALLS: [lookup_patient_records({'patient_id': 'P001'})]
[3] TOOL RESULT (lookup_patient_records): Patient ID: P001 ...
[4] AGENT → TOOL CALLS: [get_lab_results({'patient_id': 'P001'})]
[5] TOOL RESULT (get_lab_results): Lab results for P001 ...
[6] AGENT → TOOL CALLS: [search_drug_interactions({'drug_a': 'metformin', 'drug_b': 'lisinopril'})]
...
[N] AGENT → FINAL ANSWER: ## Clinical Summary ...
```

> **Why this trace matters:** Each `AGENT → TOOL CALLS` step is the *Reason* phase (the LLM deciding what to do), and each `TOOL RESULT` step is the *Act* phase (execution). Seeing this loop is the core insight of the ReAct pattern.

#### Step 3: Add in-context memory for multi-turn sessions

To hold context across follow-up questions in the same session, accumulate messages manually:

```python
# medagent/run.py  (append)

def run_session(questions: list[str], recursion_limit: int = 10) -> None:
    """Run multiple questions in the same conversation context."""
    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    for q in questions:
        print(f"\n>>> USER: {q}")
        messages.append(HumanMessage(content=q))
        result = app.invoke({"messages": messages}, config={"recursion_limit": recursion_limit})
        # Extend our running history with everything the agent added
        new_messages = result["messages"][len(messages):]
        messages.extend(new_messages)
        final = result["messages"][-1].content
        print(f"<<< AGENT:\n{final}")


run_session([
    "Look up patient P002's records.",
    "Now check their lab results.",
    "Are there any drug interactions I should be aware of given their medication list?",
])
```

#### Step 4: Demonstrate and handle the recursion limit

The recursion limit is the safety valve that prevents an agent from spinning forever when a tool keeps returning unhelpful results.

```python
# medagent/run.py  (append)

# Temporarily patch get_lab_results to simulate a stuck tool
import medagent.tools as tools_module
from langchain_core.tools import tool
from pydantic import BaseModel

original_get_lab = tools_module.get_lab_results

@tool
def broken_lab_tool(patient_id: str) -> str:
    """Get lab results."""
    return "I need more information. Please try again with additional context."

# Demonstrate hitting the recursion limit
print("\n--- RECURSION LIMIT DEMO ---")
from agent import build_graph
from tools import lookup_patient_records, search_drug_interactions

demo_tools = [lookup_patient_records, broken_lab_tool, search_drug_interactions]
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, END
import operator
from typing import Annotated, TypedDict
from langchain_core.messages import SystemMessage, HumanMessage

class DemoState(TypedDict):
    messages: Annotated[list, operator.add]

demo_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(demo_tools)

def demo_agent(state):
    return {"messages": [demo_llm.invoke(state["messages"])]}

def demo_route(state):
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return END

demo_graph = StateGraph(DemoState)
demo_graph.add_node("agent", demo_agent)
demo_graph.add_node("tools", ToolNode(demo_tools))
demo_graph.set_entry_point("agent")
demo_graph.add_conditional_edges("agent", demo_route, {"tools": "tools", END: END})
demo_graph.add_edge("tools", "agent")
demo_app = demo_graph.compile()

try:
    demo_app.invoke(
        {"messages": [HumanMessage(content="Get lab results for P001.")]},
        config={"recursion_limit": 5},
    )
except Exception as e:
    print(f"Caught safely: {type(e).__name__}: {e}")
```

Expected output:

```
Caught safely: GraphRecursionError: Recursion limit of 5 reached ...
```

> **Why cap recursion?** An agent in a retry loop makes real API calls, incurs real costs, and can exhaust your rate limits in seconds. A limit of 10–15 turns is appropriate for most clinical workflows; complex multi-step reasoning rarely needs more.

#### Step 5: Run three complete patient scenarios

```python
# medagent/run.py  (append)

from agent import run_query

SCENARIOS = [
    (
        "P001",
        "Review patient P001's lab results. Check all pairwise drug interactions "
        "for their current medications. Produce a full clinical summary.",
    ),
    (
        "P002",
        "Patient P002 has a follow-up today. Their INR result just came back. "
        "Check their labs and flag any interactions or toxicity concerns given "
        "their medication list. Produce a clinical summary.",
    ),
    (
        "P003",
        "Patient P003 is on methotrexate therapy. Review their latest labs "
        "and check for interactions between all their current medications. "
        "Summarise findings for the rheumatology team.",
    ),
]

for patient_id, question in SCENARIOS:
    print("\n" + "=" * 70)
    print(f"SCENARIO — Patient {patient_id}")
    print("=" * 70)
    summary = run_query(question)
    print(summary)
```

Run the complete file:

```bash
python run.py
```

You should see three full clinical summaries, each preceded by a reasoning trace showing which tools were called and in what order.

---

### References

1. LangGraph documentation — StateGraph and ToolNode: <https://langchain-ai.github.io/langgraph/>
2. LangChain `@tool` decorator and Pydantic schemas: <https://python.langchain.com/docs/concepts/tools/>
3. ReAct: Synergizing Reasoning and Acting in Language Models (Yao et al., 2022): <https://arxiv.org/abs/2210.03629>
4. OpenAI parallel tool calling: <https://platform.openai.com/docs/guides/function-calling>
5. LangGraph recursion limits and error handling: <https://langchain-ai.github.io/langgraph/how-tos/recursion-limit/>
