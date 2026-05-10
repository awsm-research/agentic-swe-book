"""
supervisor.py — Multi-agent orchestrator for MedAgent (Chapter 22).

Implements the Supervisor pattern using LangGraph's Send API for parallel
dispatch of the Research and Records agents, with a circuit breaker to
prevent cascading failures.

Architecture:
    supervisor → [research_agent, records_agent] (parallel via Send API)
              → drafting_agent (after both parallel agents complete)
              → END

Usage:
    python supervisor.py                              # demo run
    from supervisor import run_orchestration          # import runner
"""

import json
import logging
import os
import sys
import time
import uuid
from typing import Optional

from langchain_core.messages import HumanMessage
from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

# Support running from the medagent root
sys.path.insert(0, os.path.dirname(__file__))
from agents.drafting_agent import run_drafting_agent  # noqa: E402
from agents.records_agent import get_records_agent, RecordsState  # noqa: E402
from agents.research_agent import get_research_agent, ResearchState  # noqa: E402

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Orchestrator state
# ---------------------------------------------------------------------------


class OrchestratorState(TypedDict):
    """Shared state for the MedAgent supervisor graph."""

    # Inputs
    question: str
    patient_id: str
    session_id: str

    # Subagent outputs (populated as agents complete)
    patient_summary: Optional[str]
    research_findings: Optional[str]
    draft_note: Optional[str]

    # Orchestration metadata
    errors: list
    research_failures: int  # For circuit breaker


# ---------------------------------------------------------------------------
# Circuit breaker (simple stateless version based on OrchestratorState)
# ---------------------------------------------------------------------------

CIRCUIT_OPEN_THRESHOLD = 2


def _research_circuit_open(state: OrchestratorState) -> bool:
    """Return True if the research circuit breaker should be open."""
    return state.get("research_failures", 0) >= CIRCUIT_OPEN_THRESHOLD


# ---------------------------------------------------------------------------
# Supervisor dispatch node
# ---------------------------------------------------------------------------


def supervisor_dispatch(state: OrchestratorState) -> list:
    """Fan-out node: dispatch Research and Records agents in parallel.

    Implements a circuit breaker: if research_failures >= 2, skip the
    Research agent and return only the Records Send.

    Returns a list of Send objects — LangGraph executes these concurrently.
    """
    logger.info(
        "supervisor=dispatch session=%s patient=%s",
        state["session_id"],
        state["patient_id"],
    )

    records_input: RecordsState = {
        "messages": [
            HumanMessage(
                content=(
                    f"Retrieve the full patient record and all available lab results "
                    f"for patient {state['patient_id']}."
                )
            )
        ],
        "patient_id": state["patient_id"],
        "required_labs": ["INR", "creatinine", "HbA1c"],
        "patient_summary": None,
    }

    if _research_circuit_open(state):
        logger.warning(
            "supervisor=dispatch circuit_open session=%s skipping research_agent",
            state["session_id"],
        )
        return [Send("records_node", records_input)]

    research_input: ResearchState = {
        "messages": [HumanMessage(content=state["question"])],
        "question": state["question"],
        "patient_context": f"Patient ID: {state['patient_id']}",
        "research_findings": None,
    }

    return [
        Send("research_node", research_input),
        Send("records_node", records_input),
    ]


# ---------------------------------------------------------------------------
# Wrapper nodes — execute subgraphs and write to OrchestratorState
# ---------------------------------------------------------------------------


def run_research_node(state: ResearchState) -> dict:
    """Execute the Research subgraph and merge output into OrchestratorState."""
    try:
        agent = get_research_agent()
        result = agent.invoke(state, config={"recursion_limit": 10})
        findings = result.get("research_findings", "")
        logger.info("research_node=success findings_len=%d", len(findings))
        return {
            "research_findings": findings,
            "errors": [],
            "research_failures": 0,
        }
    except Exception as exc:
        logger.error("research_node=error error=%s", exc)
        return {
            "research_findings": None,
            "errors": [f"Research agent failed: {exc}"],
            "research_failures": 1,
        }


def run_records_node(state: RecordsState) -> dict:
    """Execute the Records subgraph and merge output into OrchestratorState."""
    try:
        agent = get_records_agent()
        result = agent.invoke(state, config={"recursion_limit": 10})
        summary = result.get("patient_summary", "")
        logger.info("records_node=success summary_len=%d", len(summary))
        return {
            "patient_summary": summary,
            "errors": [],
        }
    except Exception as exc:
        logger.error("records_node=error error=%s", exc)
        return {
            "patient_summary": None,
            "errors": [f"Records agent failed: {exc}"],
        }


def run_drafting_node(state: OrchestratorState) -> dict:
    """Execute the Drafting Agent with collected research and records outputs."""
    errors = state.get("errors", [])
    research_error = None
    records_error = None

    if state.get("research_findings") is None:
        research_error = "Research agent did not produce findings."
        if not any("Research agent" in e for e in errors):
            research_error = "Research data unavailable (circuit breaker or failure)."

    if state.get("patient_summary") is None:
        records_error = "Records agent did not produce a patient summary."

    logger.info(
        "drafting_node session=%s research_error=%s records_error=%s",
        state["session_id"],
        research_error,
        records_error,
    )

    draft = run_drafting_agent(
        question=state["question"],
        patient_summary=state.get("patient_summary"),
        research_findings=state.get("research_findings"),
        research_error=research_error,
        records_error=records_error,
    )

    return {"draft_note": draft}


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------


def build_supervisor_graph():
    """Compile the MedAgent supervisor orchestration graph.

    The graph uses Send API for parallel dispatch of Research and Records
    agents. Both feed into a fan-in at the drafting node.
    The errors list uses operator.add for merge-safe parallel writes.
    """
    import operator
    from typing import Annotated

    # Redefine state with merge-safe errors for LangGraph parallel fan-in
    class ParallelOrchestratorState(TypedDict):
        question: str
        patient_id: str
        session_id: str
        patient_summary: Optional[str]
        research_findings: Optional[str]
        draft_note: Optional[str]
        errors: Annotated[list, operator.add]
        research_failures: Annotated[int, operator.add]

    graph = StateGraph(ParallelOrchestratorState)

    graph.add_node("supervisor", supervisor_dispatch)
    graph.add_node("research_node", run_research_node)
    graph.add_node("records_node", run_records_node)
    graph.add_node("drafting", run_drafting_node)

    graph.set_entry_point("supervisor")

    # Fan-out: supervisor uses Send API to dispatch in parallel
    graph.add_conditional_edges(
        "supervisor",
        lambda state: supervisor_dispatch(state),
    )

    # Fan-in: both parallel nodes feed into drafting
    graph.add_edge("research_node", "drafting")
    graph.add_edge("records_node", "drafting")
    graph.add_edge("drafting", END)

    return graph.compile()


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------


def run_orchestration(
    question: str,
    patient_id: str,
    session_id: Optional[str] = None,
) -> dict:
    """Run the full MedAgent orchestration pipeline.

    Args:
        question:   The clinical question or task.
        patient_id: The patient identifier (e.g. 'PAT-00123').
        session_id: Optional session ID; generated if not provided.

    Returns:
        A dict with keys:
          'draft_note'         - synthesised clinical note draft
          'patient_summary'    - Records agent output
          'research_findings'  - Research agent output
          'errors'             - list of agent error messages (empty on success)
          'session_id'         - the session ID used
    """
    if session_id is None:
        session_id = str(uuid.uuid4())

    app = build_supervisor_graph()

    initial_state = {
        "question": question,
        "patient_id": patient_id,
        "session_id": session_id,
        "patient_summary": None,
        "research_findings": None,
        "draft_note": None,
        "errors": [],
        "research_failures": 0,
    }

    logger.info(
        "orchestration=start session=%s patient=%s", session_id, patient_id
    )
    start = time.monotonic()

    result = app.invoke(initial_state, config={"recursion_limit": 30})

    elapsed = time.monotonic() - start
    logger.info(
        "orchestration=complete session=%s elapsed_s=%.1f errors=%d",
        session_id,
        elapsed,
        len(result.get("errors", [])),
    )

    result["session_id"] = session_id
    return result


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    result = run_orchestration(
        question=(
            "Patient PAT-00123 is on warfarin 5 mg daily. "
            "Her GP wants to add aspirin 81 mg for cardioprotection. "
            "Please check the warfarin-aspirin interaction, review her recent INR, "
            "and retrieve relevant AF management guidelines."
        ),
        patient_id="PAT-00123",
        session_id=str(uuid.uuid4()),
    )

    print(f"\nErrors       : {result['errors']}")
    print(f"Session ID   : {result['session_id']}")
    print(f"\n{'=' * 70}")
    print("DRAFT CLINICAL NOTE")
    print("=" * 70)
    print(result.get("draft_note", "No draft produced."))
