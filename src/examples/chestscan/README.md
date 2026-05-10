# ChestScan — Pneumonia Detection System

A three-class chest X-ray classifier (Normal / Bacterial Pneumonia / Viral Pneumonia) built with PyTorch, served via FastAPI, and tracked with MLflow. Accompanies Tutorials 14–16 of *Agentic Software Engineering*.

---

## Architecture

```
chestscan/
├── train.py                  # Model training (ResNet-18 or DAViT)
├── evaluate.py               # Clinical metric evaluation
├── explain.py                # Grad-CAM saliency maps
├── register_and_promote.py   # MLflow model registry promotion
├── gate.py                   # Quality gate (blocks promotion if metrics fail)
├── monitor.py                # Production drift monitoring
├── dataset.py                # Dataset class and dataloader builder
├── transforms.py             # Train / val image transforms (shared with backend)
├── requirements.txt          # Training dependencies
├── model_card.yaml           # Model card (intended use, limitations, metrics)
├── docker-compose.yml        # Three-service stack
├── backend/                  # FastAPI inference server
│   ├── Dockerfile
│   ├── main.py               # /health, /predict, /explain endpoints
│   └── requirements.txt
└── frontend/                 # Streamlit radiologist UI
    ├── Dockerfile
    ├── app.py
    └── requirements.txt
```

The model is **not baked into the Docker image**. The backend loads the registered champion model from MLflow at startup, so promoting a new model version requires no image rebuild.

---

## Prerequisites

- Docker Desktop 24+ (running)
- Python 3.11 (for local training only)
- The [Kaggle chest X-ray dataset](https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia) extracted to `./chest_xray/`

Expected dataset layout:

```
chest_xray/
├── train/
│   ├── NORMAL/
│   ├── BACTERIA/
│   └── VIRUS/
├── val/
└── test/
```

---

## Quickstart — Docker (Tutorials 16)

The Docker stack runs MLflow, the FastAPI backend, and the Streamlit frontend. Before starting it you need a trained, registered model. Follow the two-step process below.

### Step 1: Train and register a model (local)

Install training dependencies:

```bash
pip install -r requirements.txt
```

Train (ResNet-18 baseline, ~15 min on CPU):

```bash
python train.py \
  --model resnet18 \
  --data-root ./chest_xray \
  --epochs 30 \
  --mlflow-uri http://localhost:5000
```

Copy the `run_id` printed at the end (e.g. `abc12345`), then evaluate:

```bash
python evaluate.py \
  --run-id abc12345 \
  --data-root ./chest_xray \
  --mlflow-uri http://localhost:5000
```

Run the quality gate, then register:

```bash
python gate.py --run-id abc12345 --mlflow-uri http://localhost:5000
python register_and_promote.py --run-id abc12345 --mlflow-uri http://localhost:5000
```

This registers the model as `chestscan-pneumonia-detector` with the alias `champion`.

### Step 2: Start the Docker stack

```bash
docker compose up --build
```

Service startup order is enforced by health checks:

1. **mlflow** starts first (SQLite backend, local artifact store)
2. **backend** starts after MLflow is healthy — loads the champion model from the registry
3. **frontend** starts after the backend is healthy

Wait for all three containers to show `healthy`:

```bash
docker compose ps
```

| Service  | URL                           | Purpose                        |
|----------|-------------------------------|--------------------------------|
| MLflow   | http://localhost:5000         | Experiment tracking + registry |
| Backend  | http://localhost:8000/docs    | FastAPI OpenAPI docs            |
| Frontend | http://localhost:8501         | Streamlit radiologist UI        |

---

## Using the Stack

### Upload an X-ray via the Streamlit UI

Open http://localhost:8501, upload a JPEG or PNG chest X-ray, and the UI returns:

- Predicted class (Normal / Bacterial / Viral)
- Per-class probabilities
- Grad-CAM heatmap overlay showing which region drove the prediction

### Call the API directly

```bash
# Health check
curl http://localhost:8000/health

# Classify an image
curl -X POST http://localhost:8000/predict \
  -F "file=@/path/to/xray.jpg"

# Get a Grad-CAM heatmap (returns PNG)
curl -X POST http://localhost:8000/explain \
  -F "file=@/path/to/xray.jpg" \
  --output heatmap.png
```

Example `/predict` response:

```json
{
  "prediction": "BACTERIA",
  "confidence": 0.87,
  "probabilities": {
    "NORMAL": 0.06,
    "BACTERIA": 0.87,
    "VIRUS": 0.07
  },
  "inference_ms": 42
}
```

---

## Local Training Workflows (Tutorials 14–15)

Run a local MLflow tracking server first:

```bash
mlflow server \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./mlflow-artifacts \
  --host 127.0.0.1 \
  --port 5000
```

Then use the training scripts independently:

| Script                    | Purpose                                        |
|---------------------------|------------------------------------------------|
| `train.py`                | Train ResNet-18 or DAViT; logs to MLflow       |
| `evaluate.py`             | Full clinical metric suite + ROC curve plots   |
| `explain.py`              | Grad-CAM saliency maps for a batch of images   |
| `gate.py`                 | Quality gate — fails if AUC or sensitivity low |
| `register_and_promote.py` | Register model, assign `champion` alias        |
| `monitor.py`              | PSI-based drift detection on production logs   |

### Train the DAViT hybrid model

```bash
python train.py \
  --model davit \
  --data-root ./chest_xray \
  --epochs 30 \
  --lr 1e-4 \
  --mlflow-uri http://localhost:5000
```

### Generate Grad-CAM explanations

```bash
python explain.py \
  --run-id abc12345 \
  --data-root ./chest_xray \
  --mlflow-uri http://localhost:5000
```

---

## Docker Reference

```bash
# Build and start all services (foreground)
docker compose up --build

# Start in background
docker compose up --build -d

# Tail backend logs
docker compose logs -f backend

# Check health of all services
docker compose ps

# Stop and remove containers (keep the MLflow data volume)
docker compose down

# Stop and remove containers AND the MLflow data volume
docker compose down -v
```

The `mlflow_data` Docker volume persists the SQLite database and artifact store across restarts. Removing it with `docker compose down -v` clears all experiment history.

---

## Model Card

| Property        | Value                                                        |
|-----------------|--------------------------------------------------------------|
| Architecture    | Hybrid CNN+ViT (ResNet-34 backbone + 6-layer ViT)           |
| Training data   | Kaggle Chest X-Ray (Guangzhou Women and Children's Medical Centre), n=5856 |
| Classes         | Normal, Bacterial Pneumonia, Viral Pneumonia                 |
| AUC             | 0.96                                                         |
| Sensitivity     | 0.94                                                         |
| Specificity     | 0.91                                                         |
| Macro F1        | 0.93                                                         |
| Intended use    | Clinical decision support for radiologists                   |
| Not for         | Autonomous diagnosis; adult populations; non-paediatric cohorts |

---

## Dataset

Download from Kaggle: https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia

The dataset contains 5,856 paediatric chest X-rays from Guangzhou Women and Children's Medical Centre. The `BACTERIA/` and `VIRUS/` subdirectories correspond to the two pneumonia subtypes. The dataset ships with a pre-defined `train/val/test` split — do not reshuffle it randomly, as the split is patient-level to prevent data leakage.
