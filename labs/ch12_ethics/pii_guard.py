# pii_guard.py
import anthropic
from presidio_analyzer import AnalyzerEngine

analyzer = AnalyzerEngine()
client = anthropic.Anthropic()


def safe_ai_request(prompt: str, model: str = "claude-haiku-4-5-20251001") -> str:
    """Reject prompts that contain detectable PII."""
    results = analyzer.analyze(text=prompt, language="en")

    pii_found = [r.entity_type for r in results if r.score > 0.7]
    if pii_found:
        raise ValueError(
            f"Prompt contains potential PII ({pii_found}). "
            "Remove PII before sending to external AI services."
        )

    response = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


# Usage
try:
    result = safe_ai_request(
        "Fix the bug in this function. The user john.doe@example.com reported it."
    )
except ValueError as e:
    print(f"PII guard blocked request: {e}")
    # Sanitise the prompt: remove the email address before retrying
