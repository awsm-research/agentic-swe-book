# anonymize_prompt.py
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

_analyzer = AnalyzerEngine()
_anonymizer = AnonymizerEngine()


def anonymize_prompt(text: str) -> str:
    """Replace detected PII with <ENTITY_TYPE> placeholders."""
    results = _analyzer.analyze(text=text, language="en")
    if not results:
        return text
    return _anonymizer.anonymize(text=text, analyzer_results=results).text
