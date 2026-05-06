# Tutorial 9 — SAST in CI/CD

The full SAST pipeline scaffolding from Tutorial 9 Parts A–E.

## Files

| File | Source |
|---|---|
| `example_vulnerable.py` | Part A target file with five deliberate vulnerabilities |
| `security_review.py` | Part B aggregated SAST runner script |
| `rules/unsafe-path.yml` | Part C custom Semgrep rule for path traversal |
| `test_path.py` | Part C triggering example for the custom rule |
| `.github/workflows/security.yml` | Part D + E GitHub Actions pipeline |
| `.gitlab-ci.yml` | Part D + E GitLab CI configuration |
| `requirements.txt` | Part E known-vulnerable pin (`requests==2.18.0`) |

## How to run

```bash
uv add --dev bandit semgrep pip-audit

bandit example_vulnerable.py -l -ii
semgrep --config p/python --config p/owasp-top-ten example_vulnerable.py
python security_review.py example_vulnerable.py

semgrep --config rules/unsafe-path.yml test_path.py

pip-audit -r requirements.txt
```
