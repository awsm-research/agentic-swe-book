## 8.3 PII and Credential Detection

### 8.3.1 GitLeaks

GitLeaks ([Gitleaks, 2019](https://github.com/gitleaks/gitleaks)) is an open-source tool that scans git repositories for secrets — API keys, passwords, tokens, and other credentials — using a library of regular expression patterns.

```bash
# Install
brew install gitleaks   # macOS
# or: go install github.com/gitleaks/gitleaks/v8@latest

# Scan the current repository
gitleaks detect --source .

# Scan git history (catches secrets that were committed then deleted)
gitleaks detect --source . --log-opts="--all"
```

GitLeaks can be added to your CI/CD pipeline to prevent secrets from ever reaching the repository.

```yaml
# .github/workflows/security.yml (add to CI)
- name: Scan for secrets
  uses: gitleaks/gitleaks-action@v2
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 8.3.2 PII Detection

Personally Identifiable Information (PII) — names, email addresses, phone numbers, government IDs — must be handled with particular care under regulations like GDPR (EU) and the Privacy Act (Australia).

For Python applications, the Microsoft Presidio library ([Microsoft, 2019](https://github.com/microsoft/presidio)) provides PII detection and anonymisation:

```python
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
```

---
