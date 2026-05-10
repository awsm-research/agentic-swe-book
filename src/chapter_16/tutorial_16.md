## 16.13 Tutorial: Serving, Containerising, and Monitoring ChestScan

The model is registered and approved. Now the radiology team wants a web interface where they can upload a chest X-ray and immediately see the diagnosis and an explanation of what the model detected. Your job is to build a FastAPI backend that loads the champion model from the MLflow registry, a Streamlit frontend for radiologists, and containerise the whole system with Docker Compose — so it runs identically on the hospital's on-premises server and every engineer's laptop.

**Concepts covered:** FastAPI, UploadFile, Pydantic, Streamlit, Docker multi-stage builds, Docker Compose, health checks, service dependencies, prediction logging, Population Stability Index drift detection

**Format:** Individual or pairs | **Duration:** ~2.5 hours | **Tool:** Python · FastAPI · Streamlit · Docker · Docker Compose · MLflow · hadolint · uvicorn

---

### Outline

- [Part A: Build the Backend and Frontend](#part-a-build-the-backend-and-frontend) *(~75 min)*
- [Part B: Containerise and Monitor](#part-b-containerise-and-monitor) *(~75 min)*

---

### Learning Objectives

By the end of this tutorial, you will be able to:

1. Build a FastAPI application that loads a model from the MLflow Model Registry at startup and serves predictions through typed REST endpoints.
2. Implement a Streamlit frontend that calls the backend API and renders diagnostic results with visual confidence indicators.
3. Write a multi-stage Dockerfile that produces a small, non-root runtime image verified by hadolint.
4. Compose three services (MLflow, backend, API) with health-check-based start-up ordering.
5. Log production predictions to MLflow as a drift-monitoring baseline.
6. Compute the Population Stability Index to detect class-distribution drift between training and production.

---

### Prerequisites

- Tutorials 13 and 14 completed: `davit-pneumonia-detector@champion` exists in the MLflow registry
- Docker Desktop (or Docker Engine + Compose plugin) installed and running
- hadolint installed (`brew install hadolint` on macOS, or download from [GitHub](https://github.com/hadolint/hadolint/releases))

Install Python dependencies for local development:

```bash
pip install fastapi uvicorn[standard] streamlit python-multipart httpx pillow
```

Verify Docker:

```bash
docker --version   # expect 24.x or later
docker compose version
```

---

### Part A: Build the Backend and Frontend

*(~75 min)*

#### Step 1: Create the project structure

```bash
mkdir davit-app && cd davit-app
mkdir -p backend frontend
touch backend/main.py backend/transforms.py backend/explainer.py
touch backend/requirements.txt frontend/app.py frontend/requirements.txt
touch docker-compose.yml
```

The final layout:

```
davit-app/
├── backend/
│   ├── main.py
│   ├── transforms.py
│   ├── explainer.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
└── docker-compose.yml
```

#### Step 2: Write `backend/transforms.py`

This file must contain the **exact same** transforms used during training in Tutorial 13. Any mismatch between training-time and inference-time preprocessing is one of the most common silent accuracy bugs in deployed ML systems.

```python
# backend/transforms.py
"""
Inference-time image transforms.

IMPORTANT: These must match get_transforms("val") from the training pipeline.
Mean and std are ImageNet statistics. Input is resized to 224×224 — no
random crop or flip at inference time.
"""

from torchvision import transforms

MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]


def get_inference_transform() -> transforms.Compose:
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD),
    ])
```

#### Step 3: Write `backend/explainer.py`

```python
# backend/explainer.py
"""
Grad-CAM overlay generator for the ResNet-18 model.
Returns a PIL Image that can be streamed as a PNG response.
"""

import io

import numpy as np
import torch
from PIL import Image
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget

from transforms import get_inference_transform

_transform = get_inference_transform()


def generate_gradcam(
    model: torch.nn.Module,
    pil_image: Image.Image,
    target_class: int,
    device: torch.device,
) -> bytes:
    """
    Generate a Grad-CAM overlay for ``target_class`` and return it as PNG bytes.

    Args:
        model: Loaded ResNet-18 in eval mode.
        pil_image: Input image as a PIL Image (RGB).
        target_class: Class index to explain (0=Normal, 1=Bacterial, 2=Viral).
        device: Inference device.

    Returns:
        PNG-encoded bytes of the heatmap overlay.
    """
    model.eval()
    target_layers = [model.layer4[-1]]

    raw = np.array(pil_image.resize((224, 224))).astype(np.float32) / 255.0

    tensor = _transform(pil_image).unsqueeze(0).to(device)

    cam = GradCAM(model=model, target_layers=target_layers)
    grayscale = cam(
        input_tensor=tensor,
        targets=[ClassifierOutputTarget(target_class)],
    )[0]

    overlay = show_cam_on_image(raw, grayscale, use_rgb=True)
    pil_overlay = Image.fromarray(overlay)

    buf = io.BytesIO()
    pil_overlay.save(buf, format="PNG")
    return buf.getvalue()
```

#### Step 4: Write `backend/main.py`

```python
# backend/main.py
"""
FastAPI inference server for ChestScan.

Endpoints:
  GET  /health   — liveness + model metadata
  POST /predict  — returns diagnosis JSON
  POST /explain  — returns Grad-CAM PNG
"""

import io
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime

import mlflow
import mlflow.pytorch
import torch
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from PIL import Image
from pydantic import BaseModel

from explainer import generate_gradcam
from transforms import get_inference_transform

# ---------------------------------------------------------------------------
# Configuration (override via environment variables in Docker Compose)
# ---------------------------------------------------------------------------
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
MODEL_URI = os.getenv("MODEL_URI", "models:/davit-pneumonia-detector@champion")
PRODUCTION_EXPERIMENT = "chest-xray-production"
MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB

CLASS_NAMES = ["Normal", "Bacterial Pneumonia", "Viral Pneumonia"]
DIAGNOSIS_LABELS = {0: "Normal", 1: "Pneumonia", 2: "Pneumonia"}

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# ---------------------------------------------------------------------------
# Global model state (populated at startup)
# ---------------------------------------------------------------------------
_state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model from MLflow registry before accepting requests."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Loading {MODEL_URI} on {device} …")
    model = mlflow.pytorch.load_model(MODEL_URI, map_location=device)
    model.eval()

    # Retrieve the resolved model version for the health endpoint
    client = mlflow.tracking.MlflowClient()
    mv = client.get_model_version_by_alias(
        "davit-pneumonia-detector", "champion"
    )

    _state["model"] = model
    _state["device"] = device
    _state["model_version"] = mv.version
    _state["transform"] = get_inference_transform()

    mlflow.set_experiment(PRODUCTION_EXPERIMENT)
    print(f"Model version {mv.version} ready.")
    yield
    _state.clear()


app = FastAPI(title="ChestScan API", lifespan=lifespan)


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------
class HealthResponse(BaseModel):
    status: str
    model_version: str
    device: str


class PredictResponse(BaseModel):
    diagnosis: str
    predicted_class: int
    predicted_class_name: str
    confidence: float
    probabilities: dict[str, float]
    model_version: str
    inference_time_ms: float


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _read_image(file: UploadFile) -> Image.Image:
    if file.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(
            status_code=415, detail="Only JPEG and PNG images are accepted."
        )
    raw = file.file.read()
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds 10 MB limit.")
    return Image.open(io.BytesIO(raw)).convert("RGB")


def _infer(pil_image: Image.Image) -> tuple[torch.Tensor, float]:
    """Return (softmax_probs tensor, inference_ms)."""
    tensor = _state["transform"](pil_image).unsqueeze(0).to(_state["device"])
    t0 = time.perf_counter()
    with torch.no_grad():
        logits = _state["model"](tensor)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    probs = torch.softmax(logits, dim=1)[0]
    return probs, elapsed_ms


def _log_prediction(probs: torch.Tensor, pred_class: int) -> None:
    """Log a single prediction as an MLflow run for drift monitoring."""
    with mlflow.start_run(run_name="production-prediction"):
        mlflow.log_param("model_version", _state["model_version"])
        mlflow.log_param("timestamp", datetime.utcnow().isoformat())
        mlflow.log_param("predicted_class", pred_class)
        mlflow.log_metric("prob_normal", probs[0].item())
        mlflow.log_metric("prob_bacterial", probs[1].item())
        mlflow.log_metric("prob_viral", probs[2].item())


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok",
        model_version=_state.get("model_version", "unknown"),
        device=str(_state.get("device", "unknown")),
    )


@app.post("/predict", response_model=PredictResponse)
async def predict(file: UploadFile):
    pil_image = _read_image(file)
    probs, elapsed_ms = _infer(pil_image)
    pred_class = int(probs.argmax().item())
    confidence = float(probs[pred_class].item())

    _log_prediction(probs, pred_class)

    return PredictResponse(
        diagnosis=DIAGNOSIS_LABELS[pred_class],
        predicted_class=pred_class,
        predicted_class_name=CLASS_NAMES[pred_class],
        confidence=confidence,
        probabilities={
            name: float(probs[i].item()) for i, name in enumerate(CLASS_NAMES)
        },
        model_version=_state["model_version"],
        inference_time_ms=round(elapsed_ms, 2),
    )


@app.post("/explain")
async def explain(file: UploadFile):
    pil_image = _read_image(file)
    probs, _ = _infer(pil_image)
    pred_class = int(probs.argmax().item())

    png_bytes = generate_gradcam(
        model=_state["model"],
        pil_image=pil_image,
        target_class=pred_class,
        device=_state["device"],
    )
    return StreamingResponse(io.BytesIO(png_bytes), media_type="image/png")
```

Write `backend/requirements.txt`:

```text
fastapi==0.111.1
uvicorn[standard]==0.30.1
mlflow==2.13.2
torch==2.3.1
torchvision==0.18.1
grad-cam==1.5.2
Pillow==10.3.0
python-multipart==0.0.9
pydantic==2.7.3
```

#### Step 5: Test the backend locally

Start the server:

```bash
cd davit-app/backend
export MLFLOW_TRACKING_URI=http://localhost:5000
uvicorn main:app --reload --port 8000
```

In a second terminal, test each endpoint:

```bash
# Health check
curl http://localhost:8000/health

# Prediction (replace with a real X-ray path)
curl -X POST http://localhost:8000/predict \
  -F "file=@/path/to/chest_xray/test/PNEUMONIA/BACTERIA_1.jpeg" \
  | python -m json.tool

# Grad-CAM — save overlay to disk
curl -X POST http://localhost:8000/explain \
  -F "file=@/path/to/chest_xray/test/PNEUMONIA/BACTERIA_1.jpeg" \
  --output gradcam_test.png
open gradcam_test.png   # macOS; use xdg-open on Linux
```

Expected health check response:

```json
{"status": "ok", "model_version": "1", "device": "cpu"}
```

#### Step 6: Write `frontend/app.py`

```python
# frontend/app.py
"""
Streamlit radiologist interface for ChestScan.
"""

import io
import os

import httpx
import streamlit as st
from PIL import Image

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

CLASS_COLORS = {
    "Normal": "green",
    "Pneumonia": "red",
}

st.set_page_config(
    page_title="ChestScan",
    page_icon="🫁",
    layout="centered",
)

st.title("Chest X-Ray ChestScan")
st.caption("Upload a chest X-ray to receive an AI-assisted diagnosis.")

uploaded = st.file_uploader(
    "Choose a chest X-ray image", type=["jpg", "jpeg", "png"]
)

if uploaded is not None:
    image_bytes = uploaded.read()
    pil_image = Image.open(io.BytesIO(image_bytes))

    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Uploaded X-ray")
        st.image(pil_image, use_container_width=True)

    # --- Prediction ---
    with st.spinner("Running inference …"):
        try:
            resp = httpx.post(
                f"{BACKEND_URL}/predict",
                files={"file": (uploaded.name, image_bytes, uploaded.type)},
                timeout=30,
            )
            resp.raise_for_status()
            result = resp.json()
        except httpx.HTTPStatusError as e:
            st.error(f"Prediction failed: {e.response.text}")
            st.stop()
        except httpx.RequestError as e:
            st.error(f"Cannot reach backend at {BACKEND_URL}: {e}")
            st.stop()

    diagnosis = result["diagnosis"]
    confidence = result["confidence"]
    color = CLASS_COLORS.get(diagnosis, "orange")

    with col2:
        st.subheader("Diagnosis")
        st.markdown(
            f"<h2 style='color:{color};'>{diagnosis}</h2>",
            unsafe_allow_html=True,
        )
        st.metric("Confidence", f"{confidence:.1%}")
        st.caption(
            f"Predicted class: {result['predicted_class_name']}  |  "
            f"Model v{result['model_version']}  |  "
            f"{result['inference_time_ms']:.0f} ms"
        )

    st.subheader("Class Probabilities")
    probs = result["probabilities"]
    for class_name, prob in probs.items():
        st.progress(prob, text=f"{class_name}: {prob:.1%}")

    st.divider()
    if st.button("Show Grad-CAM Explanation"):
        with st.spinner("Generating heatmap …"):
            try:
                explain_resp = httpx.post(
                    f"{BACKEND_URL}/explain",
                    files={"file": (uploaded.name, image_bytes, uploaded.type)},
                    timeout=60,
                )
                explain_resp.raise_for_status()
                overlay = Image.open(io.BytesIO(explain_resp.content))
            except httpx.HTTPStatusError as e:
                st.error(f"Explanation failed: {e.response.text}")
                st.stop()

        exp_col1, exp_col2 = st.columns(2)
        with exp_col1:
            st.subheader("Original")
            st.image(pil_image, use_container_width=True)
        with exp_col2:
            st.subheader("Grad-CAM Heatmap")
            st.image(overlay, use_container_width=True)
        st.caption(
            "Red/warm regions show areas the model weighted most heavily for the predicted class."
        )
```

Write `frontend/requirements.txt`:

```text
streamlit==1.35.0
httpx==0.27.0
Pillow==10.3.0
```

---

### Part B: Containerise and Monitor

*(~75 min)*

#### Step 1: Write `backend/Dockerfile`

```dockerfile
# backend/Dockerfile
# ── Stage 1: Builder ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build tools and compile wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: Runtime ─────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Copy only the installed packages from the builder — no compiler in runtime
COPY --from=builder /install /usr/local

WORKDIR /app
COPY main.py transforms.py explainer.py ./

# Run as non-root to limit blast radius if the container is compromised
RUN useradd -m appuser
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

> **Why multi-stage?** The builder stage needs `gcc` and development headers to compile Python packages with C extensions (e.g., PyTorch). Copying only `/install` to the runtime stage means the final image contains no compiler — reducing the attack surface and cutting image size by ~200 MB.

> **Why non-root?** If an attacker exploits a vulnerability in the application or a dependency, running as `appuser` instead of root limits what they can do: they cannot write to system directories, install packages, or escalate privileges.

#### Step 2: Write `frontend/Dockerfile`

```dockerfile
# frontend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

RUN useradd -m streamlituser
USER streamlituser

EXPOSE 8501

HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
```

#### Step 3: Run hadolint on both Dockerfiles

```bash
hadolint davit-app/backend/Dockerfile
hadolint davit-app/frontend/Dockerfile
```

Common warnings and fixes:

| Warning | Fix |
|---|---|
| `DL3008` — pin apt packages | Add `=<version>` to apt-get installs or add `# hadolint ignore=DL3008` |
| `DL3013` — pin pip packages | Already done via `requirements.txt` with pinned versions |
| `DL3045` — `COPY` without `--chown` | Add `--chown=appuser:appuser` to the final `COPY` instruction |

Fix any warnings, then re-run until the output is empty.

#### Step 4: Write `docker-compose.yml`

```yaml
# docker-compose.yml
version: "3.9"

services:

  mlflow:
    image: ghcr.io/mlflow/mlflow:v2.13.2
    ports:
      - "5000:5000"
    volumes:
      - mlflow_data:/mlflow
    command: >
      mlflow server
        --host 0.0.0.0
        --port 5000
        --backend-store-uri sqlite:////mlflow/mlflow.db
        --default-artifact-root /mlflow/artifacts
    healthcheck:
      test: ["CMD", "python", "-c",
             "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"]
      interval: 15s
      timeout: 5s
      start_period: 20s
      retries: 5

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      MLFLOW_TRACKING_URI: http://mlflow:5000
      MODEL_URI: models:/davit-pneumonia-detector@champion
    depends_on:
      mlflow:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "python", "-c",
             "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 15s
      timeout: 5s
      start_period: 60s
      retries: 5

  frontend:
    build: ./frontend
    ports:
      - "8501:8501"
    environment:
      BACKEND_URL: http://backend:8000
    depends_on:
      backend:
        condition: service_healthy

volumes:
  mlflow_data:
```

> **Why `depends_on` with `condition: service_healthy`?** Docker Compose without health-check conditions starts services in declaration order but does not wait for them to be ready. The backend tries to load the model from MLflow on startup — if MLflow is not yet accepting connections, the backend crashes. Health-check-based ordering guarantees that each service only starts after its dependency passes its health check.

#### Step 5: Build and start all services

```bash
cd davit-app
docker compose up --build
```

Wait for all three services to print healthy status. You will see lines like:

```
davit-app-mlflow-1   | [INFO] Listening at: http://0.0.0.0:5000
davit-app-backend-1  | INFO:     Application startup complete.
davit-app-frontend-1 | You can now view your Streamlit app in your browser.
```

Verify each service independently:

```bash
curl http://localhost:5000/health          # MLflow
curl http://localhost:8000/health          # Backend
curl http://localhost:8501/_stcore/health  # Streamlit
```

#### Step 6: Upload a test X-ray in the Streamlit UI

Open [http://localhost:8501](http://localhost:8501) in your browser.

1. Click **Browse files** and upload any JPEG from `data/chest_xray/test/`
2. The diagnosis badge appears within a few seconds
3. Click **Show Grad-CAM Explanation** — the heatmap loads alongside the original
4. Return to [http://localhost:5000](http://localhost:5000), navigate to the `chest-xray-production` experiment, and confirm a new run appears with the prediction metrics logged

#### Step 7: Write `monitor.py` — drift detection

Save outside `davit-app/` in the project root:

```python
# monitor.py
"""
Population Stability Index (PSI) drift detector.

Reads the last N production predictions from MLflow and compares the
predicted class distribution against the training baseline.

PSI < 0.1  : No significant drift
PSI 0.1–0.2: Moderate drift — investigate
PSI > 0.2  : Significant drift — retrain or escalate
"""

import argparse

import mlflow
import numpy as np
from mlflow.tracking import MlflowClient

MLFLOW_TRACKING_URI = "http://localhost:5000"
PRODUCTION_EXPERIMENT = "chest-xray-production"

# Training set class distribution (from Tutorial 13 dataset metadata)
# Normal=1341, Bacterial=2530, Viral=1345 → normalise to proportions
TRAINING_BASELINE = np.array([1341, 2530, 1345], dtype=float)
TRAINING_BASELINE /= TRAINING_BASELINE.sum()

CLASS_NAMES = ["Normal", "Bacterial Pneumonia", "Viral Pneumonia"]
PSI_ALERT_THRESHOLD = 0.2
PSI_WARN_THRESHOLD = 0.1


def compute_psi(expected: np.ndarray, actual: np.ndarray) -> float:
    """
    Population Stability Index: sum((actual - expected) * ln(actual / expected)).
    Applies a small epsilon to avoid division-by-zero on empty buckets.
    """
    eps = 1e-6
    actual = np.clip(actual, eps, None)
    expected = np.clip(expected, eps, None)
    return float(np.sum((actual - expected) * np.log(actual / expected)))


def collect_production_predictions(n: int = 100) -> np.ndarray | None:
    """
    Return an (n_runs, 3) array of softmax probabilities from production runs,
    or None if fewer than 10 runs exist.
    """
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    client = MlflowClient()
    experiment = client.get_experiment_by_name(PRODUCTION_EXPERIMENT)

    if experiment is None:
        print(f"Experiment '{PRODUCTION_EXPERIMENT}' not found.")
        return None

    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        filter_string="tags.mlflow.runName = 'production-prediction'",
        order_by=["start_time DESC"],
        max_results=n,
    )

    if len(runs) < 10:
        print(f"Only {len(runs)} production runs found — need at least 10 for PSI.")
        return None

    probs = []
    for run in runs:
        m = run.data.metrics
        row = [m.get("prob_normal", 0.0), m.get("prob_bacterial", 0.0),
               m.get("prob_viral", 0.0)]
        probs.append(row)
    return np.array(probs)


def run_monitor(n: int = 100) -> None:
    probs = collect_production_predictions(n)
    if probs is None:
        return

    # Predicted class distribution = argmax of each run's probabilities
    pred_classes = probs.argmax(axis=1)
    class_counts = np.bincount(pred_classes, minlength=3).astype(float)
    production_dist = class_counts / class_counts.sum()

    psi = compute_psi(TRAINING_BASELINE, production_dist)

    print(f"\nDrift Report — last {len(probs)} production predictions")
    print("-" * 50)
    print(f"{'Class':<25} {'Training':>10} {'Production':>12}")
    for i, name in enumerate(CLASS_NAMES):
        print(f"  {name:<23} {TRAINING_BASELINE[i]:>10.3f} {production_dist[i]:>12.3f}")
    print("-" * 50)
    print(f"PSI = {psi:.4f}")

    if psi > PSI_ALERT_THRESHOLD:
        print(f"\n*** DRIFT DETECTED (PSI={psi:.4f} > {PSI_ALERT_THRESHOLD}) ***")
        print("Action: review recent X-ray sources, consider retraining.")
    elif psi > PSI_WARN_THRESHOLD:
        print(f"\nWarning: moderate drift (PSI={psi:.4f}). Monitor closely.")
    else:
        print(f"\nNo significant drift detected (PSI={psi:.4f} < {PSI_WARN_THRESHOLD}).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=100,
                        help="Number of recent production runs to analyse")
    args = parser.parse_args()
    run_monitor(args.n)
```

```bash
python monitor.py --n 100
```

#### Step 8: View the production run in the MLflow UI

1. Go to [http://localhost:5000](http://localhost:5000)
2. Click the **chest-xray-production** experiment in the left sidebar
3. Each row is one inference request — click a run to see `prob_normal`, `prob_bacterial`, `prob_viral`, and the `model_version` parameter
4. Use the **Chart** tab to plot `prob_viral` over time — an upward trend alongside stable `prob_normal` might indicate a seasonal respiratory illness wave reaching the radiology queue

---

### References

- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [Streamlit documentation](https://docs.streamlit.io/)
- [Docker multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
- [hadolint — Dockerfile linter](https://github.com/hadolint/hadolint)
- [Population Stability Index — a practical introduction](https://mwburke.github.io/data%20science/2018/04/29/population-stability-index.html)
