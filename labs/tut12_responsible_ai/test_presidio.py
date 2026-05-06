# test_presidio.py
from presidio_analyzer import AnalyzerEngine

analyzer = AnalyzerEngine()
text = "Contact john.doe@example.com or call +61 412 345 678 about the incident on 192.168.1.1"
results = analyzer.analyze(text=text, language="en")

for r in results:
    print(f"{r.entity_type:20s}  score={r.score:.2f}  '{text[r.start:r.end]}'")
