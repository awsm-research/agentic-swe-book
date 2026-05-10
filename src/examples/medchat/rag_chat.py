"""
MedChat RAG conversation loop — Chapter 17.

Extends chat.py with a full Retrieval-Augmented Generation pipeline:
  1. Embed the user's question.
  2. Retrieve the top-k most similar chunks from pgvector.
  3. Rerank with a cross-encoder.
  4. Inject the retrieved context into the system prompt.
  5. Generate a grounded, source-attributed answer.
  6. Print retrieved sources alongside the answer.

Usage:
    export DATABASE_URL="postgresql://user:pass@localhost/medchat"
    export OPENAI_API_KEY="sk-..."
    python rag_chat.py
"""

import os
import time
import yaml
from pathlib import Path

from openai import OpenAI

from retriever import retrieve, rerank

# ── Configuration ──────────────────────────────────────────────────────────────

PROMPT_FILE = Path(__file__).parent / "prompts" / "system_v1.yaml"
MODEL = "gpt-4o-mini"
TEMPERATURE = 0.1
MAX_TOKENS = 500
MAX_HISTORY_TURNS = 6          # keep last 3 user+assistant pairs
TOP_K_RETRIEVE = 10
TOP_N_RERANK = 3

RAG_CONTEXT_HEADER = (
    "Answer only from the provided context below. "
    "If the context does not contain the answer, say: "
    "'I don't have information about that in my clinical references.'\n\n"
    "## Retrieved Clinical Context\n"
)


# ── Helpers ────────────────────────────────────────────────────────────────────


def load_system_prompt(path: Path) -> tuple[str, str]:
    """Load system prompt YAML. Returns (prompt_text, version)."""
    with open(path, "r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    return cfg.get("system_prompt", "").strip(), cfg.get("version", "unknown")


def format_context(chunks: list[dict]) -> str:
    """Format reranked chunks into an annotated context string."""
    if not chunks:
        return ""
    parts: list[str] = []
    for i, ch in enumerate(chunks, start=1):
        title = ch.get("title", "Unknown Document")
        parts.append(f"[Source: {title}]\n{ch['content']}")
    return "\n\n".join(parts)


def trim_history(history: list[dict]) -> list[dict]:
    """Keep only the most recent MAX_HISTORY_TURNS messages."""
    return history[-MAX_HISTORY_TURNS:]


# ── RAG query ──────────────────────────────────────────────────────────────────


def rag_query(
    question: str,
    conversation_history: list[dict],
    client: OpenAI,
    base_system_prompt: str,
) -> tuple[str, list[dict], dict]:
    """
    Run the full RAG pipeline for a single user question.

    Returns:
        (answer, reranked_chunks, metadata)
    """
    # 1. Retrieve and rerank
    candidates = retrieve(question, top_k=TOP_K_RETRIEVE)
    top_chunks = rerank(question, candidates, top_n=TOP_N_RERANK)

    # 2. Build system prompt with injected context
    context_text = format_context(top_chunks)
    if context_text:
        system_content = (
            base_system_prompt
            + "\n\n"
            + RAG_CONTEXT_HEADER
            + context_text
        )
    else:
        system_content = (
            base_system_prompt
            + "\n\nNo relevant context was retrieved. "
            + "State explicitly that the answer is based on general knowledge and "
            + "recommend verifying with authoritative sources."
        )

    # 3. Build message list
    messages = [{"role": "system", "content": system_content}]
    messages.extend(trim_history(conversation_history))
    messages.append({"role": "user", "content": question})

    # 4. Call the LLM
    t0 = time.perf_counter()
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )
    latency_ms = (time.perf_counter() - t0) * 1000

    answer: str = response.choices[0].message.content or ""
    finish_reason: str = response.choices[0].finish_reason or ""

    metadata = {
        "model": MODEL,
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
        "latency_ms": round(latency_ms, 1),
        "finish_reason": finish_reason,
        "chunks_retrieved": len(candidates),
        "chunks_in_context": len(top_chunks),
    }

    return answer, top_chunks, metadata


# ── Conversation loop ──────────────────────────────────────────────────────────


def run() -> None:
    """Interactive MedChat RAG conversation loop."""
    base_prompt, version = load_system_prompt(PROMPT_FILE)
    client = OpenAI()
    history: list[dict] = []

    print("=" * 60)
    print(f"MedChat RAG v{version} — Clinical Q&A (with retrieval)")
    print("For use by qualified healthcare professionals only.")
    print("Type 'quit' or 'exit' to end the session.")
    print("=" * 60)
    print()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSession ended.")
            break

        if not user_input:
            continue
        if user_input.lower() in {"quit", "exit"}:
            print("Goodbye.")
            break

        answer, sources, meta = rag_query(
            question=user_input,
            conversation_history=history,
            client=client,
            base_system_prompt=base_prompt,
        )

        # Append turn to history
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": answer})

        print(f"\nMedChat: {answer}\n")

        if sources:
            print("Sources used:")
            for ch in sources:
                title = ch.get("title", "Unknown")
                score = ch.get("reranker_score", 0.0)
                sim = ch.get("similarity", 0.0)
                print(f"  • {title}  (reranker={score:.3f}, similarity={sim:.3f})")
        else:
            print("Sources: none retrieved")

        print(
            f"\n[{meta['latency_ms']:.0f} ms | "
            f"{meta['total_tokens']} tokens | "
            f"{meta['chunks_in_context']}/{meta['chunks_retrieved']} chunks used]"
        )
        print()


if __name__ == "__main__":
    run()
