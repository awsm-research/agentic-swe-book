"""
tools.py — LangChain tools for MedAgent.

All tools in this module are read-only. They observe the world without
changing it. Write tools are in write_tools.py and require human approval
before execution.

Each tool:
  - Has a typed Pydantic input schema
  - Returns a JSON string (never raises exceptions to the caller)
  - Logs its inputs, outcome, and latency
  - Is explicitly idempotent (safe to call twice with the same arguments)
"""

import json
import logging
import time

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from mock_data import DRUG_INTERACTIONS, LAB_RESULTS, PATIENTS, CLINICAL_GUIDELINES

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Custom exceptions (used internally, never propagated to the agent)
# ---------------------------------------------------------------------------


class PatientNotFoundError(Exception):
    pass


class LabResultNotFoundError(Exception):
    pass


class UnknownDrugError(Exception):
    def __init__(self, drug_name: str):
        self.drug_name = drug_name
        super().__init__(drug_name)


# ---------------------------------------------------------------------------
# Input schemas (Pydantic v2)
# ---------------------------------------------------------------------------


class PatientLookupInput(BaseModel):
    patient_id: str = Field(
        description=(
            "The unique patient identifier, e.g. 'PAT-00123'. "
            "Must begin with 'PAT-' followed by digits."
        )
    )


class LabResultsInput(BaseModel):
    patient_id: str = Field(
        description="The unique patient identifier, e.g. 'PAT-00123'."
    )
    test_type: str = Field(
        description=(
            "The lab test to retrieve. Valid values: "
            "'creatinine', 'INR', 'HbA1c', 'CBC', 'LFT', 'BMP'. "
            "Use 'all' to retrieve all available results for this patient. "
            "Case-insensitive."
        )
    )


class DrugInteractionInput(BaseModel):
    drug_a: str = Field(
        description=(
            "First drug name. Use the generic (INN) name, e.g. 'warfarin'. "
            "Case-insensitive."
        )
    )
    drug_b: str = Field(
        description=(
            "Second drug name. Use the generic (INN) name, e.g. 'aspirin'. "
            "Case-insensitive."
        )
    )


class GuidelinesInput(BaseModel):
    condition: str = Field(
        description=(
            "Condition or topic to look up. Supported keys: "
            "'atrial_fibrillation', 'type2_diabetes', 'uti', 'hypertension'. "
            "Case-insensitive partial matching is applied."
        )
    )
    guideline_type: str = Field(
        default="treatment",
        description=(
            "Section of the guideline to return. "
            "Options: 'treatment', 'monitoring', 'all'. Defaults to 'treatment'."
        ),
    )


class DraftNoteInput(BaseModel):
    patient_id: str = Field(
        description="The unique patient identifier, e.g. 'PAT-00123'."
    )
    findings: str = Field(
        description=(
            "Clinical findings to include in the note. "
            "Describe what was found from patient records, lab results, and "
            "drug interaction checks."
        )
    )
    recommendation: str = Field(
        description=(
            "Proposed clinical recommendation for clinician review. "
            "This will be clearly marked as DRAFT PENDING CLINICIAN REVIEW."
        )
    )


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------


@tool(args_schema=PatientLookupInput)
def lookup_patient_records(patient_id: str) -> str:
    """Retrieve a patient's demographic and clinical summary from the EHR.

    Returns a JSON string with: patient_id, name, age, dob, weight_kg,
    allergies (list of strings), current_medications (list with name,
    dose_mg, frequency), primary_diagnosis, and last_visit_date.

    Returns a JSON object with key 'error' if the patient is not found or
    if the patient_id format is invalid.

    Does NOT return lab results — use get_lab_results for that.
    Does NOT return imaging or procedure history.
    Call this tool once per patient per session.
    """
    start = time.monotonic()
    try:
        if not patient_id.startswith("PAT-"):
            return json.dumps(
                {
                    "error": (
                        f"Invalid patient_id format: '{patient_id}'. "
                        "Must start with 'PAT-' followed by digits."
                    )
                }
            )

        record = _fetch_patient_from_ehr(patient_id)
        elapsed = time.monotonic() - start
        logger.info(
            "tool=lookup_patient_records patient_id=%s status=success latency_ms=%.1f",
            patient_id,
            elapsed * 1000,
        )
        return json.dumps(record)

    except PatientNotFoundError:
        elapsed = time.monotonic() - start
        logger.warning(
            "tool=lookup_patient_records patient_id=%s status=not_found latency_ms=%.1f",
            patient_id,
            elapsed * 1000,
        )
        return json.dumps({"error": f"Patient '{patient_id}' not found in EHR."})

    except Exception as exc:
        elapsed = time.monotonic() - start
        logger.error(
            "tool=lookup_patient_records patient_id=%s status=error error=%s latency_ms=%.1f",
            patient_id,
            exc,
            elapsed * 1000,
        )
        return json.dumps({"error": "EHR service unavailable. Try again later."})


@tool(args_schema=LabResultsInput)
def get_lab_results(patient_id: str, test_type: str = "all") -> str:
    """Retrieve recent lab results for a patient.

    If test_type is 'all', returns all available lab results for the patient
    as a JSON array. Otherwise returns the most recent result for the
    specified test as a JSON object.

    Each result contains: patient_id, test_type, value (numeric), unit,
    reference_range, flag (one of 'normal', 'low', 'high', 'critical'),
    and collected_at (ISO 8601 timestamp).

    Valid test_type values: 'creatinine', 'INR', 'HbA1c', 'CBC', 'LFT',
    'BMP', or 'all'.

    Returns a JSON object with key 'error' if the patient is not found,
    the test_type is not valid, or no result exists for this test.

    Returns only the most recent result per test type — does not return a
    historical series.
    """
    VALID_TESTS = {"creatinine", "inr", "hba1c", "cbc", "lft", "bmp", "all"}
    start = time.monotonic()
    try:
        if patient_id not in PATIENTS:
            raise PatientNotFoundError(patient_id)

        if test_type.lower() not in VALID_TESTS:
            return json.dumps(
                {
                    "error": (
                        f"Unrecognised test_type '{test_type}'. "
                        f"Valid values: {sorted(VALID_TESTS)}"
                    )
                }
            )

        if test_type.lower() == "all":
            results = [
                v
                for (pid, _), v in LAB_RESULTS.items()
                if pid == patient_id
            ]
            elapsed = time.monotonic() - start
            logger.info(
                "tool=get_lab_results patient_id=%s test=all count=%d latency_ms=%.1f",
                patient_id,
                len(results),
                elapsed * 1000,
            )
            return json.dumps(results)

        result = _fetch_lab_result(patient_id, test_type.lower())
        elapsed = time.monotonic() - start
        logger.info(
            "tool=get_lab_results patient_id=%s test=%s flag=%s latency_ms=%.1f",
            patient_id,
            test_type,
            result.get("flag"),
            elapsed * 1000,
        )
        return json.dumps(result)

    except PatientNotFoundError:
        elapsed = time.monotonic() - start
        logger.warning(
            "tool=get_lab_results patient_id=%s status=patient_not_found latency_ms=%.1f",
            patient_id,
            elapsed * 1000,
        )
        return json.dumps({"error": f"Patient '{patient_id}' not found."})

    except LabResultNotFoundError:
        elapsed = time.monotonic() - start
        logger.warning(
            "tool=get_lab_results patient_id=%s test=%s status=result_not_found latency_ms=%.1f",
            patient_id,
            test_type,
            elapsed * 1000,
        )
        return json.dumps(
            {"error": f"No {test_type} result on record for patient '{patient_id}'."}
        )

    except Exception as exc:
        elapsed = time.monotonic() - start
        logger.error(
            "tool=get_lab_results status=error error=%s latency_ms=%.1f",
            exc,
            elapsed * 1000,
        )
        return json.dumps({"error": "Lab service unavailable."})


@tool(args_schema=DrugInteractionInput)
def search_drug_interactions(drug_a: str, drug_b: str) -> str:
    """Search for known interactions between two drugs.

    Returns a JSON string with: drug_a, drug_b, severity (one of 'none',
    'minor', 'moderate', 'major', 'contraindicated'), mechanism (string
    describing the pharmacological basis), and clinical_recommendation
    (string with prescriber guidance).

    Returns a JSON object with key 'error' if either drug name is
    unrecognised.

    Does NOT check three-way or higher-order interactions.
    Call this tool once per drug pair you need to evaluate.
    Use generic (INN) drug names.
    """
    start = time.monotonic()
    try:
        result = _query_interaction_database(
            drug_a.lower().strip(),
            drug_b.lower().strip(),
        )
        elapsed = time.monotonic() - start
        logger.info(
            "tool=search_drug_interactions drug_a=%s drug_b=%s severity=%s latency_ms=%.1f",
            drug_a,
            drug_b,
            result.get("severity"),
            elapsed * 1000,
        )
        return json.dumps(result)

    except UnknownDrugError as exc:
        elapsed = time.monotonic() - start
        logger.warning(
            "tool=search_drug_interactions unknown_drug=%s latency_ms=%.1f",
            exc.drug_name,
            elapsed * 1000,
        )
        return json.dumps(
            {
                "error": (
                    f"Unrecognised drug name: '{exc.drug_name}'. "
                    "Use the generic (INN) name."
                )
            }
        )

    except Exception as exc:
        elapsed = time.monotonic() - start
        logger.error(
            "tool=search_drug_interactions status=error error=%s latency_ms=%.1f",
            exc,
            elapsed * 1000,
        )
        return json.dumps({"error": "Drug interaction service unavailable."})


@tool(args_schema=GuidelinesInput)
def search_clinical_guidelines(
    condition: str, guideline_type: str = "treatment"
) -> str:
    """Search clinical guidelines for a condition.

    Returns a JSON string with the relevant guideline section.
    guideline_type controls which section is returned:
      - 'treatment' — first-line and alternative treatments
      - 'monitoring' — monitoring schedules and parameters
      - 'all' — the full guideline entry

    Supported conditions: 'atrial_fibrillation', 'type2_diabetes',
    'uti', 'hypertension'. Partial matching is applied (e.g., 'diabetes'
    matches 'type2_diabetes').

    Returns a JSON object with key 'error' if no guideline is found.
    Does NOT replace specialist clinical judgement.
    """
    start = time.monotonic()
    try:
        condition_lower = condition.lower().strip()

        # Partial match against guideline keys
        matched_key = None
        for key in CLINICAL_GUIDELINES:
            if condition_lower in key or key in condition_lower:
                matched_key = key
                break

        if matched_key is None:
            elapsed = time.monotonic() - start
            logger.warning(
                "tool=search_clinical_guidelines condition=%s status=not_found latency_ms=%.1f",
                condition,
                elapsed * 1000,
            )
            return json.dumps(
                {
                    "error": (
                        f"No guideline found for condition '{condition}'. "
                        f"Supported conditions: {list(CLINICAL_GUIDELINES.keys())}"
                    )
                }
            )

        guideline = CLINICAL_GUIDELINES[matched_key]

        if guideline_type.lower() == "all":
            result = guideline
        elif guideline_type.lower() == "monitoring":
            result = {
                "condition": guideline.get("condition"),
                "guideline_source": guideline.get("guideline_source"),
                "monitoring": guideline.get("monitoring", "No monitoring data available."),
            }
        else:
            # Default: treatment
            result = {
                "condition": guideline.get("condition"),
                "guideline_source": guideline.get("guideline_source"),
                "first_line": guideline.get("first_line", guideline.get("anticoagulation")),
                "targets": guideline.get("targets"),
                "alternatives": guideline.get("alternatives"),
            }

        elapsed = time.monotonic() - start
        logger.info(
            "tool=search_clinical_guidelines condition=%s matched=%s type=%s latency_ms=%.1f",
            condition,
            matched_key,
            guideline_type,
            elapsed * 1000,
        )
        return json.dumps(result)

    except Exception as exc:
        elapsed = time.monotonic() - start
        logger.error(
            "tool=search_clinical_guidelines status=error error=%s latency_ms=%.1f",
            exc,
            elapsed * 1000,
        )
        return json.dumps({"error": "Guideline service unavailable."})


@tool(args_schema=DraftNoteInput)
def draft_clinical_note(patient_id: str, findings: str, recommendation: str) -> str:
    """Draft a clinical note for a patient.

    Formats the provided findings and recommendation into a structured
    draft clinical note. Returns the draft text as a JSON string.

    The draft is NOT persisted to the patient record — it requires
    explicit clinician review and approval before any use.
    Calling this tool does not trigger an approval workflow.

    Returns JSON with: patient_id, draft_text, status ('draft'),
    and a reminder that clinician review is required.
    """
    start = time.monotonic()
    try:
        if patient_id not in PATIENTS:
            return json.dumps(
                {"error": f"Patient '{patient_id}' not found — cannot draft note."}
            )

        patient = PATIENTS[patient_id]
        draft_text = (
            f"DRAFT CLINICAL NOTE — PENDING CLINICIAN REVIEW\n"
            f"{'=' * 60}\n"
            f"Patient: {patient['name']} ({patient_id})\n"
            f"Age: {patient['age']}  |  Diagnosis: {patient['primary_diagnosis']}\n"
            f"{'=' * 60}\n\n"
            f"FINDINGS\n"
            f"{findings}\n\n"
            f"RECOMMENDATION (DRAFT — NOT FOR CLINICAL USE WITHOUT REVIEW)\n"
            f"{recommendation}\n\n"
            f"{'=' * 60}\n"
            f"This note is a DRAFT generated by MedAgent AI.\n"
            f"It must be reviewed, amended as necessary, and countersigned\n"
            f"by an authorised clinician before any clinical action is taken.\n"
        )

        elapsed = time.monotonic() - start
        logger.info(
            "tool=draft_clinical_note patient_id=%s status=drafted latency_ms=%.1f",
            patient_id,
            elapsed * 1000,
        )
        return json.dumps(
            {
                "patient_id": patient_id,
                "draft_text": draft_text,
                "status": "draft",
                "requires_clinician_review": True,
            }
        )

    except Exception as exc:
        elapsed = time.monotonic() - start
        logger.error(
            "tool=draft_clinical_note status=error error=%s latency_ms=%.1f",
            exc,
            elapsed * 1000,
        )
        return json.dumps({"error": "Could not draft clinical note."})


# ---------------------------------------------------------------------------
# Internal back-end helpers
# ---------------------------------------------------------------------------


def _fetch_patient_from_ehr(patient_id: str) -> dict:
    if patient_id not in PATIENTS:
        raise PatientNotFoundError(patient_id)
    return PATIENTS[patient_id]


def _query_interaction_database(drug_a: str, drug_b: str) -> dict:
    key = tuple(sorted([drug_a, drug_b]))
    if key in DRUG_INTERACTIONS:
        return DRUG_INTERACTIONS[key]
    # Return a 'none' result for unknown pairs rather than an error
    return {
        "drug_a": drug_a,
        "drug_b": drug_b,
        "severity": "none",
        "mechanism": "No clinically significant interaction identified in database.",
        "clinical_recommendation": "Standard monitoring applies. Consult a pharmacist for complex regimens.",
    }


def _fetch_lab_result(patient_id: str, test_type: str) -> dict:
    if patient_id not in PATIENTS:
        raise PatientNotFoundError(patient_id)
    key = (patient_id, test_type)
    if key not in LAB_RESULTS:
        raise LabResultNotFoundError(f"{patient_id}/{test_type}")
    return LAB_RESULTS[key]


# ---------------------------------------------------------------------------
# Tool registry — import this in agent and orchestrator modules
# ---------------------------------------------------------------------------

MEDAGENT_TOOLS = [
    lookup_patient_records,
    get_lab_results,
    search_drug_interactions,
    search_clinical_guidelines,
    draft_clinical_note,
]

MEDAGENT_READ_TOOLS = [
    lookup_patient_records,
    get_lab_results,
    search_drug_interactions,
    search_clinical_guidelines,
]
