## 13.8 Tutorial: Setting Up Your SE4AI Development Environment

You are joining a team that builds and maintains ML-powered and LLM-powered clinical applications. Before you can contribute to ChestScan (the pneumonia detection model), MedChat (the clinical RAG chatbot), or MedAgent (the autonomous clinical agent), you need a working environment. This tutorial sets up everything you will use across Tutorials 14–24: a Python environment manager, PyTorch, MLflow, an LLM API key, LangChain, LangGraph, and a local PostgreSQL instance for audit logs. By the end you will have each component verified with a short smoke test.

**Concepts covered:** Python environment management with `uv`, PyTorch CPU/GPU verification, MLflow local tracking server, OpenAI API key configuration, LangChain and LangGraph installation, Docker-based PostgreSQL

**Format:** Individual | **Duration:** ~45 min | **Tool:** Python · uv · PyTorch · MLflow · Docker · OpenAI API · LangChain · LangGraph

---

### Outline

- [Learning Objectives](#learning-objectives)
- [Prerequisites](#prerequisites)
- [Part A: Python Environment and ML Dependencies](#part-a-python-environment-and-ml-dependencies-15-min)
- [Part B: MLflow Tracking Server](#part-b-mlflow-tracking-server-10-min)
- [Part C: LLM and Agent Toolchain](#part-c-llm-and-agent-toolchain-15-min)
- [Part D: Verify Everything Works](#part-d-verify-everything-works-5-min)
- [References](#references)

---

### Learning Objectives

By the end of this tutorial, you will be able to:

1. Create and activate an isolated Python environment using `uv` for each project area.
2. Install and verify PyTorch on CPU (or GPU if available).
3. Start a local MLflow tracking server and log a test run to confirm it is working.
4. Configure an OpenAI API key and verify it with a single API call.
5. Install and verify LangChain, LangGraph, and LangSmith for agent development.
6. Start a local PostgreSQL container using Docker and confirm connectivity.

---

### Prerequisites

- macOS, Linux, or WSL2 on Windows
- Python 3.11 or 3.12 installed (via [pyenv](https://github.com/pyenv/pyenv) or system package manager)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- An OpenAI account with an API key (free tier is sufficient for most tutorials)
- Git installed

Verify before starting:

```bash
python --version      # should print 3.11.x or 3.12.x
docker --version      # should print Docker version 24+
git --version
```

---

### Part A: Python Environment and ML Dependencies *(~15 min)*

#### Step 1: Install `uv`

`uv` is the package and project manager used throughout this book. It replaces `pip` and `venv` with a single fast tool and produces reproducible lockfiles.

```bash
curl -Lsf https://astral.sh/uv/install.sh | sh
```

Verify:

```bash
uv --version
# uv 0.4.x or later
```

#### Step 2: Create the ML project environment

All MLOps tutorials (14–16) share a single environment called `chestscan-env`.

```bash
mkdir -p ~/se4ai/chestscan
cd ~/se4ai/chestscan
uv init --python 3.11
uv add torch torchvision scikit-learn mlflow matplotlib pyyaml
```

Activate the environment:

```bash
source .venv/bin/activate
python --version
```

> **GPU note:** If you have an NVIDIA GPU, replace `torch torchvision` with `torch torchvision --index-url https://download.pytorch.org/whl/cu121` to install the CUDA-enabled build.

#### Step 3: Verify PyTorch

```python
# Run this as a quick script or in a Python REPL
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"Device: {'cuda' if torch.cuda.is_available() else 'cpu'}")

# Smoke test: create a small tensor and run a matrix multiply
a = torch.randn(4, 4)
b = torch.randn(4, 4)
c = torch.mm(a, b)
print(f"Matrix multiply output shape: {c.shape}")
print("PyTorch OK")
```

```bash
python -c "
import torch
print(f'PyTorch {torch.__version__} — CUDA: {torch.cuda.is_available()}')
a = torch.randn(4, 4)
print(f'Tensor device: {a.device}')
print('PyTorch OK')
"
```

Expected output:

```
PyTorch 2.x.x — CUDA: False
Tensor device: cpu
PyTorch OK
```

#### Step 4: Activity — verify scikit-learn and MLflow import

Confirm that both packages imported correctly before moving to the tracking server:

```bash
python -c "
import sklearn, mlflow
print(f'scikit-learn {sklearn.__version__}')
print(f'MLflow {mlflow.__version__}')
print('ML dependencies OK')
"
```

---

### Part B: MLflow Tracking Server *(~10 min)*

#### Step 1: Start the local tracking server

MLflow's local tracking server stores run metadata in SQLite and artifacts on the local filesystem. This is sufficient for all tutorials in this book.

```bash
# From inside ~/se4ai/chestscan with the environment active
mlflow server \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./mlflow-artifacts \
  --host 127.0.0.1 \
  --port 5000
```

Leave this terminal running. Open a second terminal for the next step.

#### Step 2: Log a test run

```python
# ~/se4ai/chestscan/test_mlflow.py
import mlflow

mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("se4ai-smoke-test")

with mlflow.start_run(run_name="environment-check"):
    mlflow.log_param("python_version", "3.11")
    mlflow.log_metric("test_metric", 1.0)
    mlflow.set_tag("purpose", "environment verification")
    print(f"Run ID: {mlflow.active_run().info.run_id}")
    print("MLflow run logged successfully")
```

```bash
python test_mlflow.py
```

Open <http://127.0.0.1:5000> in your browser. You should see the `se4ai-smoke-test` experiment with one run listed.

> **What you are looking at:** The MLflow UI shows every run you log — its parameters, metrics, tags, and artifact links. From Tutorial 14 onward, every ChestScan training run will appear here, making it possible to compare runs and select the best model for registration.

#### Step 3: Activity — log an additional metric

Extend `test_mlflow.py` to log a second metric called `data_samples` with value `5856` (the ChestScan dataset size). Confirm it appears as a new metric in the MLflow UI for the same run. Then stop the tracking server with Ctrl+C.

---

### Part C: LLM and Agent Toolchain *(~15 min)*

#### Step 1: Create the LLMOps and AgentOps environment

LLMOps tutorials (17–21) and AgentOps tutorials (22–24) share a single environment called `medchat-env`.

```bash
mkdir -p ~/se4ai/medchat
cd ~/se4ai/medchat
uv init --python 3.11
uv add openai langchain langchain-openai langgraph langsmith \
       fastapi uvicorn pydantic python-dotenv \
       chromadb sentence-transformers psycopg2-binary pyyaml pytest
```

#### Step 2: Configure your OpenAI API key

Create a `.env` file (never commit this to Git):

```bash
# ~/se4ai/medchat/.env
OPENAI_API_KEY=sk-...your-key-here...
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=medchat-tutorial
```

Add `.env` to `.gitignore`:

```bash
echo ".env" >> .gitignore
echo "*.db" >> .gitignore
```

#### Step 3: Verify the OpenAI API

```python
# ~/se4ai/medchat/test_openai.py
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Reply with exactly: SE4AI environment OK"}],
    max_tokens=20,
)
print(response.choices[0].message.content)
print(f"Model: {response.model}")
print(f"Tokens used: {response.usage.total_tokens}")
```

```bash
source .venv/bin/activate
python test_openai.py
```

Expected output:

```
SE4AI environment OK
Model: gpt-4o-mini-...
Tokens used: 14
```

#### Step 4: Verify LangChain and LangGraph

```bash
python -c "
from dotenv import load_dotenv; load_dotenv()
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

llm = ChatOpenAI(model='gpt-4o-mini', max_tokens=10)
response = llm.invoke('Reply: LangChain OK')
print(response.content)

# Verify LangGraph can build a minimal graph
from typing import TypedDict
class S(TypedDict):
    x: int
g = StateGraph(S)
g.add_node('n', lambda s: {'x': s['x'] + 1})
g.set_entry_point('n')
g.add_edge('n', END)
app = g.compile()
result = app.invoke({'x': 0})
print(f'LangGraph graph output: {result}')
print('LangChain and LangGraph OK')
"
```

#### Step 5: Start a PostgreSQL container for audit logging

Tutorial 24 uses PostgreSQL for the append-only audit log. Verify Docker is working now so you do not hit setup delays later.

```bash
docker run -d \
  --name se4ai-postgres \
  -e POSTGRES_USER=medagent \
  -e POSTGRES_PASSWORD=medagent_secret \
  -e POSTGRES_DB=medagent \
  -p 5432:5432 \
  postgres:16
```

Wait a few seconds, then verify:

```bash
docker exec se4ai-postgres pg_isready -U medagent
# /var/run/postgresql:5432 - accepting connections
```

Stop the container when done (it will be started again in Tutorial 24):

```bash
docker stop se4ai-postgres
```

#### Step 6: Activity — confirm all package versions

Run this verification script and save the output. Paste it into your lab notebook or submission.

```bash
python -c "
import importlib, sys

packages = [
    'openai', 'langchain', 'langchain_openai', 'langgraph',
    'langsmith', 'fastapi', 'pydantic', 'chromadb',
    'sentence_transformers', 'psycopg2', 'yaml', 'pytest',
]
print(f'Python {sys.version}')
for pkg in packages:
    try:
        mod = importlib.import_module(pkg)
        version = getattr(mod, '__version__', 'installed')
        print(f'  {pkg}: {version}')
    except ImportError:
        print(f'  {pkg}: MISSING')
"
```

Every package should show a version number, not `MISSING`.

---

### Part D: Verify Everything Works *(~5 min)*

#### Step 1: Final smoke test

From the `chestscan` environment, confirm the ML stack is ready:

```bash
cd ~/se4ai/chestscan
source .venv/bin/activate
python -c "
import torch, sklearn, mlflow
print(f'torch {torch.__version__} | sklearn {sklearn.__version__} | mlflow {mlflow.__version__}')
print('ChestScan environment ready')
"
```

From the `medchat` environment, confirm the LLM and agent stack is ready:

```bash
cd ~/se4ai/medchat
source .venv/bin/activate
python -c "
import openai, langchain, langgraph
print(f'openai {openai.__version__} | langchain {langchain.__version__} | langgraph {langgraph.__version__}')
print('MedChat/MedAgent environment ready')
"
```

Both should print without errors.

#### Step 2: Activity — project structure check

Create the directory structure you will build into across all tutorials:

```bash
mkdir -p ~/se4ai/chestscan/data/{raw,processed}
mkdir -p ~/se4ai/chestscan/models
mkdir -p ~/se4ai/medchat/{prompts,rag,agent}
touch ~/se4ai/chestscan/.gitignore
touch ~/se4ai/medchat/.gitignore
echo "*.db\nmlflow-artifacts/\n__pycache__/\n.env" | tee ~/se4ai/chestscan/.gitignore ~/se4ai/medchat/.gitignore
```

Verify the layout:

```bash
find ~/se4ai -maxdepth 3 -type d | sort
```

You should see both `chestscan/` and `medchat/` subtrees. This is the workspace you will fill across Tutorials 14–24.

---

### References

1. uv documentation: <https://docs.astral.sh/uv/>
2. PyTorch installation guide: <https://pytorch.org/get-started/locally/>
3. MLflow tracking server: <https://mlflow.org/docs/latest/tracking.html>
4. OpenAI API reference: <https://platform.openai.com/docs/api-reference>
5. LangGraph quickstart: <https://langchain-ai.github.io/langgraph/tutorials/introduction/>
6. Docker Desktop: <https://www.docker.com/products/docker-desktop/>
