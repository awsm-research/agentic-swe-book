"""
agents/research_agent.py — Research specialist subgraph (Chapter 22).

The Research Agent queries the drug interaction database and retrieves
clinical guidelines. It is implemented as a compiled LangGraph subgraph
with its own state, system prompt, and recursion limit.

Factory function: get_research_agent() returns a compiled LangGraph app.
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
from tools import search_clinical_guidelines, search_drug_interactions  # noqa: E402

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Research agent system prompt
# ---------------------------------------------------------------------------

RESEARCH_SYSTEM_PROMPT = """You are MedAgent Research — a specialist in drug
interactions and clinical guidelines. Given a clinical question and patient
context, you:

1. Identify all drug pairs that need interaction checking from the question
   and patient context.
2. Call search_drug_interactions for each pair (one call per pair).
3. Call search_clinical_guidelines for the patient's primary condition(s).
4. Summarise the interaction findings with severity ratings.
5. Return a structured JSON response.

Your output must be valid JSON with keys:
  - drug_interactions: list of interaction result objects
  - guideline_excerpts: list of strings with relevant guideline text
  - summary: one paragraph clinical summary of the research findings
  - confidence: 'high', 'medium', or 'low' based on data completeness

Do not hallucinate drug names or interaction severities.
If a tool returns an error, include the error message in your response
and set confidence to 'low' rather than guessing.
Report all interactions found, including those with severity 'none'."""

# ---------------------------------------------------------------------------
# Research agent state
# ---------------------------------------------------------------------------


class ResearchState(TypedDict):
    """Isolated state for the Research Agent subgraph."""

    messages: Annotated[Sequence[BaseMessage], operator.add]
    question: str
    patient_context: Optional[str]
    research_findings: Optional[str]


# ---------------------------------------------------------------------------
# Graph nodes
# ---------------------------------------------------------------------------


def research_call_model(state: ResearchState) -> dict:
    """LLM reasoning node for the Research Agent."""
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=os.environ["OPENAI_API_KEY"],
    ).bind_tools([search_drug_interactions, search_clinical_guidelines])

    context = (
        f"\nPatient context: {state.get('patient_context', 'None provided')}"
    )
    system = SystemMessage(content=RESEARCH_SYSTEM_PROMPT + context)
    messages = [system] + list(state["messages"])
    response = llm.invoke(messages)
    return {"messages": [response]}


def research_should_continue(state: ResearchState) -> str:
    """Route to tools if tool calls are present, else END."""
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return END


def research_extract_findings(state: ResearchState) -> dict:
    """Post-processing node: extract the final answer as research_findings."""
    messages = list(state["messages"])
    if messages:
        last = messages[-1]
        findings = last.content if hasattr(last, "content") else str(last)
    else:
        findings = ""
    return {"research_findings": findings}


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------


def get_research_agent():
    """Build and compile the Research Agent as a LangGraph subgraph.

    Returns a compiled LangGraph app with ResearchState.
    The final state includes a 'research_findings' field containing the
    agent's compiled output as a JSON string.
    """
    tools = [search_drug_interactions, search_clinical_guidelines]
    tool_node = ToolNode(tools)

    graph = StateGraph(ResearchState)
    graph.add_node("agent", research_call_model)
    graph.add_node("tools", tool_node)
    graph.add_node("extract_findings", research_extract_findings)

    graph.set_entry_point("agent")
    graph.add_conditional_edges(
        "agent",
        research_should_continue,
        {"tools": "tools", END: "extract_findings"},
    )
    graph.add_edge("tools", "agent")
    graph.add_edge("extract_findings", END)

    return graph.compile()


# Pre-compiled singleton — import and use directly in the orchestrator
research_agent = get_research_agent()


# ---------------------------------------------------------------------------
# Standalone runner for testing
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    agent = get_research_agent()
    initial_state: ResearchState = {
        "messages": [
            HumanMessage(
                content=(
                    "Patient PAT-00123 is on warfarin 5 mg daily and metoprolol 25 mg BD. "
                    "Her GP wants to add aspirin 81 mg for cardioprotection. "
                    "Check all relevant drug interactions and retrieve AF guidelines."
                )
            )
        ],
        "question": (
            "Check warfarin-aspirin and metoprolol-warfarin interactions "
            "and retrieve atrial fibrillation guidelines."
        ),
        "patient_context": "Patient: Jane Doe, 67F, AF, warfarin, metoprolol, ramipril",
        "research_findings": None,
    }

    result = agent.invoke(initial_state, config={"recursion_limit": 10})
    print("Research Findings:")
    print(result.get("research_findings", "No findings produced."))
