"""
MedChat prompt regression test suite — Chapter 18.

Loads test cases from tests/fixtures/prompt_tests.yaml and runs each against
the MedChat RAG pipeline (using mock context from the fixture).

Run:
    pytest tests/test_prompts.py -v
    pytest tests/test_prompts.py -v -k "drug_dosing"   # filter by category

Tests are skipped automatically when OPENAI_API_KEY is not set.
"""

import os
import sys
import pytest
import yaml
from pathlib import Path

# Allow importing rag_chat from the parent medchat directory
sys.path.insert(0, str(Path(__file__).parent.parent))

from openai import OpenAI  # noqa: E402

# ── Constants ──────────────────────────────────────────────────────────────────

FIXTURES_PATH = Path(__file__).parent / "fixtures" / "prompt_tests.yaml"
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
PROMPT_FILE = PROMPTS_DIR / "system_v1.yaml"
MODEL = "gpt-4o-mini"
TEMPERATURE = 0.1
MAX_TOKENS = 500


# ── Load fixture data ──────────────────────────────────────────────────────────


def _load_test_cases() -> list[dict]:
    with open(FIXTURES_PATH, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data.get("tests", [])


def _load_system_prompt() -> str:
    with open(PROMPT_FILE, "r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    return cfg.get("system_prompt", "").strip()


_TEST_CASES = _load_test_cases()
_TEST_IDS = [tc["id"] for tc in _TEST_CASES]


# ── Fixtures ───────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def openai_client():
    """Shared OpenAI client; skip the entire session if no API key is set."""
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        pytest.skip("OPENAI_API_KEY is not set — skipping all LLM prompt tests.")
    return OpenAI(api_key=api_key)


@pytest.fixture(scope="session")
def base_system_prompt() -> str:
    return _load_system_prompt()


# ── Helper: build message list with injected context ──────────────────────────


def _build_messages(
    system_prompt: str,
    context: str,
    question: str,
) -> list[dict]:
    """Construct the message list for one test case."""
    rag_addition = ""
    if context.strip():
        rag_addition = (
            "\n\nAnswer only from the provided context. "
            "If the context does not contain the answer, say: "
            "'I don't have information about that in my clinical references.'\n\n"
            "## Retrieved Clinical Context\n"
            + context.strip()
        )
    system_content = system_prompt + rag_addition
    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": question},
    ]


# ── Assertion helper ───────────────────────────────────────────────────────────


def _check_response(response_text: str, test_case: dict) -> list[str]:
    """
    Validate response_text against must_contain, must_not_contain, and max_words.

    Returns a list of failure messages (empty list = all assertions passed).
    """
    failures: list[str] = []
    text_lower = response_text.lower()

    for phrase in test_case.get("must_contain", []):
        if phrase.lower() not in text_lower:
            failures.append(f"must_contain '{phrase}' — not found in response.")

    for phrase in test_case.get("must_not_contain", []):
        if phrase and phrase.lower() in text_lower:
            failures.append(f"must_not_contain '{phrase}' — found in response.")

    max_words = test_case.get("max_words")
    if max_words is not None:
        word_count = len(response_text.split())
        if word_count > max_words:
            failures.append(
                f"max_words exceeded: response has {word_count} words "
                f"(limit: {max_words})."
            )

    return failures


# ── Parametrised test ──────────────────────────────────────────────────────────


@pytest.mark.parametrize("test_case", _TEST_CASES, ids=_TEST_IDS)
def test_prompt_regression(
    test_case: dict,
    openai_client: OpenAI,
    base_system_prompt: str,
) -> None:
    """
    For each test case in the YAML fixture:
      1. Build a message list with the provided mock context.
      2. Query the MedChat prompt via the OpenAI API.
      3. Assert must_contain, must_not_contain, and max_words constraints.
    """
    question: str = test_case["question"]
    context: str = test_case.get("context", "")
    test_id: str = test_case["id"]

    messages = _build_messages(base_system_prompt, context, question)

    response = openai_client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )

    answer = response.choices[0].message.content or ""
    assert answer, f"[{test_id}] Model returned an empty response."

    failures = _check_response(answer, test_case)

    if failures:
        failure_detail = "\n  ".join(failures)
        snippet = answer[:300].replace("\n", " ")
        pytest.fail(
            f"[{test_id}] {len(failures)} assertion(s) failed:\n"
            f"  {failure_detail}\n\n"
            f"Response snippet:\n  {snippet}"
        )
