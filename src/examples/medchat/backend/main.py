"""
MedChat FastAPI backend — Chapter 20.

Endpoints:
    POST /chat          — standard (non-streaming) response
    POST /chat/stream   — StreamingResponse using LiteLLM stream=True

Features:
    - LiteLLM for LLM calls (not openai directly)
    - System prompt loaded from prompts/system_v1.yaml
    - Input guardrails applied before LLM call
    - Output guardrails applied after LLM call
    - Cost logged to MLflow via response._hidden_params["response_cost"]
    - Model cascade: gpt-4o-mini default, gpt-4o for complex/safety-critical queries

Usage:
    export OPENAI_API_KEY="sk-..."
    export DATABASE_URL="postgresql://user:pass@localhost/medchat"
    export MLFLOW_TRACKING_URI="http://localhost:5000"
    uvicorn backend.main:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import os
import re
import sys
import json
import logging
import asyncio
from pathlib import Path
from typing import AsyncGenerator

import yaml
import litellm
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Allow importing guardrails from the parent medchat directory
sys.path.insert(0, str(Path(__file__).parent.parent))

from guardrails.input_guard import check_input
from guardrails.output_guard import check_output

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("medchat.backend")

# ── MLflow (optional — non-fatal if unavailable) ───────────────────────────────
try:
    import mlflow

    mlflow.set_tracking_uri(
        os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000")
    )
    _MLFLOW_AVAILABLE = True
except Exception:
    _MLFLOW_AVAILABLE = False
    logger.warning("MLflow not available — cost logging disabled.")

# ── Configuration ──────────────────────────────────────────────────────────────

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
PROMPT_FILE = PROMPTS_DIR / "system_v1.yaml"

DEFAULT_MODEL = os.environ.get("MEDCHAT_MODEL", "gpt-4o-mini")
ESCALATION_MODEL = "gpt-4o"
TEMPERATURE = 0.1
MAX_TOKENS = 500

# Safety-critical keywords that trigger model escalation
_ESCALATION_PATTERNS = [
    re.compile(r"\boverdose\b", re.IGNORECASE),
    re.compile(r"\bcontraindicated?\b", re.IGNORECASE),
    re.compile(r"\bpregnant\b", re.IGNORECASE),
    re.compile(r"\bneonatal?\b", re.IGNORECASE),
    re.compile(r"\brenal\s+failure\b", re.IGNORECASE),
    re.compile(r"\bcritically\s+ill\b", re.IGNORECASE),
    re.compile(r"\bICU\b"),
    re.compile(r"\btoxic(?:ity)?\b", re.IGNORECASE),
]


# ── Helpers ────────────────────────────────────────────────────────────────────


def _load_system_prompt() -> str:
    with open(PROMPT_FILE, "r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    return cfg.get("system_prompt", "").strip()


def _pick_model(question: str) -> str:
    """Return ESCALATION_MODEL for complex/safety-critical queries, else DEFAULT_MODEL."""
    for pattern in _ESCALATION_PATTERNS:
        if pattern.search(question):
            logger.info(f"Model escalated to {ESCALATION_MODEL} — safety-critical query.")
            return ESCALATION_MODEL
    return DEFAULT_MODEL


def _log_cost(model: str, cost: float, session_id: str) -> None:
    """Log per-request cost to MLflow (non-fatal)."""
    if not _MLFLOW_AVAILABLE:
        return
    try:
        with mlflow.start_run(
            run_name=f"query-cost-{session_id}", nested=True
        ):
            mlflow.log_params({"model": model, "session_id": session_id})
            mlflow.log_metric("cost_usd", cost)
    except Exception as exc:
        logger.debug(f"MLflow cost logging failed: {exc}")


# ── App & shared state ─────────────────────────────────────────────────────────

app = FastAPI(title="MedChat API", version="1.0.0")

_SYSTEM_PROMPT: str = ""


@app.on_event("startup")
async def _startup() -> None:
    global _SYSTEM_PROMPT
    _SYSTEM_PROMPT = _load_system_prompt()
    logger.info("System prompt loaded.")


# ── Request / Response models ──────────────────────────────────────────────────


class ChatRequest(BaseModel):
    question: str
    conversation_history: list[dict] = []
    session_id: str = "default"


class ChatResponse(BaseModel):
    answer: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float


# ── Input guard helper ─────────────────────────────────────────────────────────


def _apply_input_guard(question: str) -> None:
    """Raise HTTPException 400 if the input is unsafe."""
    result = check_input(question)
    if not result.safe:
        raise HTTPException(status_code=400, detail=result.reason)


# ── Standard (non-streaming) endpoint ─────────────────────────────────────────


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    """Non-streaming clinical Q&A endpoint."""
    _apply_input_guard(req.question)

    model = _pick_model(req.question)
    messages = [{"role": "system", "content": _SYSTEM_PROMPT}]
    messages.extend(req.conversation_history[-6:])
    messages.append({"role": "user", "content": req.question})

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: litellm.completion(
            model=model,
            messages=messages,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        ),
    )

    answer: str = response.choices[0].message.content or ""

    # Extract cost from LiteLLM hidden params
    cost: float = 0.0
    try:
        cost = response._hidden_params.get("response_cost", 0.0) or 0.0
    except Exception:
        pass

    _log_cost(model, cost, req.session_id)

    # Output guardrail
    guard = check_output(answer, retrieved_sources=[])
    if not guard.safe:
        raise HTTPException(status_code=500, detail=guard.reason)

    return ChatResponse(
        answer=answer,
        model=model,
        prompt_tokens=response.usage.prompt_tokens,
        completion_tokens=response.usage.completion_tokens,
        cost_usd=cost,
    )


# ── Streaming endpoint ─────────────────────────────────────────────────────────


@app.post("/chat/stream")
async def chat_stream(req: ChatRequest) -> StreamingResponse:
    """Streaming clinical Q&A endpoint using LiteLLM stream=True."""
    _apply_input_guard(req.question)

    model = _pick_model(req.question)
    messages = [{"role": "system", "content": _SYSTEM_PROMPT}]
    messages.extend(req.conversation_history[-6:])
    messages.append({"role": "user", "content": req.question})

    async def _token_generator() -> AsyncGenerator[str, None]:
        full_response: list[str] = []
        try:
            loop = asyncio.get_event_loop()
            stream = await loop.run_in_executor(
                None,
                lambda: litellm.completion(
                    model=model,
                    messages=messages,
                    temperature=TEMPERATURE,
                    max_tokens=MAX_TOKENS,
                    stream=True,
                ),
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    full_response.append(delta)
                    yield f"data: {json.dumps({'token': delta})}\n\n"

            complete = "".join(full_response)
            guard = check_output(complete, retrieved_sources=[])
            if not guard.safe:
                yield f"data: {json.dumps({'error': guard.reason})}\n\n"
            else:
                # Log cost from the final chunk's hidden params if available
                cost: float = 0.0
                try:
                    cost = chunk._hidden_params.get("response_cost", 0.0) or 0.0
                    _log_cost(model, cost, req.session_id)
                except Exception:
                    pass
                yield f"data: {json.dumps({'done': True, 'cost_usd': cost})}\n\n"

        except Exception as exc:
            logger.error(f"Streaming error: {exc}")
            yield f"data: {json.dumps({'error': 'An error occurred. Please try again.'})}\n\n"

    return StreamingResponse(
        _token_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ── Health check ───────────────────────────────────────────────────────────────


@app.get("/health")
async def health() -> dict:
    return {"status": "healthy", "service": "medchat-backend"}
