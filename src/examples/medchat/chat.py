"""
MedChat — Chapter 16 conversation loop.

Loads a versioned system prompt from prompts/system_v1.yaml, maintains
conversation history with token budget management, and logs token count
and latency per turn.

Usage:
    export OPENAI_API_KEY="sk-..."
    python chat.py
"""

import os
import time
import yaml
import tiktoken
from openai import OpenAI

# ── Configuration ──────────────────────────────────────────────────────────────

PROMPT_FILE = os.path.join(os.path.dirname(__file__), "prompts", "system_v1.yaml")
MAX_HISTORY_TOKENS = 3000
ENCODING_NAME = "cl100k_base"

# ── Helpers ────────────────────────────────────────────────────────────────────


def load_config(path: str) -> dict:
    """Load system prompt config from a YAML file."""
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def count_tokens(text: str) -> int:
    """Count tokens in a string using tiktoken cl100k_base encoding."""
    enc = tiktoken.get_encoding(ENCODING_NAME)
    return len(enc.encode(text))


def count_history_tokens(history: list[dict]) -> int:
    """Count total tokens across all messages in the history list."""
    return sum(count_tokens(msg["content"]) for msg in history)


def trim_history(history: list[dict], max_tokens: int = MAX_HISTORY_TOKENS) -> list[dict]:
    """
    Trim conversation history so that total token count stays within budget.
    Drops the oldest messages first (sliding window).
    Warns when trimming is needed.
    """
    total = count_history_tokens(history)
    if total > max_tokens:
        print(
            f"\n[Warning] Conversation history is {total} tokens "
            f"(budget: {max_tokens}). Trimming oldest messages.\n"
        )
    trimmed = list(history)
    while count_history_tokens(trimmed) > max_tokens and len(trimmed) > 2:
        trimmed.pop(0)
    return trimmed


# ── Main conversation loop ─────────────────────────────────────────────────────


def run() -> None:
    """Interactive MedChat conversation loop (Chapter 16 prototype)."""
    config = load_config(PROMPT_FILE)

    model: str = config.get("model", "gpt-4o-mini")
    temperature: float = config.get("temperature", 0.1)
    max_tokens: int = config.get("max_tokens", 500)
    system_text: str = config.get("system_prompt", "").strip()
    version: str = config.get("version", "unknown")

    client = OpenAI()
    conversation_history: list[dict] = []

    print("=" * 60)
    print(f"MedChat v{version} — Clinical Q&A Assistant")
    print("For use by qualified healthcare professionals only.")
    print("Type 'quit' or 'exit' to end the session.")
    print("=" * 60)
    print()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nSession ended.")
            break

        if not user_input:
            continue

        if user_input.lower() in {"quit", "exit"}:
            print("Goodbye.")
            break

        # Build message list: system + trimmed history + new user message
        trimmed_history = trim_history(conversation_history)
        messages = [{"role": "system", "content": system_text}]
        messages.extend(trimmed_history)
        messages.append({"role": "user", "content": user_input})

        # --- LLM call with latency measurement ---
        t0 = time.perf_counter()
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        latency_ms = (time.perf_counter() - t0) * 1000

        answer: str = response.choices[0].message.content or ""
        finish_reason: str = response.choices[0].finish_reason or ""
        prompt_tokens: int = response.usage.prompt_tokens
        completion_tokens: int = response.usage.completion_tokens
        total_tokens: int = response.usage.total_tokens

        if finish_reason == "length":
            print("[Warning] Response was truncated (finish_reason=length).")

        # Append this turn to the conversation history
        conversation_history.append({"role": "user", "content": user_input})
        conversation_history.append({"role": "assistant", "content": answer})

        # Display answer and stats
        print(f"\nMedChat: {answer}")
        print(
            f"\n[{latency_ms:.0f} ms | "
            f"{total_tokens} tokens "
            f"(in={prompt_tokens}, out={completion_tokens})]"
        )

        # Warn when history is approaching the budget
        history_tok = count_history_tokens(conversation_history)
        if history_tok > MAX_HISTORY_TOKENS:
            print(
                f"[Warning] History is {history_tok} tokens "
                f"(budget: {MAX_HISTORY_TOKENS}). Oldest turns will be dropped next turn."
            )

        print()


if __name__ == "__main__":
    run()
