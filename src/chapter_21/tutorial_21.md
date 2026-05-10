## 21.12 Tutorial: Deploying MedChat with LiteLLM, Streaming, and Guardrails

MedChat has passed evaluation. Now you need to deploy it for the hospital — but three departments have different requirements: the radiology team needs fast streaming responses, the pharmacy team needs cost tracking per query, and IT security requires that no patient names or identifiers ever reach the external LLM API. Your job is to build a production deployment using LiteLLM as the LLM gateway, add streaming to a FastAPI backend and Streamlit frontend, implement PII guardrails with Microsoft Presidio, and containerise the full system with Docker Compose.

**Concepts covered:** LiteLLM proxy, model aliases, streaming responses, FastAPI StreamingResponse, cost tracking, input/output guardrails, PII detection, Docker Compose multi-service

**Format:** Individual or pairs | **Duration:** ~2.5 hours | **Tool:** Python · litellm · FastAPI · Streamlit · Docker · Docker Compose · presidio-analyzer · uvicorn

---

### Outline

- [Part A: LiteLLM Gateway and Streaming](#part-a-litellm-gateway-and-streaming--75-min)
- [Part B: Guardrails and Containerisation](#part-b-guardrails-and-containerisation--75-min)
- [References](#references)

---

### Learning Objectives

1. Replace direct OpenAI SDK calls with LiteLLM and explain why the drop-in replacement enables model portability.
2. Implement model cascading — route simple queries to a cheaper model and complex ones to a more capable model.
3. Build a streaming FastAPI endpoint and consume it from Streamlit using `st.write_stream`.
4. Detect and block PII in user input using Microsoft Presidio before it reaches the LLM API.
5. Validate LLM output against clinical safety rules using a regex-based output guard.
6. Write a multi-service Docker Compose stack with health checks, non-root containers, and environment injection.

---

### Prerequisites

You need the MedChat project from Tutorials 16–19.

```bash
pip install litellm fastapi uvicorn streamlit \
            presidio-analyzer presidio-anonymizer \
            python-dotenv pydantic
```

Verify:

```bash
python -c "import litellm, fastapi, streamlit; print('all imports OK')"
presidio-analyzer --help 2>/dev/null || python -c "from presidio_analyzer import AnalyzerEngine; print('presidio OK')"
```

Docker and Docker Compose are required for Part B.

---

### Part A: LiteLLM Gateway and Streaming *(~75 min)*

#### Step 1: Install LiteLLM

Add to `requirements.txt`:

```
litellm>=1.35.0
fastapi>=0.111.0
uvicorn[standard]>=0.29.0
streamlit>=1.35.0
presidio-analyzer>=2.2.354
presidio-anonymizer>=2.2.354
```

```bash
pip install litellm fastapi "uvicorn[standard]" streamlit
```

#### Step 2: Drop-in replacement for OpenAI

Create `litellm_demo.py` to demonstrate the migration:

```python
import os
from dotenv import load_dotenv

load_dotenv()

# ── BEFORE: direct OpenAI SDK ──────────────────────────────────────────────────
from openai import OpenAI

client   = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "What is amoxicillin used for?"}],
)
print("OpenAI SDK:", response.choices[0].message.content[:80])

# ── AFTER: LiteLLM drop-in ─────────────────────────────────────────────────────
import litellm

response = litellm.completion(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "What is amoxicillin used for?"}],
)
print("LiteLLM:   ", response.choices[0].message.content[:80])
```

Run it:

```bash
python litellm_demo.py
```

The outputs should be identical. LiteLLM uses the same `OPENAI_API_KEY` environment variable and returns an OpenAI-compatible response object.

> **Why LiteLLM?** When the hospital later decides to switch to a self-hosted model (for data sovereignty reasons), you change the model string — not the code. LiteLLM normalises 100+ LLM providers behind a single interface.

#### Step 3: Model switching with a single string change

Add this to `litellm_demo.py` to demonstrate provider switching:

```python
# Local model via Ollama (install ollama and pull llama3.2 first)
# response = litellm.completion(
#     model="ollama/llama3.2",
#     messages=[{"role": "user", "content": "What is amoxicillin used for?"}],
#     api_base="http://localhost:11434",
# )

# Azure OpenAI (uses AZURE_API_KEY, AZURE_API_BASE, AZURE_API_VERSION env vars)
# response = litellm.completion(
#     model="azure/gpt-4o-mini",
#     messages=[{"role": "user", "content": "What is amoxicillin used for?"}],
# )

# Anthropic Claude
# response = litellm.completion(
#     model="claude-3-haiku-20240307",
#     messages=[{"role": "user", "content": "What is amoxicillin used for?"}],
# )

print("Provider switching: just change the model string. No code changes needed.")
```

#### Step 4: Cost tracking and model cascading

Create `gateway.py` — the LiteLLM wrapper used by the rest of the application:

```python
"""
LiteLLM gateway for MedChat.
Handles model selection, cost tracking, and streaming.
"""

import os
import re
import mlflow
import litellm
from dotenv import load_dotenv

load_dotenv()

# ── Model configuration ────────────────────────────────────────────────────────

MODEL_DEFAULT = "gpt-4o-mini"    # fast and cheap — used for most queries
MODEL_COMPLEX = "gpt-4o"         # used for complex clinical calculations

# Trigger phrases that warrant the more capable model
COMPLEX_TRIGGERS = [
    r"drug interaction",
    r"dosage calculation",
    r"renal.{0,10}adjust",
    r"hepatic.{0,10}adjust",
    r"pharmacokinetics",
]

def select_model(question: str) -> str:
    """Choose the appropriate model based on question complexity."""
    q_lower = question.lower()
    for pattern in COMPLEX_TRIGGERS:
        if re.search(pattern, q_lower):
            return MODEL_COMPLEX
    return MODEL_DEFAULT

# ── LiteLLM completion with cost tracking ─────────────────────────────────────

def complete(messages: list[dict], stream: bool = False, mlflow_run_id: str = None):
    """
    Call LiteLLM with automatic model selection and cost logging.
    Returns the response object (or a generator if stream=True).
    """
    # Determine model from the last user message
    last_user_msg = next(
        (m["content"] for m in reversed(messages) if m["role"] == "user"),
        "",
    )
    model = select_model(last_user_msg)

    response = litellm.completion(
        model=model,
        messages=messages,
        temperature=0.1,
        max_tokens=500,
        stream=stream,
    )

    if not stream:
        # Log cost to MLflow
        cost = getattr(response, "_hidden_params", {}).get("response_cost", 0.0)
        if mlflow_run_id:
            with mlflow.start_run(run_id=mlflow_run_id):
                mlflow.log_metric("cost_usd", cost)
        print(f"  [model={model} cost=${cost:.6f}]")

    return response

if __name__ == "__main__":
    msgs = [
        {"role": "system", "content": "You are MedChat."},
        {"role": "user",   "content": "What is the first-line antibiotic for pneumonia?"},
    ]
    r = complete(msgs)
    print(r.choices[0].message.content)

    msgs2 = [
        {"role": "system", "content": "You are MedChat."},
        {"role": "user",   "content": "Explain the pharmacokinetics of vancomycin dosage calculation in renal impairment."},
    ]
    r2 = complete(msgs2)
    # Should print: model=gpt-4o
    print(r2.choices[0].message.content[:100])
```

Run the gateway demo:

```bash
python gateway.py
```

#### Step 5: Write the FastAPI backend with streaming

Create the `backend/` directory and `backend/main.py`:

```bash
mkdir -p backend frontend guardrails
touch backend/main.py frontend/app.py guardrails/__init__.py
touch guardrails/input_guard.py guardrails/output_guard.py
```

Write `backend/main.py`:

```python
"""
MedChat FastAPI backend with LiteLLM streaming.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import litellm

from guardrails.input_guard  import check_input
from guardrails.output_guard import check_output

load_dotenv()

app = FastAPI(title="MedChat API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Load system prompt ─────────────────────────────────────────────────────────

def load_system_prompt() -> dict:
    with open("prompts/system_v1.yaml") as f:
        return yaml.safe_load(f)

PROMPT_CONFIG  = load_system_prompt()
SYSTEM_CONTENT = PROMPT_CONFIG["system_prompt"].strip()

# ── Request / Response schemas ─────────────────────────────────────────────────

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[Message]
    model: str = "gpt-4o-mini"

class ChatResponse(BaseModel):
    content: str
    model: str
    blocked: bool = False
    block_reason: str = ""

# ── Non-streaming endpoint ─────────────────────────────────────────────────────

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    user_messages = [m.model_dump() for m in request.messages]
    last_user_content = next(
        (m["content"] for m in reversed(user_messages) if m["role"] == "user"),
        "",
    )

    # Input guard: PII check
    guard_result = check_input(last_user_content)
    if guard_result["blocked"]:
        return ChatResponse(
            content=guard_result["message"],
            model=request.model,
            blocked=True,
            block_reason=guard_result["reason"],
        )

    messages = [{"role": "system", "content": SYSTEM_CONTENT}] + user_messages

    response = litellm.completion(
        model=request.model,
        messages=messages,
        temperature=0.1,
        max_tokens=500,
    )

    answer = response.choices[0].message.content

    # Output guard: safety check
    output_result = check_output(answer)
    if output_result["blocked"]:
        return ChatResponse(
            content=output_result["message"],
            model=request.model,
            blocked=True,
            block_reason=output_result["reason"],
        )

    return ChatResponse(content=answer, model=request.model)

# ── Streaming endpoint ─────────────────────────────────────────────────────────

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    user_messages = [m.model_dump() for m in request.messages]
    last_user_content = next(
        (m["content"] for m in reversed(user_messages) if m["role"] == "user"),
        "",
    )

    # Input guard
    guard_result = check_input(last_user_content)
    if guard_result["blocked"]:
        async def blocked_gen():
            yield guard_result["message"]
        return StreamingResponse(blocked_gen(), media_type="text/plain")

    messages = [{"role": "system", "content": SYSTEM_CONTENT}] + user_messages

    async def generate():
        loop     = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: litellm.completion(
                model=request.model,
                messages=messages,
                temperature=0.1,
                max_tokens=500,
                stream=True,
            ),
        )
        for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    return StreamingResponse(generate(), media_type="text/plain")

# ── Health check ───────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
```

Start the backend:

```bash
uvicorn backend.main:app --reload --port 8000
```

Test in another terminal:

```bash
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "What is amoxicillin?"}]}' | python -m json.tool
```

#### Step 6: Write the Streamlit frontend with streaming

Write `frontend/app.py`:

```python
"""
MedChat Streamlit frontend with streaming support.
"""

import requests
import streamlit as st

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="MedChat", page_icon="🏥", layout="wide")
st.title("MedChat — Clinical Decision Support")
st.caption("Powered by LiteLLM | For junior doctor support only — always consult a senior clinician")

# ── Session state ──────────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Display history ────────────────────────────────────────────────────────────

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ── Chat input ─────────────────────────────────────────────────────────────────

if prompt := st.chat_input("Ask a clinical question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Stream the response
    with st.chat_message("assistant"):
        def stream_response():
            with requests.post(
                f"{API_BASE}/chat/stream",
                json={"messages": st.session_state.messages, "model": "gpt-4o-mini"},
                stream=True,
                timeout=60,
            ) as resp:
                resp.raise_for_status()
                for chunk in resp.iter_content(chunk_size=None, decode_unicode=True):
                    if chunk:
                        yield chunk

        try:
            full_response = st.write_stream(stream_response())
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to the MedChat backend. Is it running on port 8000?")
```

Run the frontend (requires the backend to be running):

```bash
streamlit run frontend/app.py
```

Navigate to <http://localhost:8501>. You should see streaming tokens appear word-by-word.

---

### Part B: Guardrails and Containerisation *(~75 min)*

#### Step 1: Install Presidio

```bash
pip install presidio-analyzer presidio-anonymizer
python -m spacy download en_core_web_lg
```

#### Step 2: Write `guardrails/input_guard.py`

```python
"""
Input guard: detects PII in user messages and blocks them before they reach the LLM API.
Uses Microsoft Presidio for NER-based PII detection.
"""

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

analyzer  = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# PII entity types we want to block in clinical context
BLOCKED_ENTITIES = [
    "PERSON",           # patient names
    "PHONE_NUMBER",     # contact numbers
    "EMAIL_ADDRESS",    # email addresses
    "UK_NHS",           # NHS numbers (UK-specific)
    "US_SSN",           # US social security numbers
    "MEDICAL_LICENSE",  # medical licence numbers
    "IP_ADDRESS",       # should not appear in clinical queries
]

def check_input(text: str) -> dict:
    """
    Analyse the input text for PII.
    Returns {"blocked": bool, "reason": str, "message": str, "entities": list}.
    """
    results = analyzer.analyze(
        text=text,
        language="en",
        entities=BLOCKED_ENTITIES,
        score_threshold=0.7,   # only flag high-confidence detections
    )

    if results:
        entity_types = list({r.entity_type for r in results})
        return {
            "blocked": True,
            "reason":  f"PII detected: {', '.join(entity_types)}",
            "message": (
                "Your message appears to contain patient-identifiable information "
                f"({', '.join(entity_types)}). Please remove all patient names, "
                "NHS numbers, phone numbers, and other identifiers before sending. "
                "MedChat must never receive real patient data."
            ),
            "entities": entity_types,
        }

    return {"blocked": False, "reason": "", "message": "", "entities": []}

def anonymize_text(text: str) -> str:
    """
    Replace PII with placeholder tokens (for logging/debugging only).
    Do NOT use this as a bypass for the guard — block is the correct action.
    """
    results = analyzer.analyze(text=text, language="en")
    anonymized = anonymizer.anonymize(text=text, analyzer_results=results)
    return anonymized.text

if __name__ == "__main__":
    test_cases = [
        "What dose of amoxicillin should I give?",
        "My patient John Smith (NHS 943 476 5919) needs a UTI treatment.",
        "The patient is allergic to penicillin. Phone 07700 900461 for follow-up.",
        "john.doe@hospital.nhs.uk has a drug interaction question.",
    ]
    for text in test_cases:
        result = check_input(text)
        status = "BLOCKED" if result["blocked"] else "ALLOWED"
        print(f"[{status}] {text[:60]}")
        if result["blocked"]:
            print(f"         Reason: {result['reason']}")
```

Test the input guard:

```bash
python guardrails/input_guard.py
```

Expected:
```
[ALLOWED] What dose of amoxicillin should I give?
[BLOCKED] My patient John Smith (NHS 943 476 5919) needs a UTI t...
         Reason: PII detected: PERSON, UK_NHS
[BLOCKED] The patient is allergic to penicillin. Phone 07700 900...
         Reason: PII detected: PHONE_NUMBER
[BLOCKED] john.doe@hospital.nhs.uk has a drug interaction questio...
         Reason: PII detected: EMAIL_ADDRESS
```

#### Step 3: Write `guardrails/output_guard.py`

```python
"""
Output guard: validates LLM responses against clinical safety rules.
Blocks responses that lack source citations or contain dangerous prescription language.
"""

import re

# ── Safety rules ───────────────────────────────────────────────────────────────

# Phrases that should NEVER appear in MedChat responses
DANGEROUS_PHRASES = [
    r"\bprescribe\b",                   # MedChat should not prescribe
    r"\bI recommend you take\b",        # Direct drug recommendation to patient
    r"\byou should take\b",             # Directing patient to take a drug
    r"\bguaranteed\b",                  # No clinical guarantees
    r"\bno side effects\b",             # All drugs have potential side effects
    r"\b100% safe\b",                   # Never absolutely safe
    r"\bno need to see a doctor\b",     # Should not replace clinical consultation
]

# The response should contain at least one of these source-attribution patterns
SOURCE_CITATION_PATTERNS = [
    r"\[Source\s*\d+",           # [Source 1: ...]
    r"\baccording to\b",
    r"\bguideline",
    r"\breference",
    r"\bprotocol",
    r"\bwho\b",                  # WHO guideline references
    r"\bnhs\b",                  # NHS reference
    r"\bbnf\b",                  # British National Formulary
    r"consult\s+a\s+senior",     # Acceptable clinical citation substitute
    r"cannot find this information",   # Explicit "not found" is acceptable
]

SAFE_FALLBACK_MESSAGE = (
    "I was unable to generate a safe response to your question. "
    "Please consult a senior clinician or refer to your local clinical guidelines."
)

def check_output(text: str) -> dict:
    """
    Validate the LLM output against clinical safety rules.
    Returns {"blocked": bool, "reason": str, "message": str}.
    """
    text_lower = text.lower()

    # Rule 1: Check for dangerous prescribing language
    for pattern in DANGEROUS_PHRASES:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return {
                "blocked": True,
                "reason":  f"Dangerous prescribing language detected: pattern '{pattern}'",
                "message": SAFE_FALLBACK_MESSAGE,
            }

    # Rule 2: Check for source citation (only for substantive answers)
    word_count = len(text.split())
    if word_count > 30:   # short replies (e.g., "I don't know") don't need citations
        has_citation = any(
            re.search(pat, text_lower, re.IGNORECASE)
            for pat in SOURCE_CITATION_PATTERNS
        )
        if not has_citation:
            return {
                "blocked": True,
                "reason":  "Response lacks source citation",
                "message": SAFE_FALLBACK_MESSAGE,
            }

    return {"blocked": False, "reason": "", "message": ""}

if __name__ == "__main__":
    test_outputs = [
        # PASS: cites guideline
        "According to WHO guidelines, amoxicillin 500 mg three times daily is recommended for CAP.",
        # FAIL: dangerous prescribing
        "I recommend you take amoxicillin 500 mg three times daily.",
        # FAIL: no citation
        "Amoxicillin 500 mg three times daily is used for pneumonia. The duration is 5 days.",
        # PASS: explicit not-found
        "I cannot find this information in my reference documents. Please consult a senior clinician.",
    ]
    for output in test_outputs:
        result = check_output(output)
        status = "BLOCKED" if result["blocked"] else "ALLOWED"
        print(f"[{status}] {output[:70]}")
        if result["blocked"]:
            print(f"         Reason: {result['reason']}")
```

Test the output guard:

```bash
python guardrails/output_guard.py
```

#### Step 4: Wire guardrails into the FastAPI backend

The guardrails are already integrated in `backend/main.py` (Steps 5 and 6 of Part A). Verify the middleware is working by sending a blocked request:

```bash
# Should be blocked by input guard (patient name)
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "My patient Jane Doe needs a UTI treatment plan"}]}' \
  | python -m json.tool
```

Expected response:
```json
{
  "content": "Your message appears to contain patient-identifiable information...",
  "model": "gpt-4o-mini",
  "blocked": true,
  "block_reason": "PII detected: PERSON"
}
```

#### Step 5: Write Dockerfiles

**`backend/Dockerfile`** (multi-stage, non-root user, health check):

```dockerfile
# ── Stage 1: Build ─────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Download spacy model
RUN /install/bin/python -m spacy download en_core_web_lg

# ── Stage 2: Runtime ───────────────────────────────────────────────────────────
FROM python:3.11-slim

# Non-root user for security
RUN addgroup --system medchat && adduser --system --ingroup medchat medchat

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY backend/   ./backend/
COPY guardrails/ ./guardrails/
COPY prompts/   ./prompts/
COPY retriever.py .
COPY gateway.py   .

# Change ownership to non-root user
RUN chown -R medchat:medchat /app
USER medchat

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**`frontend/Dockerfile`**:

```dockerfile
FROM python:3.11-slim

RUN addgroup --system medchat && adduser --system --ingroup medchat medchat

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir streamlit requests

COPY frontend/ ./frontend/

RUN chown -R medchat:medchat /app
USER medchat

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')"

CMD ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### Step 6: Write `docker-compose.yml`

```yaml
services:

  # ── PostgreSQL with pgvector ─────────────────────────────────────────────────
  pgvector:
    image: pgvector/pgvector:pg16
    container_name: medchat-pgvector
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-medchat}
      POSTGRES_DB: ${POSTGRES_DB:-medchat}
    ports:
      - "5432:5432"
    volumes:
      - pgvector_data:/var/lib/postgresql/data
      - ./db/schema.sql:/docker-entrypoint-initdb.d/schema.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d medchat"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s

  # ── FastAPI backend ──────────────────────────────────────────────────────────
  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    container_name: medchat-backend
    ports:
      - "8000:8000"
    environment:
      OPENAI_API_KEY:   ${OPENAI_API_KEY}
      DATABASE_URL:     postgresql://postgres:${POSTGRES_PASSWORD:-medchat}@pgvector:5432/${POSTGRES_DB:-medchat}
      MLFLOW_TRACKING_URI: ${MLFLOW_TRACKING_URI:-http://localhost:5000}
    depends_on:
      pgvector:
        condition: service_healthy
    restart: on-failure
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 20s

  # ── Streamlit frontend ───────────────────────────────────────────────────────
  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile
    container_name: medchat-frontend
    ports:
      - "8501:8501"
    environment:
      API_BASE: http://backend:8000
    depends_on:
      backend:
        condition: service_healthy
    restart: on-failure

volumes:
  pgvector_data:
```

> **Why environment injection, not hardcoded values?** The `OPENAI_API_KEY` must never appear in a Dockerfile or docker-compose.yml that gets committed to git. Docker Compose reads it from the host environment or a `.env` file at runtime. Run `docker compose config` to verify no secrets appear in the resolved configuration.

#### Step 7: Build and run the full system

Ensure your `.env` file has the required variables:

```
OPENAI_API_KEY=sk-...
POSTGRES_PASSWORD=medchat
POSTGRES_DB=medchat
```

Build and start all services:

```bash
docker compose up --build
```

Wait for all health checks to pass (watch for `medchat-backend  | Application startup complete`), then verify:

```bash
# Check all containers are healthy
docker compose ps

# Check backend health
curl http://localhost:8000/health

# Test a clinical question through the API
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "What is the first-line antibiotic for pneumonia?"}]}' \
  | python -m json.tool
```

Open Streamlit at <http://localhost:8501>.

#### Step 8: End-to-end guardrail test through the UI

In the Streamlit chat interface, send:

```
My patient Michael Johnson (DOB 15/04/1982, NHS 943 476 5919) has a penicillin allergy and a UTI. What antibiotic should I prescribe?
```

The input guard should block the message before it reaches the LLM API. The Streamlit UI will display the PII warning instead of an LLM response. The `OPENAI_API_KEY` is never used for this request.

To confirm, check the backend logs:

```bash
docker compose logs backend --tail=20
```

You should see the guard blocking the request with no outbound API call.

To verify cost logging, check the MLflow UI (if running):

```bash
mlflow ui &
```

Navigate to <http://localhost:5000> and inspect the `medchat-production` experiment. Every non-blocked request should have a `cost_usd` metric logged.

---

### References

1. LiteLLM documentation — <https://docs.litellm.ai>
2. FastAPI StreamingResponse — <https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse>
3. Microsoft Presidio (PII detection) — <https://microsoft.github.io/presidio/>
4. Docker Compose health checks — <https://docs.docker.com/compose/compose-file/05-services/#healthcheck>
5. Streamlit `st.write_stream` — <https://docs.streamlit.io/develop/api-reference/write-magic/st.write_stream>
