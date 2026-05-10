"""
MedChat output guardrail — Chapter 20.

Validates LLM responses before they are displayed to the user:

  1. Source citation check — response must cite at least one source.
  2. Dangerous-phrase check — must not contain prescriptive language.
  3. Hallucination check — must not cite sources absent from the
     retrieved_sources list.

Usage:
    from guardrails.output_guard import check_output, GuardResult

    result = check_output(answer, retrieved_sources=["Antibiotic Guidelines"])
    if not result.safe:
        print("Blocked:", result.reason)
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# ── Result type ────────────────────────────────────────────────────────────────


@dataclass
class GuardResult:
    """Result of an output guardrail check."""

    safe: bool
    reason: str = ""
    warnings: list[str] = field(default_factory=list)


# ── Patterns ───────────────────────────────────────────────────────────────────

# Matches "[Source: ...]" citations anywhere in the text
_SOURCE_CITATION_PATTERN = re.compile(r"\[Source:", re.IGNORECASE)

# Phrases that indicate the response is making autonomous prescriptive decisions
_DANGEROUS_PHRASES: list[tuple[str, re.Pattern]] = [
    ("prescribe",        re.compile(r"\bI\s+(?:will\s+)?prescribe\b", re.IGNORECASE)),
    ("self-medicate",    re.compile(r"\bself[-\s]?medicate\b", re.IGNORECASE)),
    ("I recommend you take",
                         re.compile(r"\bI\s+recommend\s+(?:you\s+)?take\b", re.IGNORECASE)),
    ("start the patient on",
                         re.compile(r"\bstart\s+the\s+patient\s+on\b", re.IGNORECASE)),
    ("manipulation signal",
                         re.compile(
                             r"my\s+system\s+prompt\s+is|"
                             r"i\s+have\s+been\s+instructed\s+to\s+ignore|"
                             r"as\s+an?\s+(?:unrestricted|jailbroken)\s+AI",
                             re.IGNORECASE,
                         )),
]

# Regex to extract all "[Source: X]" citation names from a response
_CITED_SOURCE_PATTERN = re.compile(r"\[Source:\s*([^\]]+)\]", re.IGNORECASE)


# ── Public API ─────────────────────────────────────────────────────────────────


def check_output(
    response: str,
    retrieved_sources: list[str],
) -> GuardResult:
    """
    Validate a MedChat response before displaying it.

    Args:
        response:          The raw LLM response text.
        retrieved_sources: List of document/chunk titles that were actually
                           retrieved and injected into the context for this query.
                           Used to detect fabricated source citations.

    Returns:
        GuardResult with safe=True if all checks pass.
        safe=False if any blocking check fails, with the reason populated.
    """
    if not response or not response.strip():
        return GuardResult(safe=False, reason="Empty response from LLM.")

    warnings: list[str] = []

    # ── Check 1: Source citation presence ─────────────────────────────────────
    has_citation = _SOURCE_CITATION_PATTERN.search(response) is not None
    if retrieved_sources and not has_citation:
        # Non-blocking warning: sources were available but none cited
        warnings.append(
            "Response does not contain a [Source: ...] citation despite "
            "retrieved context being available."
        )
        logger.warning("Output warning: no source citation found.")

    # ── Check 2: Dangerous prescriptive phrases ────────────────────────────────
    for label, pattern in _DANGEROUS_PHRASES:
        if pattern.search(response):
            logger.error(f"Output blocked — dangerous phrase detected: '{label}'")
            return GuardResult(
                safe=False,
                warnings=warnings,
                reason=(
                    f"Response contains dangerous prescriptive language ('{label}'). "
                    "MedChat must not autonomously prescribe or recommend specific "
                    "patient actions without appropriate clinical hedging."
                ),
            )

    # ── Check 3: Hallucinated source citation check ───────────────────────────
    if retrieved_sources:
        cited_names = _CITED_SOURCE_PATTERN.findall(response)
        # Normalise for comparison (lowercase, strip whitespace)
        normalised_sources = {s.lower().strip() for s in retrieved_sources}
        fabricated: list[str] = []
        for cited in cited_names:
            cited_clean = cited.lower().strip()
            # Check if the cited source matches any actual retrieved source
            # (partial match to handle section suffixes like "Antibiotic Guidelines, Section 1.2")
            if not any(
                cited_clean in norm or norm in cited_clean
                for norm in normalised_sources
            ):
                fabricated.append(cited)

        if fabricated:
            logger.warning(
                f"Output warning: possible hallucinated sources: {fabricated}"
            )
            warnings.append(
                f"Response cites source(s) not in retrieved context: {fabricated}. "
                "These may be hallucinated references."
            )
            # This is a warning, not a block, but severe cases could be escalated
            # to a block by changing the return below.

    return GuardResult(safe=True, reason="All output checks passed.", warnings=warnings)


# ── Demo / manual testing ─────────────────────────────────────────────────────


if __name__ == "__main__":
    cases = [
        (
            "Amoxicillin 500 mg TDS is recommended [Source: Antibiotic Guidelines].",
            ["Antibiotic Guidelines"],
        ),
        (
            "I prescribe you amoxicillin 500 mg. Take it three times a day.",
            ["Antibiotic Guidelines"],
        ),
        (
            "Self-medicate with paracetamol until you see a doctor.",
            [],
        ),
        (
            "Amoxicillin 500 mg is recommended [Source: Made-Up Reference 2025].",
            ["Antibiotic Guidelines"],
        ),
        (
            # No citation, but retrieved_sources is empty — should pass without warning
            "Amoxicillin is a common antibiotic.",
            [],
        ),
    ]

    for response_text, sources in cases:
        result = check_output(response_text, sources)
        status = "SAFE" if result.safe else "BLOCKED"
        print(f"[{status}] {response_text[:70]}")
        if not result.safe:
            print(f"  Reason: {result.reason}")
        if result.warnings:
            for w in result.warnings:
                print(f"  Warning: {w}")
