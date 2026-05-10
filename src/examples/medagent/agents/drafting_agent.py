"""
agents/drafting_agent.py — Drafting specialist subgraph (Chapter 22).

The Drafting Agent receives assembled research findings and patient record
summaries, then synthesises them into a draft clinical note for clinician
review. It does not call any tools — it is a pure synthesis agent.

The separation is deliberate: if upstream agents fail, the Drafting Agent
receives explicit error markers in its input rather than silent gaps, and
the draft note clearly documents which data is unavailable.

Factory function: get_drafting_agent() returns a compiled LangGraph app.
"""

import json
import logging
import operator
import os
import sys
from typing import Annotated, Optional, Sequence

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Drafting agent system prompt
# ---------------------------------------------------------------------------

DRAFTING_SYSTEM_PROMPT = """You are MedAgent Drafting — a clinical documentation
specialist. You receive structured research findings and patient data, and produce
a draft clinical note for clinician review.

Your draft must follow this structure:
  1. Patient Summary (demographics, primary diagnosis, current medications)
  2. Clinical Question (what was asked)
  3. Research Findings (drug interactions with severity, guideline excerpts)
  4. Lab Results (relevant values with flags and reference ranges)
  5. Assessment and Recommendation (DRAFT — clearly marked for clinician review)
  6. Missing or Uncertain Data (any gaps in the retrieved information)

Rules:
- Always mark the Assessment and Recommendation section as DRAFT PENDING CLINICIAN REVIEW.
- Never omit the Missing or Uncertain Data section — it is safety-critical.
- If research_output is null or contains an error, state explicitly that research
  data is unavailable and do not fabricate findings.
- If records_output is null or contains an error, state explicitly that patient
  data is unavailable.
- Write clearly for a clinician reader, not for a machine."""

# ---------------------------------------------------------------------------
# Drafting agent state
# ---------------------------------------------------------------------------


class DraftingState(TypedDict):
    """Isolated state for the Drafting Agent subgraph."""

    messages: Annotated[Sequence[BaseMessage], operator.add]
    question: str
    patient_summary: Optional[str]
    research_findings: Optional[str]
    research_error: Optional[str]
    records_error: Optional[str]
    draft_note: Optional[str]


# ---------------------------------------------------------------------------
# Graph nodes
# ---------------------------------------------------------------------------


def drafting_call_model(state: DraftingState) -> dict:
    """LLM synthesis node for the Drafting Agent. No tools are bound."""
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.1,  # Slight creativity for fluent clinical prose
        api_key=os.environ["OPENAI_API_KEY"],
    )

    patient_data = state.get("patient_summary") or "NOT AVAILABLE"
    research_data = state.get("research_findings") or "NOT AVAILABLE"
    research_err = state.get("research_error")
    records_err = state.get("records_error")

    user_content = (
        f"Clinical Question: {state['question']}\n\n"
        f"Patient Record Summary:\n{patient_data}\n"
    )
    if records_err:
        user_content += f"\nRECORDS ERROR: {records_err}\n"

    user_content += f"\nResearch Findings:\n{research_data}\n"
    if research_err:
        user_content += f"\nRESEARCH ERROR: {research_err}\n"

    user_content += (
        "\nPlease draft a clinical note following the structure in your instructions."
    )

    messages = [
        SystemMessage(content=DRAFTING_SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]
    response = llm.invoke(messages)
    return {"messages": [response]}


def drafting_extract_note(state: DraftingState) -> dict:
    """Post-processing node: extract the final answer as draft_note."""
    messages = list(state["messages"])
    if messages:
        last = messages[-1]
        note = last.content if hasattr(last, "content") else str(last)
    else:
        note = "Could not produce draft note."
    return {"draft_note": note}


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------


def get_drafting_agent():
    """Build and compile the Drafting Agent as a LangGraph subgraph.

    Returns a compiled LangGraph app with DraftingState.
    The final state includes a 'draft_note' field with the synthesised note.
    No tools are bound — this agent only calls the LLM once.
    """
    graph = StateGraph(DraftingState)
    graph.add_node("agent", drafting_call_model)
    graph.add_node("extract_note", drafting_extract_note)

    graph.set_entry_point("agent")
    graph.add_edge("agent", "extract_note")
    graph.add_edge("extract_note", END)

    return graph.compile()


def run_drafting_agent(
    question: str,
    patient_summary: Optional[str] = None,
    research_findings: Optional[str] = None,
    research_error: Optional[str] = None,
    records_error: Optional[str] = None,
) -> str:
    """Convenience function: run the Drafting Agent and return the draft note.

    Args:
        question:          The original clinical question.
        patient_summary:   Output from the Records Agent (JSON string or None).
        research_findings: Output from the Research Agent (JSON string or None).
        research_error:    Error message if Research Agent failed (or None).
        records_error:     Error message if Records Agent failed (or None).

    Returns:
        The draft clinical note as a string.
    """
    agent = get_drafting_agent()
    initial_state: DraftingState = {
        "messages": [],
        "question": question,
        "patient_summary": patient_summary,
        "research_findings": research_findings,
        "research_error": research_error,
        "records_error": records_error,
        "draft_note": None,
    }

    result = agent.invoke(initial_state, config={"recursion_limit": 5})
    return result.get("draft_note", "Draft not produced.")


# Pre-compiled singleton
drafting_agent = get_drafting_agent()


# ---------------------------------------------------------------------------
# Standalone runner for testing
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    sample_patient_summary = json.dumps(
        {
            "patient_id": "PAT-00123",
            "name": "Jane Doe",
            "age": 67,
            "primary_diagnosis": "Atrial fibrillation",
            "current_medications": [
                {"name": "warfarin", "dose_mg": 5, "frequency": "daily"},
                {"name": "metoprolol", "dose_mg": 25, "frequency": "twice daily"},
            ],
            "lab_results": [
                {"test_type": "INR", "value": 2.8, "flag": "normal"},
                {"test_type": "creatinine", "value": 1.4, "flag": "high"},
            ],
        },
        indent=2,
    )

    sample_research_findings = json.dumps(
        {
            "drug_interactions": [
                {
                    "drug_a": "warfarin",
                    "drug_b": "aspirin",
                    "severity": "major",
                    "mechanism": "Additive anticoagulation + platelet inhibition.",
                    "clinical_recommendation": "Avoid unless benefit outweighs bleeding risk.",
                }
            ],
            "guideline_excerpts": [
                "AF: target INR 2.0–3.0 on warfarin. DOACs preferred for new diagnoses."
            ],
            "summary": "Major warfarin-aspirin interaction identified. Avoid combination.",
            "confidence": "high",
        },
        indent=2,
    )

    draft = run_drafting_agent(
        question=(
            "Patient PAT-00123 is on warfarin. GP wants to add aspirin 81mg. "
            "Check interaction and review INR."
        ),
        patient_summary=sample_patient_summary,
        research_findings=sample_research_findings,
    )

    print("Draft Clinical Note:")
    print(draft)
