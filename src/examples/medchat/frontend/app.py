"""
MedChat Streamlit frontend — Chapter 20.

Provides a streaming chat interface that:
  - Connects to the FastAPI backend at BACKEND_URL (env var)
  - Displays tokens progressively as they stream from the server
  - Shows source documents used for each response
  - Maintains full conversation history in session state

Usage:
    export BACKEND_URL="http://localhost:8000"
    streamlit run frontend/app.py
"""

from __future__ import annotations

import os
import json
import uuid

import requests
import streamlit as st

BACKEND_URL: str = os.environ.get("BACKEND_URL", "http://localhost:8000")

# ── Page config ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="MedChat Clinical Q&A",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title("MedChat Clinical Q&A")
st.caption("For use by qualified healthcare professionals only.")

# ── Session state initialisation ───────────────────────────────────────────────

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history: list[dict] = []

if "session_id" not in st.session_state:
    st.session_state.session_id: str = str(uuid.uuid4())

if "sources_by_turn" not in st.session_state:
    st.session_state.sources_by_turn: list[list[dict]] = []

# ── Display existing conversation ──────────────────────────────────────────────

for i, message in enumerate(st.session_state.conversation_history):
    with st.chat_message(message["role"]):
        st.write(message["content"])

        # Show sources for assistant turns
        if (
            message["role"] == "assistant"
            and i // 2 < len(st.session_state.sources_by_turn)
        ):
            sources = st.session_state.sources_by_turn[i // 2]
            if sources:
                with st.expander("Retrieved sources"):
                    for src in sources:
                        doc = src.get("document", "Unknown")
                        section = src.get("section") or "—"
                        score = src.get("score", 0.0)
                        st.write(f"**{doc}** — {section} (relevance: {score:.2f})")

# ── Chat input ─────────────────────────────────────────────────────────────────

if question := st.chat_input("Ask a clinical question…"):
    # Show the user's message immediately
    with st.chat_message("user"):
        st.write(question)

    st.session_state.conversation_history.append(
        {"role": "user", "content": question}
    )

    # Stream the response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        sources_placeholder = st.empty()

        accumulated: list[str] = []
        turn_sources: list[dict] = []

        payload = {
            "question": question,
            "conversation_history": st.session_state.conversation_history[:-1],
            "session_id": st.session_state.session_id,
        }

        try:
            with requests.post(
                f"{BACKEND_URL}/chat/stream",
                json=payload,
                stream=True,
                timeout=60,
            ) as resp:
                if resp.status_code != 200:
                    st.error(
                        f"Backend error {resp.status_code}: "
                        f"{resp.text[:200]}"
                    )
                else:
                    for raw_line in resp.iter_lines():
                        if not raw_line:
                            continue
                        line = (
                            raw_line.decode("utf-8")
                            if isinstance(raw_line, bytes)
                            else raw_line
                        )
                        if not line.startswith("data: "):
                            continue

                        try:
                            data = json.loads(line[6:])
                        except json.JSONDecodeError:
                            continue

                        if "error" in data:
                            response_placeholder.error(data["error"])
                            break

                        if token := data.get("token"):
                            accumulated.append(token)
                            response_placeholder.write("".join(accumulated))

                        if data.get("done"):
                            turn_sources = data.get("sources", [])
                            break

        except requests.exceptions.Timeout:
            response_placeholder.error(
                "Request timed out. Please try again or simplify your question."
            )
        except requests.exceptions.ConnectionError:
            response_placeholder.error(
                f"Could not connect to the backend at {BACKEND_URL}. "
                "Please check that the backend service is running."
            )
        except Exception as exc:
            response_placeholder.error(f"Unexpected error: {exc}")

        final_answer = "".join(accumulated)

        if turn_sources:
            with sources_placeholder.expander("Retrieved sources"):
                for src in turn_sources:
                    doc = src.get("document", "Unknown")
                    section = src.get("section") or "—"
                    score = src.get("score", 0.0)
                    st.write(f"**{doc}** — {section} (relevance: {score:.2f})")

    # Persist the turn in session state
    if final_answer:
        st.session_state.conversation_history.append(
            {"role": "assistant", "content": final_answer}
        )
        st.session_state.sources_by_turn.append(turn_sources)
