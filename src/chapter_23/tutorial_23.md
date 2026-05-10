## 23.10 Tutorial: Multi-Agent Orchestration — Planner, Specialists, and Supervisor

MedAgent v1 handles one patient query at a time, but the chief of medicine has a bigger ask: for complex cases, the system should simultaneously review the patient's records, check current clinical guidelines, and draft a referral letter — then hand a coherent package to the clinician. Three concerns at once means three specialised agents working in parallel, coordinated by a supervisor. Your job is to build **MedAgent v2**: a LangGraph multi-agent system with a Records agent, a Research agent, and a Drafting agent, orchestrated by a Supervisor that fans out tasks in parallel, collects results, and degrades gracefully when one agent fails.

**Concepts covered:** LangGraph subgraphs, `Send` API for parallel dispatch, Supervisor orchestrator, agent-to-agent message passing, circuit breaker pattern, failure isolation, integration testing with mocked tools

**Format:** Individual or pairs | **Duration:** ~2 hours | **Tool:** Python · langgraph · langchain · langchain-openai · pytest

---

### Outline

- [Learning Objectives](#learning-objectives)
- [Prerequisites](#prerequisites)
- [Part A: Three Specialised Agents as Subgraphs](#part-a-three-specialised-agents-as-subgraphs-60-min)
- [Part B: Supervisor and Failure Handling](#part-b-supervisor-and-failure-handling-60-min)
- [References](#references)

---

### Learning Objectives

1. Compile individual LangGraph agents as reusable subgraphs with typed input/output state.
2. Use the `Send` API to dispatch tasks to multiple agents simultaneously.
3. Wire a Supervisor graph that fans out, collects results, and fans in to a final node.
4. Implement a circuit breaker that skips a failing agent after N failures.
5. Write integration tests that mock all tool calls and verify pipeline outputs.
6. Read parallel execution in the LangGraph trace to confirm agents ran concurrently.

---

### Prerequisites

All packages from Tutorial 22 plus `pytest`:

```bash
pip install langgraph langchain langchain-openai pydantic python-dotenv pytest
```

Verify:

```bash
pytest --version
python -c "from langgraph.constants import Send; print('Send OK')"
```

Copy `mock_data.py` and `tools.py` from Tutorial 22's `medagent/` folder into the new project root, or symlink them.

---

### Part A: Three Specialised Agents as Subgraphs *(~60 min)*

#### Step 1: Create the project structure

```bash
mkdir -p medagent_v2/agents medagent_v2/tests
cd medagent_v2
touch agents/__init__.py agents/records_agent.py agents/research_agent.py agents/drafting_agent.py
touch supervisor.py run.py tests/__init__.py tests/test_orchestration.py
cp ../medagent/mock_data.py .
cp ../medagent/tools.py .
```

The final layout:

```
medagent_v2/
├── agents/
│   ├── __init__.py
│   ├── records_agent.py
│   ├── research_agent.py
│   └── drafting_agent.py
├── tests/
│   ├── __init__.py
│   └── test_orchestration.py
├── supervisor.py
├── tools.py          # Tutorial 22 tools + two new tools
├── mock_data.py      # Tutorial 22 data + guidelines
└── run.py
```

#### Step 2: Extend `mock_data.py` with clinical guidelines

```python
# medagent_v2/mock_data.py  (append to the existing file)

CLINICAL_GUIDELINES = {
    ("atrial_fibrillation", "anticoagulation"): {
        "source": "ACC/AHA 2023",
        "recommendation": (
            "For non-valvular AF with CHA₂DS₂-VASc ≥ 2, oral anticoagulation is recommended. "
            "DOACs preferred over warfarin unless contraindicated (e.g., severe CKD)."
        ),
        "monitoring": "INR 2.0–3.0 if warfarin; renal function every 6 months on DOACs.",
    },
    ("type_2_diabetes", "glycaemic_control"): {
        "source": "ADA Standards of Care 2024",
        "recommendation": (
            "Target HbA1c < 7% for most adults. Intensify therapy if > 8% after 3 months. "
            "Metformin remains first-line unless eGFR < 30."
        ),
        "monitoring": "HbA1c every 3 months until stable, then every 6 months.",
    },
    ("rheumatoid_arthritis", "methotrexate_monitoring"): {
        "source": "ACR 2021",
        "recommendation": (
            "Monitor CBC and liver enzymes every 4–8 weeks during dose escalation, "
            "then every 8–12 weeks when stable. Hold if ALT > 3× ULN."
        ),
        "monitoring": "ALT, AST, CBC, creatinine every 8 weeks.",
    },
}
```

#### Step 3: Extend `tools.py` with two new tools

```python
# medagent_v2/tools.py  (append after existing tools)

from pydantic import BaseModel, Field
from langchain_core.tools import tool
from mock_data import CLINICAL_GUIDELINES


class ClinicalGuidelinesInput(BaseModel):
    condition: str = Field(
        description="Medical condition, lowercase with underscores, e.g. 'atrial_fibrillation'"
    )
    guideline_type: str = Field(
        description="Type of guidance needed, e.g. 'anticoagulation', 'glycaemic_control'"
    )


class DraftNoteInput(BaseModel):
    patient_id: str = Field(description="Patient identifier, e.g. 'P002'")
    findings: str = Field(description="Summary of lab results and drug interaction findings")
    recommendation: str = Field(description="Clinical recommendation for the treating team")


@tool(args_schema=ClinicalGuidelinesInput)
def search_clinical_guidelines(condition: str, guideline_type: str) -> str:
    """Search current clinical practice guidelines for a given condition and topic.
    Returns the guideline source, recommendation text, and monitoring requirements."""
    key = (condition.lower(), guideline_type.lower())
    guideline = CLINICAL_GUIDELINES.get(key)
    if guideline is None:
        available = [f"{c}/{g}" for c, g in CLINICAL_GUIDELINES.keys()]
        return (
            f"No guideline found for condition='{condition}', type='{guideline_type}'. "
            f"Available: {available}"
        )
    return (
        f"Guideline source: {guideline['source']}\n"
        f"Recommendation: {guideline['recommendation']}\n"
        f"Monitoring: {guideline['monitoring']}"
    )


@tool(args_schema=DraftNoteInput)
def draft_clinical_note(patient_id: str, findings: str, recommendation: str) -> str:
    """Draft a structured clinical note for a patient.
    This tool creates a draft only — it does NOT persist or transmit the note.
    Returns the complete draft text for human review."""
    from datetime import date

    today = date.today().isoformat()
    return (
        f"DRAFT CLINICAL NOTE — {today}\n"
        f"{'=' * 50}\n"
        f"Patient ID: {patient_id.upper()}\n\n"
        f"FINDINGS:\n{findings}\n\n"
        f"RECOMMENDATION:\n{recommendation}\n\n"
        f"[DRAFT — Requires clinician review before filing]\n"
    )


# Consolidated tool lists per agent role
records_tools = [lookup_patient_records, get_lab_results]
research_tools = [search_drug_interactions, search_clinical_guidelines]
drafting_tools = [draft_clinical_note]
all_tools = records_tools + research_tools + drafting_tools
```

> **Note:** The `lookup_patient_records`, `get_lab_results`, and `search_drug_interactions` tools are imported from the existing definitions in `tools.py`. Add the two new tools shown above at the bottom of the file.

#### Step 4: Write `agents/records_agent.py`

```python
# medagent_v2/agents/records_agent.py

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import operator
from typing import Annotated, TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from tools import records_tools

RECORDS_SYSTEM_PROMPT = """You are the Records Agent in a multi-agent clinical system.
Your sole responsibility: retrieve patient demographic data and lab results using the tools provided.
When you have all the information you need, produce a concise patient_summary.
Do not speculate or add clinical interpretation — just retrieve and report the data."""


class RecordsState(TypedDict):
    messages: Annotated[list, operator.add]
    patient_id: str
    question: str
    patient_summary: str   # output field — populated by the final AI message


def _llm():
    return ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(records_tools)


def records_call_model(state: RecordsState) -> dict:
    llm = _llm()
    msgs = state["messages"]
    if not msgs:
        msgs = [
            SystemMessage(content=RECORDS_SYSTEM_PROMPT),
            HumanMessage(content=f"Patient ID: {state['patient_id']}\nTask: {state['question']}"),
        ]
    response = llm.invoke(msgs)
    return {"messages": [response]}


def records_should_continue(state: RecordsState) -> str:
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return END


def records_finalise(state: RecordsState) -> dict:
    """Extract the final AI text as patient_summary."""
    last = state["messages"][-1]
    return {"patient_summary": last.content}


def build_records_agent():
    graph = StateGraph(RecordsState)
    graph.add_node("agent", records_call_model)
    graph.add_node("tools", ToolNode(records_tools))
    graph.add_node("finalise", records_finalise)
    graph.set_entry_point("agent")
    graph.add_conditional_edges(
        "agent", records_should_continue, {"tools": "tools", END: "finalise"}
    )
    graph.add_edge("tools", "agent")
    graph.add_edge("finalise", END)
    return graph.compile()


records_agent = build_records_agent()
```

#### Step 5: Write `agents/research_agent.py`

```python
# medagent_v2/agents/research_agent.py

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import operator
from typing import Annotated, TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from tools import research_tools

RESEARCH_SYSTEM_PROMPT = """You are the Research Agent in a multi-agent clinical system.
Your responsibility: check drug interactions and retrieve relevant clinical guidelines.
Use the tools provided. Summarise your findings concisely for the Drafting Agent."""


class ResearchState(TypedDict):
    messages: Annotated[list, operator.add]
    question: str
    patient_medications: str   # comma-separated list passed in from supervisor
    research_findings: str     # output field


def _llm():
    return ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(research_tools)


def research_call_model(state: ResearchState) -> dict:
    llm = _llm()
    msgs = state["messages"]
    if not msgs:
        context = state.get("patient_medications", "")
        task = state["question"]
        if context:
            task = f"{task}\nPatient medications to check: {context}"
        msgs = [
            SystemMessage(content=RESEARCH_SYSTEM_PROMPT),
            HumanMessage(content=task),
        ]
    return {"messages": [llm.invoke(msgs)]}


def research_should_continue(state: ResearchState) -> str:
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return END


def research_finalise(state: ResearchState) -> dict:
    last = state["messages"][-1]
    return {"research_findings": last.content}


def build_research_agent():
    graph = StateGraph(ResearchState)
    graph.add_node("agent", research_call_model)
    graph.add_node("tools", ToolNode(research_tools))
    graph.add_node("finalise", research_finalise)
    graph.set_entry_point("agent")
    graph.add_conditional_edges(
        "agent", research_should_continue, {"tools": "tools", END: "finalise"}
    )
    graph.add_edge("tools", "agent")
    graph.add_edge("finalise", END)
    return graph.compile()


research_agent = build_research_agent()
```

#### Step 6: Write `agents/drafting_agent.py`

```python
# medagent_v2/agents/drafting_agent.py

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import operator
from typing import Annotated, TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from tools import drafting_tools

DRAFTING_SYSTEM_PROMPT = """You are the Drafting Agent in a multi-agent clinical system.
You receive a patient summary and research findings.
Use the draft_clinical_note tool to produce a structured note.
The note is a draft only and will be reviewed by a clinician before filing."""


class DraftingState(TypedDict):
    messages: Annotated[list, operator.add]
    patient_id: str
    patient_summary: str
    research_findings: str
    draft_note: str   # output field


def _llm():
    return ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(drafting_tools)


def drafting_call_model(state: DraftingState) -> dict:
    llm = _llm()
    msgs = state["messages"]
    if not msgs:
        context = (
            f"Patient ID: {state['patient_id']}\n\n"
            f"PATIENT SUMMARY:\n{state.get('patient_summary', 'Not available')}\n\n"
            f"RESEARCH FINDINGS:\n{state.get('research_findings', 'Not available')}"
        )
        msgs = [
            SystemMessage(content=DRAFTING_SYSTEM_PROMPT),
            HumanMessage(content=f"Please draft a clinical note using the information below:\n{context}"),
        ]
    return {"messages": [llm.invoke(msgs)]}


def drafting_should_continue(state: DraftingState) -> str:
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return END


def drafting_finalise(state: DraftingState) -> dict:
    last = state["messages"][-1]
    return {"draft_note": last.content}


def build_drafting_agent():
    graph = StateGraph(DraftingState)
    graph.add_node("agent", drafting_call_model)
    graph.add_node("tools", ToolNode(drafting_tools))
    graph.add_node("finalise", drafting_finalise)
    graph.set_entry_point("agent")
    graph.add_conditional_edges(
        "agent", drafting_should_continue, {"tools": "tools", END: "finalise"}
    )
    graph.add_edge("tools", "agent")
    graph.add_edge("finalise", END)
    return graph.compile()


drafting_agent = build_drafting_agent()
```

---

### Part B: Supervisor and Failure Handling *(~60 min)*

#### Step 1: Write `supervisor.py`

```python
# medagent_v2/supervisor.py

import operator
from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, END, START
from langgraph.constants import Send

from agents.records_agent import records_agent, RecordsState
from agents.research_agent import research_agent, ResearchState
from agents.drafting_agent import drafting_agent, DraftingState


# ── Orchestrator state ─────────────────────────────────────────────────────────

class OrchestratorState(TypedDict):
    question: str
    patient_id: str
    patient_medications: str   # extracted from records, passed to research
    patient_summary: str
    research_findings: str
    draft_note: str
    errors: Annotated[list, operator.add]
    research_failure_count: int


# ── Circuit breaker config ─────────────────────────────────────────────────────

RESEARCH_FAILURE_THRESHOLD = 2


# ── Nodes ──────────────────────────────────────────────────────────────────────

def dispatch_parallel(state: OrchestratorState) -> list:
    """Fan out to Records and Research agents simultaneously using the Send API."""
    sends = [
        Send(
            "records_agent",
            RecordsState(
                messages=[],
                patient_id=state["patient_id"],
                question=state["question"],
                patient_summary="",
            ),
        ),
    ]

    # Check circuit breaker before dispatching research
    if state.get("research_failure_count", 0) < RESEARCH_FAILURE_THRESHOLD:
        sends.append(
            Send(
                "research_agent",
                ResearchState(
                    messages=[],
                    question=state["question"],
                    patient_medications=state.get("patient_medications", ""),
                    research_findings="",
                ),
            )
        )
    else:
        print(
            f"[Supervisor] Circuit breaker OPEN for research_agent "
            f"(failures={state['research_failure_count']}). Skipping."
        )

    return sends


def run_records_agent(state: RecordsState) -> dict:
    """Wrapper node: run the records subgraph and merge its output upward."""
    try:
        result = records_agent.invoke(state)
        return {
            "patient_summary": result.get("patient_summary", ""),
            "errors": [],
        }
    except Exception as exc:
        return {
            "patient_summary": "",
            "errors": [f"records_agent failed: {exc}"],
        }


def run_research_agent(state: ResearchState) -> dict:
    """Wrapper node: run the research subgraph and merge its output upward."""
    try:
        result = research_agent.invoke(state)
        return {
            "research_findings": result.get("research_findings", ""),
            "errors": [],
        }
    except Exception as exc:
        return {
            "research_findings": "",
            "errors": [f"research_agent failed: {exc}"],
            "research_failure_count": state.get("research_failure_count", 0) + 1,
        }


def collect_and_draft(state: OrchestratorState) -> dict:
    """After parallel agents complete, run the drafting agent."""
    research = state.get("research_findings") or "[Research unavailable — see errors]"
    summary = state.get("patient_summary") or "[Records unavailable — see errors]"

    draft_input = DraftingState(
        messages=[],
        patient_id=state["patient_id"],
        patient_summary=summary,
        research_findings=research,
        draft_note="",
    )
    try:
        result = drafting_agent.invoke(draft_input)
        return {"draft_note": result.get("draft_note", "")}
    except Exception as exc:
        return {
            "draft_note": "",
            "errors": [f"drafting_agent failed: {exc}"],
        }


# ── Graph assembly ─────────────────────────────────────────────────────────────

def build_supervisor():
    graph = StateGraph(OrchestratorState)

    graph.add_node("records_agent", run_records_agent)
    graph.add_node("research_agent", run_research_agent)
    graph.add_node("drafting_agent", collect_and_draft)

    # Fan out from START using conditional edges that return Send objects
    graph.add_conditional_edges(START, dispatch_parallel, ["records_agent", "research_agent"])

    # Fan in: both parallel agents must complete before drafting
    graph.add_edge("records_agent", "drafting_agent")
    graph.add_edge("research_agent", "drafting_agent")

    graph.add_edge("drafting_agent", END)

    return graph.compile()


supervisor = build_supervisor()
```

> **Why `Send` instead of regular edges?** A regular edge from node A to node B runs B once. `Send` lets you invoke the same node (or different nodes) multiple times with different input states in a single graph step. LangGraph runs all `Send` targets concurrently, making it the correct primitive for parallel fan-out.

#### Step 2: Run the full orchestration

```python
# medagent_v2/run.py

import os
from dotenv import load_dotenv
load_dotenv()

from supervisor import supervisor, OrchestratorState

question = (
    "Patient P002 has worsening symptoms. "
    "Review their records and lab results, check relevant clinical guidelines "
    "for their conditions, and draft a referral note for the nephrology team."
)

initial_state = OrchestratorState(
    question=question,
    patient_id="P002",
    patient_medications="",  # will be populated by records agent
    patient_summary="",
    research_findings="",
    draft_note="",
    errors=[],
    research_failure_count=0,
)

print("Running multi-agent orchestration...")
result = supervisor.invoke(initial_state, config={"recursion_limit": 25})

print("\n--- PATIENT SUMMARY (Records Agent) ---")
print(result["patient_summary"])

print("\n--- RESEARCH FINDINGS (Research Agent) ---")
print(result["research_findings"])

print("\n--- DRAFT NOTE (Drafting Agent) ---")
print(result["draft_note"])

if result["errors"]:
    print("\n--- ERRORS ---")
    for err in result["errors"]:
        print(f"  • {err}")
```

```bash
cd medagent_v2
python run.py
```

> **How does parallel execution work here?** LangGraph's `Send` API schedules both `records_agent` and `research_agent` in the same graph step. The runtime runs them in separate threads (or async tasks) and waits for both to complete before advancing to `drafting_agent`. You will see both outputs arrive before the draft is produced.

#### Step 3: Demonstrate graceful degradation with the circuit breaker

```python
# medagent_v2/run.py  (append)

print("\n\n" + "=" * 70)
print("CIRCUIT BREAKER DEMO — research_agent pre-tripped")
print("=" * 70)

# Pre-trip the circuit breaker by setting failure count above threshold
degraded_state = OrchestratorState(
    question="Review records for P001 and draft a summary note.",
    patient_id="P001",
    patient_medications="",
    patient_summary="",
    research_findings="",
    draft_note="",
    errors=[],
    research_failure_count=2,   # already at threshold
)

result_degraded = supervisor.invoke(degraded_state, config={"recursion_limit": 20})

print("\nDraft note produced despite skipped research agent:")
print(result_degraded["draft_note"][:500])
print("\nErrors recorded:", result_degraded["errors"])
```

#### Step 4: Write integration tests

```python
# medagent_v2/tests/test_orchestration.py

import pytest
from unittest.mock import patch, MagicMock

# We mock at the compiled subgraph level so no LLM calls are made
MOCK_PATIENT_SUMMARY = "Patient Bernard Okafor, 54, AF + CKD. INR 3.8 (HIGH). Digoxin 2.4 (HIGH)."
MOCK_RESEARCH_FINDINGS = "Guideline: DOACs preferred over warfarin in CKD. Digoxin toxicity risk elevated."
MOCK_DRAFT_NOTE = "DRAFT CLINICAL NOTE\nPatient: P002\nFindings: ...\nRecommendation: Urgent nephrology referral."


@pytest.fixture
def base_state():
    from supervisor import OrchestratorState
    return OrchestratorState(
        question="Review P002 and draft a referral note.",
        patient_id="P002",
        patient_medications="",
        patient_summary="",
        research_findings="",
        draft_note="",
        errors=[],
        research_failure_count=0,
    )


@patch("supervisor.records_agent")
@patch("supervisor.research_agent")
@patch("supervisor.drafting_agent")
def test_full_pipeline_produces_draft_note(mock_drafting, mock_research, mock_records, base_state):
    """Full pipeline: all agents succeed → non-empty draft note."""
    mock_records.invoke.return_value = {"patient_summary": MOCK_PATIENT_SUMMARY}
    mock_research.invoke.return_value = {"research_findings": MOCK_RESEARCH_FINDINGS}
    mock_drafting.invoke.return_value = {"draft_note": MOCK_DRAFT_NOTE}

    from supervisor import build_supervisor
    sv = build_supervisor()
    result = sv.invoke(base_state, config={"recursion_limit": 20})

    assert result["draft_note"] != "", "Draft note must be non-empty"
    assert result["errors"] == [], f"Unexpected errors: {result['errors']}"


@patch("supervisor.records_agent")
@patch("supervisor.research_agent")
@patch("supervisor.drafting_agent")
def test_circuit_breaker_skips_research_after_failures(mock_drafting, mock_research, mock_records, base_state):
    """Circuit breaker: research agent pre-tripped → skip research, still produce draft."""
    mock_records.invoke.return_value = {"patient_summary": MOCK_PATIENT_SUMMARY}
    mock_research.invoke.side_effect = RuntimeError("Research service unavailable")
    mock_drafting.invoke.return_value = {"draft_note": MOCK_DRAFT_NOTE}

    base_state["research_failure_count"] = 2  # pre-trip

    from supervisor import build_supervisor
    sv = build_supervisor()
    result = sv.invoke(base_state, config={"recursion_limit": 20})

    # Research agent should NOT have been called (circuit is open)
    mock_research.invoke.assert_not_called()
    assert result["draft_note"] != ""


@patch("supervisor.records_agent")
@patch("supervisor.research_agent")
@patch("supervisor.drafting_agent")
def test_output_state_has_required_fields(mock_drafting, mock_research, mock_records, base_state):
    """Output state must contain patient_summary and draft_note fields."""
    mock_records.invoke.return_value = {"patient_summary": MOCK_PATIENT_SUMMARY}
    mock_research.invoke.return_value = {"research_findings": MOCK_RESEARCH_FINDINGS}
    mock_drafting.invoke.return_value = {"draft_note": MOCK_DRAFT_NOTE}

    from supervisor import build_supervisor
    sv = build_supervisor()
    result = sv.invoke(base_state, config={"recursion_limit": 20})

    assert "patient_summary" in result, "patient_summary missing from output state"
    assert "draft_note" in result, "draft_note missing from output state"
    assert result["patient_summary"]  # non-empty
    assert result["draft_note"]       # non-empty
```

Run the tests:

```bash
cd medagent_v2
pytest tests/ -v
```

Expected output:

```
tests/test_orchestration.py::test_full_pipeline_produces_draft_note PASSED
tests/test_orchestration.py::test_circuit_breaker_skips_research_after_failures PASSED
tests/test_orchestration.py::test_output_state_has_required_fields PASSED

3 passed in 0.8s
```

#### Step 5: Run two complex scenarios end-to-end

```python
# medagent_v2/run.py  (append)

COMPLEX_SCENARIOS = [
    {
        "patient_id": "P002",
        "question": (
            "Bernard Okafor (P002) has worsening oedema and his INR came back high. "
            "Review his full record and labs, check guidelines for AF management in CKD, "
            "and draft a referral note to nephrology."
        ),
    },
    {
        "patient_id": "P003",
        "question": (
            "Chen Wei (P003) is on methotrexate for RA. Her latest ALT is elevated and WBC is low. "
            "Review her records and labs, check methotrexate monitoring guidelines, "
            "and draft a note for the rheumatology team flagging the toxicity concern."
        ),
    },
]

for scenario in COMPLEX_SCENARIOS:
    print("\n" + "=" * 70)
    print(f"SCENARIO — Patient {scenario['patient_id']}")
    print("=" * 70)
    state = OrchestratorState(
        question=scenario["question"],
        patient_id=scenario["patient_id"],
        patient_medications="",
        patient_summary="",
        research_findings="",
        draft_note="",
        errors=[],
        research_failure_count=0,
    )
    result = supervisor.invoke(state, config={"recursion_limit": 25})
    print("\n[DRAFT NOTE]")
    print(result["draft_note"])
    if result["errors"]:
        print("[ERRORS]", result["errors"])
```

```bash
python run.py
```

---

### References

1. LangGraph multi-agent patterns and `Send` API: <https://langchain-ai.github.io/langgraph/concepts/multi_agent/>
2. LangGraph subgraphs as compiled runnables: <https://langchain-ai.github.io/langgraph/how-tos/subgraph/>
3. Circuit breaker pattern in distributed systems (Martin Fowler): <https://martinfowler.com/bliki/CircuitBreaker.html>
4. LangChain integration testing with mocks: <https://python.langchain.com/docs/how_to/testing/>
5. LangGraph parallel node execution: <https://langchain-ai.github.io/langgraph/concepts/low_level/#send>
