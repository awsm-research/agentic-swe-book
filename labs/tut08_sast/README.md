# Tutorial 8 — SAST, AI, and Human on Vulnerability Detection

The lab file `ch08_vulnerable_app.py` is a deliberately vulnerable Flask app
used for the Phase 1–6 triage activity. The triage worksheet, AI prompt, and
answer key are in `tutorial_8.md`.

## Files

| File | Purpose |
|---|---|
| `ch08_vulnerable_app.py` | Flask app deliberately seeded with vulnerabilities for SAST review |

## How to run

```bash
python -m venv .venv && source .venv/bin/activate
pip install flask bandit semgrep

bandit -r ch08_vulnerable_app.py -ll -f json -o bandit_results.json
bandit -r ch08_vulnerable_app.py -ll

semgrep --config=auto ch08_vulnerable_app.py --json -o semgrep_results.json
semgrep --config=auto ch08_vulnerable_app.py
```

The AI prompt for Phase 3 is in `tutorial_8.md` Step 4. The full instructor
answer key with the 21-row triage table is at the end of the same file.
