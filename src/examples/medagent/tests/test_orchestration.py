"""
tests/test_orchestration.py — Integration tests for MedAgent orchestration (Chapter 22).

Tests the full multi-agent pipeline with deterministic mock tools.
All LLM calls go to real OpenAI (gpt-4o-mini); all tool I/O is mocked.

Tests:
  - test_full_pipeline_produces_draft_note
  - test_circuit_breaker_activates
  - test_output_state_has_required_fields
"""

import json
import os
import sys
import uuid
from unittest.mock import MagicMock, patch

import pytest

# Allow importing from the medagent root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ---------------------------------------------------------------------------
# Deterministic mock tool responses
# ---------------------------------------------------------------------------

MOCK_PATIENT_RECORD = json.dumps(
    {
        "patient_id": "PAT-00123",
        "name": "Jane Doe",
        "age": 67,
        "weight_kg": 72.5,
        "allergies": ["penicillin"],
        "current_medications": [
            {"name": "warfarin", "dose_mg": 5, "frequency": "daily"},
            {"name": "metoprolol", "dose_mg": 25, "frequency": "twice daily"},
        ],
        "primary_diagnosis": "Atrial fibrillation",
        "last_visit_date": "2026-04-15",
    }
)

MOCK_LAB_RESULT_INR = json.dumps(
    {
        "patient_id": "PAT-00123",
        "test_type": "INR",
        "value": 2.8,
        "unit": "ratio",
        "reference_range": "2.0-3.0",
        "flag": "normal",
        "collected_at": "2026-05-08T09:14:00Z",
    }
)

MOCK_DRUG_INTERACTION = json.dumps(
    {
        "drug_a": "warfarin",
        "drug_b": "aspirin",
        "severity": "major",
        "mechanism": "Additive anticoagulation and platelet inhibition.",
        "clinical_recommendation": "Avoid unless benefit clearly outweighs bleeding risk.",
    }
)

MOCK_GUIDELINES = json.dumps(
    {
        "condition": "Atrial Fibrillation",
        "guideline_source": "ESC 2023",
        "first_line": "Warfarin (target INR 2.0-3.0) or DOAC",
        "targets": {"INR": "2.0-3.0"},
    }
)

MOCK_DRAFT_NOTE = json.dumps(
    {
        "patient_id": "PAT-00123",
        "draft_text": (
            "DRAFT CLINICAL NOTE — PENDING CLINICIAN REVIEW\n"
            "Patient: Jane Doe (PAT-00123)\n"
            "Findings: Warfarin-aspirin interaction is MAJOR.\n"
            "Recommendation: Avoid aspirin. Monitor INR closely.\n"
            "DRAFT PENDING CLINICIAN REVIEW"
        ),
        "status": "draft",
        "requires_clinician_review": True,
    }
)


def _mock_lookup_patient_records(patient_id: str) -> str:
    if patient_id == "PAT-00123":
        return MOCK_PATIENT_RECORD
    return json.dumps({"error": f"Patient '{patient_id}' not found."})


def _mock_get_lab_results(patient_id: str, test_type: str = "all") -> str:
    return MOCK_LAB_RESULT_INR


def _mock_search_drug_interactions(drug_a: str, drug_b: str) -> str:
    pair = {drug_a.lower(), drug_b.lower()}
    if pair == {"warfarin", "aspirin"}:
        return MOCK_DRUG_INTERACTION
    return json.dumps(
        {
            "drug_a": drug_a,
            "drug_b": drug_b,
            "severity": "none",
            "mechanism": "No significant interaction.",
            "clinical_recommendation": "Standard monitoring.",
        }
    )


def _mock_search_clinical_guidelines(
    condition: str, guideline_type: str = "treatment"
) -> str:
    return MOCK_GUIDELINES


def _mock_draft_clinical_note(
    patient_id: str, findings: str, recommendation: str
) -> str:
    return MOCK_DRAFT_NOTE


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def patch_tool_backends():
    """Patch all tool backend functions to return deterministic mock data.

    This replaces the internal back-end calls in tools.py so the tools
    return mock data without hitting any real EHR or drug DB.
    """
    with (
        patch(
            "tools._fetch_patient_from_ehr",
            side_effect=lambda pid: json.loads(
                _mock_lookup_patient_records(pid)
            ),
        ),
        patch(
            "tools._fetch_lab_result",
            side_effect=lambda pid, tt: json.loads(_mock_get_lab_results(pid, tt)),
        ),
        patch(
            "tools._query_interaction_database",
            side_effect=lambda da, db: json.loads(
                _mock_search_drug_interactions(da, db)
            ),
        ),
    ):
        yield


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestOrchestrationPipeline:
    """Integration tests for the MedAgent multi-agent orchestration."""

    def test_full_pipeline_produces_draft_note(self):
        """Full pipeline with mock tools produces a non-empty draft note.

        The draft note must contain the patient name or ID and at least one
        clinical term from the question (warfarin or aspirin).
        """
        from supervisor import run_orchestration

        result = run_orchestration(
            question=(
                "Patient PAT-00123 is on warfarin. GP wants to add aspirin 81mg. "
                "Check interactions and retrieve her INR."
            ),
            patient_id="PAT-00123",
            session_id=str(uuid.uuid4()),
        )

        assert result["draft_note"] is not None, "draft_note must not be None"
        assert len(result["draft_note"]) > 50, "draft_note must be non-trivially long"

        draft_lower = result["draft_note"].lower()
        assert (
            "warfarin" in draft_lower or "aspirin" in draft_lower
        ), "draft_note must reference drugs from the question"

    def test_circuit_breaker_activates(self):
        """When research_agent fails, errors are recorded and draft is still produced.

        Simulates the research node raising an exception. Verifies that:
          - The errors list is populated with the failure message.
          - The draft_note is still produced (from records data only).
          - Partial results are returned, not a total failure.
        """
        from supervisor import run_orchestration

        original_run_research = None

        def failing_research_node(state):
            raise RuntimeError("Simulated research service outage")

        with patch(
            "supervisor.run_research_node",
            side_effect=failing_research_node,
        ):
            result = run_orchestration(
                question="Check drug interactions for PAT-00123.",
                patient_id="PAT-00123",
                session_id=str(uuid.uuid4()),
            )

        # Errors list should be populated
        errors = result.get("errors", [])
        assert len(errors) > 0, "errors list must be non-empty after research failure"
        assert any(
            "research" in str(e).lower() or "error" in str(e).lower()
            for e in errors
        ), "errors must reference the research agent failure"

        # Draft should still be produced (partial results > no result)
        assert result.get("draft_note") is not None, (
            "draft_note must still be produced even when research agent fails"
        )

    def test_output_state_has_required_fields(self):
        """Final orchestration state contains all required output fields."""
        from supervisor import run_orchestration

        result = run_orchestration(
            question="Retrieve record and drug interactions for PAT-00123.",
            patient_id="PAT-00123",
            session_id=str(uuid.uuid4()),
        )

        required_fields = ["patient_summary", "research_findings", "draft_note", "errors"]
        for field in required_fields:
            assert field in result, (
                f"Required field '{field}' missing from orchestration result. "
                f"Available keys: {list(result.keys())}"
            )

        # patient_summary and draft_note should be strings when produced
        if result["patient_summary"] is not None:
            assert isinstance(result["patient_summary"], str), (
                "patient_summary must be a string"
            )
        if result["draft_note"] is not None:
            assert isinstance(result["draft_note"], str), "draft_note must be a string"

        # errors must be a list
        assert isinstance(result["errors"], list), "errors must be a list"


class TestCircuitBreaker:
    """Unit tests for circuit breaker logic in supervisor."""

    def test_circuit_breaker_state_reflected_in_dispatch(self):
        """When research_failures >= 2, dispatch skips the research agent."""
        from supervisor import supervisor_dispatch, OrchestratorState

        state_with_failures: OrchestratorState = {
            "question": "Test question",
            "patient_id": "PAT-00123",
            "session_id": "test-001",
            "patient_summary": None,
            "research_findings": None,
            "draft_note": None,
            "errors": [],
            "research_failures": 2,  # Threshold reached
        }

        sends = supervisor_dispatch(state_with_failures)

        # Only the records Send should be present — research is skipped
        assert len(sends) == 1, (
            "With research_failures >= 2, only records_node should be dispatched"
        )
        # The single Send should target records_node
        assert sends[0].node == "records_node", (
            f"Expected Send to records_node, got {sends[0].node}"
        )

    def test_circuit_closed_when_no_failures(self):
        """With zero failures, both research and records agents are dispatched."""
        from supervisor import supervisor_dispatch, OrchestratorState

        state_no_failures: OrchestratorState = {
            "question": "Test question",
            "patient_id": "PAT-00123",
            "session_id": "test-002",
            "patient_summary": None,
            "research_findings": None,
            "draft_note": None,
            "errors": [],
            "research_failures": 0,
        }

        sends = supervisor_dispatch(state_no_failures)

        assert len(sends) == 2, (
            "With no failures, both research_node and records_node should be dispatched"
        )
        node_names = {s.node for s in sends}
        assert node_names == {"research_node", "records_node"}, (
            f"Expected both nodes dispatched, got: {node_names}"
        )
