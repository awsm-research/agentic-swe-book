# pip install presidio-analyzer presidio-anonymizer
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()


def detect_pii(text: str) -> list[dict]:
    """Detect PII entities in a text string."""
    results = analyzer.analyze(text=text, language="en")
    return [
        {
            "entity_type": r.entity_type,
            "start": r.start,
            "end": r.end,
            "score": r.score,
            "text": text[r.start : r.end],
        }
        for r in results
    ]


def anonymise_pii(text: str) -> str:
    """Replace PII entities with type placeholders."""
    results = analyzer.analyze(text=text, language="en")
    anonymised = anonymizer.anonymize(text=text, analyzer_results=results)
    return anonymised.text


# Example
text = "Alice Smith (alice@example.com) was assigned task #123"
print(detect_pii(text))
# [{'entity_type': 'PERSON', ...}, {'entity_type': 'EMAIL_ADDRESS', ...}]

print(anonymise_pii(text))
# "<PERSON> (<EMAIL_ADDRESS>) was assigned task #123"
