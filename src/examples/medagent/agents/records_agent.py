"""
agents/records_agent.py — Records specialist subgraph (Chapter 22).

The Records Agent retrieves patient demographics, medication lists, and lab
results. It is implemented as a compiled LangGraph subgraph with its own
state, system prompt, and recursion limit.

Factory function: get_records_agent() returns a compiled LangGraph app.
"""

import logging
import operator
import os
import sys
from typing import Annotated, Optional, Sequence

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict

# Support running from the medagent root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools import get_lab_results, lookup_patient_records  # noqa: E402

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Records agent system prompt
# ---------------------------------------------------------------------------

RECORDS_SYSTEM_PROMPT = """You are MedAgent Records — a specialist in patient
data retrieval. Given a patient_id and a list of required data points, you:

1. Call lookup_patient_records to retrieve demographics and medications.
2. Call get_lab_results for each required lab test (use test_type='all' if
   a comprehensive result set is requested).
3. Compile the results into a structured JSON response.

Your output must be valid JSON with keys:
  - patient_record: the full patient record object (or null if not found)
  - lab_results: list of lab result objects (empty list if none)
  - missing_data: list of requested items not found
  - retrieval_errors: list of error messages from failed tool calls

Report errors faithfully — do not substitute missing data with assumptions.
If a tool returns an error, add the error message to retrieval_errors and
set the corresponding field to null or an empty list."""

# ---------------------------------------------------------------------------
# Records agent state
# ---------------------------------------------------------------------------


class RecordsState(TypedDict):
    """Isolated state for the Records Agent subgraph."""

    messages: Annotated[Sequence[BaseMessage], operator.add]
    patient_id: str
    required_labs: list
    patient_summary: Optional[str]


# ---------------------------------------------------------------------------
# Graph nodes
# ---------------------------------------------------------------------------


def records_call_model(state: RecordsState) -> dict:
    """LLM reasoning node for the Records Agent."""
    tools = [lookup_patient_records, get_lab_results]
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=os.environ["OPENAI_API_KEY"],
    ).bind_tools(tools)

    required = state.get("required_labs", [])
    context = (
        f"\nPatient ID to retrieve: {state['patient_id']}"
        f"\nRequired lab tests: {', '.join(required) if required else 'all available'}"
    )
    system = SystemMessage(content=RECORDS_SYSTEM_PROMPT + context)
    messages = [system] + list(state["messages"])
    response = llm.invoke(messages)
    return {"messages": [response]}


def records_should_continue(state: RecordsState) -> str:
    """Route to tools if tool calls are present, else END."""
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return END


def records_extract_summary(state: RecordsState) -> dict:
    """Post-processing node: extract the final answer as patient_summary."""
    messages = list(state["messages"])
    if messages:
        last = messages[-1]
        summary = last.content if hasattr(last, "content") else str(last)
    else:
        summary = ""
    return {"patient_summary": summary}


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------


def get_records_agent():
    """Build and compile the Records Agent as a LangGraph subgraph.

    Returns a compiled LangGraph app with RecordsState.
    The final state includes a 'patient_summary' field containing the
    agent's compiled output as a JSON string.
    """
    tools = [lookup_patient_records, get_lab_results]
    tool_node = ToolNode(tools)

    graph = StateGraph(RecordsState)
    graph.add_node("agent", records_call_model)
    graph.add_node("tools", tool_node)
    graph.add_node("extract_summary", records_extract_summary)

    graph.set_entry_point("agent")
    graph.add_conditional_edges(
        "agent",
        records_should_continue,
        {"tools": "tools", END: "extract_summary"},
    )
    graph.add_edge("tools", "agent")
    graph.add_edge("extract_summary", END)

    return graph.compile()


# Pre-compiled singleton — import and use directly in the orchestrator
records_agent = get_records_agent()


# ---------------------------------------------------------------------------
# Standalone runner for testing
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    agent = get_records_agent()
    initial_state: RecordsState = {
        "messages": [
            HumanMessage(
                content="Retrieve full record and labs for patient PAT-00123."
            )
        ],
        "patient_id": "PAT-00123",
        "required_labs": ["INR", "creatinine"],
        "patient_summary": None,
    }

    result = agent.invoke(initial_state, config={"recursion_limit": 10})
    print("Patient Summary:")
    print(result.get("patient_summary", "No summary produced."))
