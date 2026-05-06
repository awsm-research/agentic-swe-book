# Chapter 8 — Common Python Security Vulnerabilities

Vulnerable + safe pairs for each Python vulnerability class covered in
Chapter 8 §8.2–8.4.

## Files

| File | CWE | Topic |
|---|---|---|
| `sql_injection.py` | CWE-89 | f-string SQL vs parameterised query |
| `command_injection.py` | CWE-78 | `shell=True` with user input vs argument list |
| `path_traversal.py` | CWE-22 | Direct path concatenation vs resolved-path check |
| `insecure_deserialization.py` | CWE-502 | `pickle.loads` on untrusted data vs JSON |
| `hardcoded_credentials.py` | CWE-798 | Hardcoded password vs env-var lookup |
| `ai_generated_vuln.py` | CWE-89, CWE-94 | The two AI-generated patterns from §8.4 |
| `pii_detection.py` | — | Presidio-based PII detection and anonymisation |

## How to run

```bash
pip install presidio-analyzer presidio-anonymizer flask
python pii_detection.py
```

The other files reference symbols intentionally undefined (`db`, `app`) — they
are meant for reading and SAST analysis, not direct execution.
