## 17.11 Tutorial: Building Your First LLM Application — MedChat Skeleton

A hospital's clinical informatics team wants a chatbot that answers questions from junior doctors about drug dosages, contraindications, and treatment protocols. You have been asked to build a working prototype in one session. Your job is to build the MedChat skeleton: a structured system prompt loaded from a versioned YAML file, a conversation loop with the OpenAI API, and logging of every interaction's token count and latency. By the end of this tutorial you will have a terminal-based clinical assistant that is already production-ready in its foundations — versioned prompts, observable outputs, and a context-window budget enforced in code.

**Concepts covered:** OpenAI Chat Completions API, message roles, system/user/assistant decomposition, prompt-as-code (YAML), token counting, latency measurement, conversation history management, context window budget

**Format:** Individual or pairs | **Duration:** ~2 hours | **Tool:** Python · openai · PyYAML · tiktoken · python-dotenv

---

### Outline

- [Part A: First Contact with the OpenAI API](#part-a-first-contact-with-the-openai-api--60-min)
- [Part B: MedChat with Versioned Prompts](#part-b-medchat-with-versioned-prompts--60-min)
- [References](#references)

---

### Learning Objectives

1. Construct a valid Chat Completions request and interpret every field in the response object.
2. Measure and log token usage and latency for every LLM call.
3. Store system prompts as versioned YAML files and load them at runtime.
4. Maintain a multi-turn conversation history while enforcing a context-window token budget.
5. Explain why low temperature is appropriate for medical decision-support applications.
6. Demonstrate a prompt upgrade workflow by diffing two YAML versions and observing behavioural change.

---

### Prerequisites

Install the required tools before starting.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install openai PyYAML tiktoken python-dotenv
```

Verify:

```bash
python -c "import openai, yaml, tiktoken, dotenv; print('all imports OK')"
```

You need an OpenAI API key. Sign in at <https://platform.openai.com>, navigate to **API Keys**, and create a new secret key.

---

### Part A: First Contact with the OpenAI API *(~60 min)*

#### Step 1: Create `.env` and install dependencies

Create a project directory and store your key:

```bash
mkdir medchat && cd medchat
touch .env
```

Add to `.env` (never commit this file):

```
OPENAI_API_KEY=sk-...your-key-here...
```

Create `requirements.txt`:

```
openai>=1.30.0
PyYAML>=6.0
tiktoken>=0.7.0
python-dotenv>=1.0.0
```

Install:

```bash
pip install -r requirements.txt
```

#### Step 2: The simplest possible completion

Create `hello_llm.py`:

```python
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "What is the first-line antibiotic for community-acquired pneumonia?"}
    ],
)

print(response.choices[0].message.content)
```

Run it:

```bash
python hello_llm.py
```

You should see a short clinical answer. If you get an `AuthenticationError`, double-check your `.env` file and confirm `load_dotenv()` is called before `OpenAI()`.

#### Step 3: Inspect the full response object

Update `hello_llm.py` to print the usage fields:

```python
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "What is the first-line antibiotic for community-acquired pneumonia?"}
    ],
)

# The answer
print("=== ANSWER ===")
print(response.choices[0].message.content)

# Token accounting
usage = response.usage
print("\n=== TOKEN USAGE ===")
print(f"  Prompt tokens:     {usage.prompt_tokens}")
print(f"  Completion tokens: {usage.completion_tokens}")
print(f"  Total tokens:      {usage.total_tokens}")

# Finish reason tells you WHY the model stopped
print(f"\nFinish reason: {response.choices[0].finish_reason}")
# 'stop' = natural end | 'length' = hit max_tokens | 'content_filter' = blocked
```

> **Why inspect finish_reason?** In production, a `finish_reason` of `length` means the answer was truncated. For a clinical assistant, a truncated drug dosage answer could be dangerous. You will use this signal later to warn users.

#### Step 4: Calculate cost

Add this block after printing token usage:

```python
# gpt-4o-mini pricing (as of mid-2024):
#   Input:  $0.150 per 1M tokens
#   Output: $0.600 per 1M tokens
PRICE_INPUT_PER_1M  = 0.150
PRICE_OUTPUT_PER_1M = 0.600

input_cost  = (usage.prompt_tokens     / 1_000_000) * PRICE_INPUT_PER_1M
output_cost = (usage.completion_tokens / 1_000_000) * PRICE_OUTPUT_PER_1M
total_cost  = input_cost + output_cost

print(f"\n=== COST ===")
print(f"  Input cost:  ${input_cost:.6f}")
print(f"  Output cost: ${output_cost:.6f}")
print(f"  Total cost:  ${total_cost:.6f}")
```

Run and observe. A single short exchange costs a fraction of a cent. At scale (1 000 queries/day) this compounds quickly — which is why token counting is a first-class concern from day one.

#### Step 5: Experiment with temperature

Create `temperature_test.py`:

```python
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

QUESTION = "What is the adult dose of amoxicillin for a urinary tract infection?"

for temp in [0.0, 1.0]:
    print(f"\n{'='*60}")
    print(f"Temperature: {temp}")
    print("="*60)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": QUESTION}],
        temperature=temp,
    )
    print(response.choices[0].message.content)
```

Run it twice and compare the outputs at each temperature:

```bash
python temperature_test.py
python temperature_test.py
```

At `temperature=0.0` the model is nearly deterministic — the same question yields the same answer. At `temperature=1.0` the phrasing varies between runs.

> **Why low temperature for medical applications?** Clinical decision support requires reproducibility and accuracy. A doctor asking the same question on Monday and Friday should receive the same answer. Creative variation in drug dosages is a patient-safety risk, not a feature.

---

### Part B: MedChat with Versioned Prompts *(~60 min)*

#### Step 1: Create the project structure

Inside the `medchat/` directory you already created:

```bash
mkdir -p prompts
touch prompts/system_v1.yaml
touch chat.py
```

Final layout:

```
medchat/
├── prompts/
│   ├── system_v1.yaml
│   └── system_v2.yaml      # created in Step 5
├── chat.py
├── hello_llm.py
├── temperature_test.py
├── .env
└── requirements.txt
```

#### Step 2: Write `prompts/system_v1.yaml`

```yaml
version: "1.0"
description: "MedChat clinical Q&A assistant — initial version"
model: "gpt-4o-mini"
temperature: 0.1
max_tokens: 500
system_prompt: |
  You are MedChat, a clinical decision support assistant for junior doctors.
  You answer questions about drug dosages, contraindications, and treatment protocols
  based only on the information provided to you.
  If you are uncertain, say so clearly. Never invent drug names, dosages, or protocols.
  Always recommend consulting a senior clinician for patient-specific decisions.
  Format your responses clearly with headers when listing multiple items.
  Always cite the source of your information when possible.
```

> **Why YAML for prompts?** Storing prompts as code-controlled files means every prompt change is a git commit with a diff, author, and message. When the clinical director asks "what changed last Tuesday?", you can answer with `git log --oneline prompts/`.

#### Step 3: Write `chat.py` — the full conversation loop

```python
import os
import time
import yaml
import tiktoken
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ── Configuration ─────────────────────────────────────────────────────────────

PROMPT_FILE = "prompts/system_v1.yaml"
CONTEXT_BUDGET_TOKENS = 3_000   # warn and trim when history exceeds this

def load_prompt_config(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)

# ── Token counting ─────────────────────────────────────────────────────────────

def count_tokens(messages: list[dict], model: str) -> int:
    """Count tokens for a list of chat messages using tiktoken."""
    try:
        enc = tiktoken.encoding_for_model(model)
    except KeyError:
        enc = tiktoken.get_encoding("cl100k_base")

    total = 0
    for msg in messages:
        # 4 tokens overhead per message (role + separators)
        total += 4
        for value in msg.values():
            total += len(enc.encode(str(value)))
    total += 2  # reply primer
    return total

# ── Context budget management ──────────────────────────────────────────────────

def trim_history(history: list[dict], system_msg: dict, model: str, budget: int) -> list[dict]:
    """
    Remove oldest user/assistant pairs until the total token count is under budget.
    The system message is always kept.
    """
    while True:
        all_messages = [system_msg] + history
        if count_tokens(all_messages, model) <= budget:
            break
        if len(history) < 2:
            # Cannot trim further — a single turn exceeds budget
            break
        # Drop the oldest user + assistant pair
        history = history[2:]
        print("  [context trimmed: removed oldest message pair to stay within budget]")
    return history

# ── Main chat loop ─────────────────────────────────────────────────────────────

def main():
    config = load_prompt_config(PROMPT_FILE)

    model       = config["model"]
    temperature = config["temperature"]
    max_tokens  = config["max_tokens"]
    system_text = config["system_prompt"].strip()

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    system_msg = {"role": "system", "content": system_text}
    history: list[dict] = []

    print(f"MedChat v{config['version']} — {config['description']}")
    print(f"Model: {model}  |  Temperature: {temperature}  |  Max tokens: {max_tokens}")
    print("Type 'quit' or 'exit' to end the session.\n")

    while True:
        # ── Get user input ──────────────────────────────────────────────────
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if user_input.lower() in {"quit", "exit", ""}:
            print("Goodbye.")
            break

        history.append({"role": "user", "content": user_input})

        # ── Token budget check ──────────────────────────────────────────────
        current_tokens = count_tokens([system_msg] + history, model)
        if current_tokens > CONTEXT_BUDGET_TOKENS:
            print(f"  [WARNING: context at {current_tokens} tokens — trimming history]")
            history = trim_history(history, system_msg, model, CONTEXT_BUDGET_TOKENS)

        # ── Call the API ────────────────────────────────────────────────────
        messages = [system_msg] + history
        t_start = time.perf_counter()

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        latency_ms = (time.perf_counter() - t_start) * 1_000

        # ── Extract and store the reply ─────────────────────────────────────
        assistant_msg = response.choices[0].message.content
        finish_reason = response.choices[0].finish_reason
        usage         = response.usage

        history.append({"role": "assistant", "content": assistant_msg})

        # ── Print the response ──────────────────────────────────────────────
        print(f"\nMedChat: {assistant_msg}\n")

        # ── Observability footer ────────────────────────────────────────────
        warn = " ⚠ TRUNCATED" if finish_reason == "length" else ""
        print(
            f"  [tokens: prompt={usage.prompt_tokens} "
            f"completion={usage.completion_tokens} "
            f"total={usage.total_tokens}{warn} | "
            f"latency={latency_ms:.0f}ms]\n"
        )

if __name__ == "__main__":
    main()
```

#### Step 4: Run MedChat and test with clinical questions

```bash
python chat.py
```

Try these five questions in sequence (they build on each other to test conversation history):

```
You: What is the first-line treatment for community-acquired pneumonia in a non-hospitalised adult?
You: What if the patient is allergic to penicillin?
You: Can I use azithromycin in a patient who is also on methadone?
You: What is the standard adult dose of amoxicillin-clavulanate for a skin infection?
You: Summarise the key points from our conversation so far.
```

Observe:
- The last question uses conversation history — MedChat should summarise the previous four turns.
- Every response shows the token and latency footer.
- Watch for context trimming warnings as the conversation grows.

#### Step 5: Create `prompts/system_v2.yaml` and observe prompt versioning

```yaml
version: "2.0"
description: "MedChat clinical Q&A assistant — conciseness update"
model: "gpt-4o-mini"
temperature: 0.1
max_tokens: 500
system_prompt: |
  You are MedChat, a clinical decision support assistant for junior doctors.
  You answer questions about drug dosages, contraindications, and treatment protocols
  based only on the information provided to you.
  If you are uncertain, say so clearly. Never invent drug names, dosages, or protocols.
  Always recommend consulting a senior clinician for patient-specific decisions.
  Format your responses clearly with headers when listing multiple items.
  Always cite the source of your information when possible.
  IMPORTANT: Respond in under 200 words. Be direct and concise.
```

Edit the `PROMPT_FILE` constant in `chat.py` to point to v2:

```python
PROMPT_FILE = "prompts/system_v2.yaml"
```

Run again with the same questions:

```bash
python chat.py
```

Compare response length. The 200-word constraint measurably shortens answers.

Now use `git diff` to show exactly what changed between versions:

```bash
git diff --no-index prompts/system_v1.yaml prompts/system_v2.yaml
```

> **Why this matters:** When a prompt change causes a clinical incident, the audit trail in git is the first document the review committee requests. Every meaningful prompt change should be a separate commit with a message explaining the clinical rationale — not just "minor edits".

Switch back to v1 for the remainder of the tutorial series:

```python
PROMPT_FILE = "prompts/system_v1.yaml"
```

---

### References

1. OpenAI Chat Completions API reference — <https://platform.openai.com/docs/api-reference/chat>
2. tiktoken tokeniser library — <https://github.com/openai/tiktoken>
3. OpenAI cookbook: How to count tokens — <https://cookbook.openai.com/examples/how_to_count_tokens_with_tiktoken>
4. Prompt engineering guide (OpenAI) — <https://platform.openai.com/docs/guides/prompt-engineering>
5. python-dotenv documentation — <https://saurabh-kumar.com/python-dotenv/>
