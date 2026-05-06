# pii_guard.py
import logging

from presidio_analyzer import AnalyzerEngine

_analyzer = AnalyzerEngine()
_log = logging.getLogger(__name__)


def check_for_pii(text: str, threshold: float = 0.7) -> list[str]:
    """Return detected PII entity types above the confidence threshold."""
    results = _analyzer.analyze(text=text, language="en")
    return [r.entity_type for r in results if r.score > threshold]


def safe_prompt(text: str) -> str:
    """Return the prompt unchanged, or raise ValueError if PII is detected."""
    found = check_for_pii(text)
    if found:
        raise ValueError(
            f"Prompt contains potential PII ({found}). "
            "Remove personal data before sending to external AI services."
        )
    return text


def sanitize_prompt(text: str) -> str:
    """Anonymise PII in text and log a warning when redaction occurs."""
    from anonymize_prompt import anonymize_prompt
    found = check_for_pii(text)
    if not found:
        return text
    sanitized = anonymize_prompt(text)
    _log.warning("PII redacted from prompt: %s → anonymised before sending", found)
    return sanitized
