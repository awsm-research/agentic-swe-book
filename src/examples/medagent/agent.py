"""
agent.py — Single-agent LangGraph ReAct loop for MedAgent (Chapter 21).

Implements the observation-action loop described in Chapter 21.
The graph has two nodes (agent, tools) connected by a conditional edge.
The agent node calls the LLM; the tools node executes any tool calls.

Usage:
    python agent.py                         # runs three example queries
    from agent import run_agent             # import the runner function
"""

import logging
import operator
import os
import sys
from typing import Annotated, Sequence

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.errors import GraphRecursionError
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict

# Allow running as a script from this directory
sys.path.insert(0, os.path.dirname(__file__))
from tools import MEDAGENT_TOOLS  # noqa: E402

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# State definition
# ---------------------------------------------------------------------------


class AgentState(TypedDict):
    """Shared state passed between all nodes in the agent graph."""

    messages: Annotated[Sequence[BaseMessage], operator.add]


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are MedAgent, a clinical decision support assistant.
You assist clinicians by retrieving patient records, checking drug interactions,
reviewing lab results, searching clinical guidelines, and drafting clinical notes.
You never prescribe, diagnose, or recommend treatment without clinician review.

When answering a question:
1. Identify what information you need and which tools to call.
2. Call the tools in a logical order, checking the results before proceeding.
3. If a tool returns an error object (JSON with key 'error'), report it clearly
   rather than proceeding with missing data.
4. Summarise your findings in a structured, clinically readable format.

You have access to five read-only / draft-only tools:
- lookup_patient_records: patient demographics, medications, allergies
- get_lab_results: most recent lab result for a named test type (or 'all')
- search_drug_interactions: drug-drug interaction checking (one pair at a time)
- search_clinical_guidelines: condition-specific treatment and monitoring guidelines
- draft_clinical_note: format findings into a draft note (NOT persisted; requires clinician approval)

You do NOT have the ability to submit orders or send communications.
Always end your response with a clear statement of what a clinician should verify."""

# ---------------------------------------------------------------------------
# Graph nodes
# ---------------------------------------------------------------------------


def call_model(state: AgentState) -> dict:
    """LLM reasoning node. Produces tool calls or a final answer."""
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=os.environ["OPENAI_API_KEY"],
    ).bind_tools(MEDAGENT_TOOLS)

    messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(state["messages"])
    response = llm.invoke(messages)
    return {"messages": [response]}


def should_continue(state: AgentState) -> str:
    """Conditional edge: route to tools if the LLM made tool calls, else END."""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------


def build_medagent_graph():
    """Construct and compile the MedAgent ReAct graph."""
    tool_node = ToolNode(MEDAGENT_TOOLS)

    graph = StateGraph(AgentState)
    graph.add_node("agent", call_model)
    graph.add_node("tools", tool_node)

    graph.set_entry_point("agent")
    graph.add_conditional_edges(
        "agent",
        should_continue,
        {"tools": "tools", END: END},
    )
    graph.add_edge("tools", "agent")

    return graph.compile()


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------


def run_agent(
    question: str,
    system_prompt: str = SYSTEM_PROMPT,
    recursion_limit: int = 15,
) -> dict:
    """Run the MedAgent ReAct loop on a clinical question.

    Args:
        question:        The clinical question or task for MedAgent.
        system_prompt:   Override the default system prompt.
        recursion_limit: Maximum graph traversals before forced termination.

    Returns:
        A dict with keys:
          'answer'             - final agent response, or None if terminated early
          'termination_reason' - 'completed', 'recursion_limit', or 'error'
          'steps'              - number of tool-calling turns taken
          'error'              - (only present on error) error message string
    """
    app = build_medagent_graph()
    initial_state: AgentState = {"messages": [HumanMessage(content=question)]}
    config = {"recursion_limit": recursion_limit}

    try:
        result = app.invoke(initial_state, config=config)
        final_message = result["messages"][-1]
        steps = sum(
            1
            for m in result["messages"]
            if hasattr(m, "tool_calls") and m.tool_calls
        )
        logger.info(
            "run_agent completed steps=%d termination=completed", steps
        )
        return {
            "answer": final_message.content,
            "termination_reason": "completed",
            "steps": steps,
        }

    except GraphRecursionError:
        logger.warning(
            "run_agent terminated at recursion_limit=%d", recursion_limit
        )
        return {
            "answer": None,
            "termination_reason": "recursion_limit",
            "steps": recursion_limit,
        }

    except Exception as exc:
        logger.error("run_agent error: %s", exc)
        return {
            "answer": None,
            "termination_reason": "error",
            "steps": -1,
            "error": str(exc),
        }


# ---------------------------------------------------------------------------
# Entry point — three example clinical queries
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    examples = [
        (
            "Patient PAT-00123 is currently on warfarin and her GP wants to add "
            "aspirin 81 mg daily for cardiovascular protection. "
            "Please: (1) retrieve her current medications and allergies, "
            "(2) check the warfarin-aspirin interaction severity, and "
            "(3) retrieve her most recent INR result. "
            "Summarise your findings for the treating clinician."
        ),
        (
            "Patient PAT-00456 is a 54-year-old with Type 2 diabetes on metformin. "
            "He is scheduled for a contrast CT scan next week. "
            "Check whether there are any interactions between metformin and contrast "
            "media, retrieve his most recent creatinine and HbA1c results, and "
            "summarise the clinical risks."
        ),
        (
            "Patient PAT-00789 has recurrent UTIs and is on nitrofurantoin. "
            "Retrieve her record, check current guidelines for recurrent UTI management, "
            "and draft a brief clinical note summarising her situation and any "
            "recommended next steps for clinician review."
        ),
    ]

    for i, question in enumerate(examples, 1):
        print(f"\n{'=' * 70}")
        print(f"EXAMPLE {i}")
        print(f"{'=' * 70}")
        print(f"Question: {question[:120]}...\n")

        result = run_agent(question, recursion_limit=15)

        print(f"Termination reason : {result['termination_reason']}")
        print(f"Steps taken        : {result['steps']}")
        print(f"\nAnswer:\n{result.get('answer') or result.get('error', 'No answer produced.')}")
