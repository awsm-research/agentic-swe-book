# backend/main.py
# FastAPI serving backend for the ChestScan pneumonia detector.
#
# Three endpoints:
#   GET  /health   — liveness/readiness check for Docker and load balancers
#   POST /predict  — classify a chest X-ray image (JPEG/PNG, max 10 MB)
#   POST /explain  — return a Grad-CAM heatmap overlay as a PNG StreamingResponse
#
# The model is loaded from the MLflow Model Registry at startup via the
# singleton ModelRegistry class.  Loading once at startup (not per request)
# is critical for acceptable response latency.
#
# Each prediction is logged asynchronously to the MLflow 'production-predictions'
# experiment for downstream drift monitoring.

import io
import logging
import os
import sys
import uuid
from contextlib import asynccontextmanager
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mlflow
import numpy as np
import torch
from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from PIL import Image
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Shared modules (copied into the container from the project root)
# ---------------------------------------------------------------------------
sys.path.insert(0, "/app")
from transforms import get_val_transforms  # noqa: E402
from dataset import CLASS_NAMES            # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MAX_FILE_SIZE_BYTES   = 10 * 1024 * 1024  # 10 MB
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/jpg", "image/png"}
MLFLOW_TRACKING_URI   = os.environ.get("MLFLOW_TRACKING_URI", "http://mlflow:5000")
MODEL_NAME            = os.environ.get("MODEL_NAME", "chestscan-pneumonia-detector")
MODEL_ALIAS           = os.environ.get("MODEL_ALIAS", "champion")

# Shared val transform — loaded once at module import time.
# Defined in transforms.py which is shared with the training script,
# guaranteeing identical preprocessing between training and inference.
TRANSFORM = get_val_transforms()

# Internal class names used in MLflow logging (matching the training dataset index)
_INTERNAL_NAMES = ["NORMAL", "BACTERIA", "VIRUS"]


# ---------------------------------------------------------------------------
# Singleton model registry
# ---------------------------------------------------------------------------

class ModelRegistry:
    """Singleton that loads the champion model from MLflow once at startup.

    Loading once (not per request) avoids the ~2–5 second overhead of
    downloading model weights from the registry on every API call.

    Usage:
        registry = ModelRegistry.get_instance()
        logits = registry.model(input_tensor)
    """

    _instance: Optional["ModelRegistry"] = None
    _model = None
    _device: Optional[torch.device] = None
    _model_uri: Optional[str] = None
    _model_version: Optional[str] = None

    @classmethod
    def get_instance(cls) -> "ModelRegistry":
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._load()
        return cls._instance

    def _load(self) -> None:
        """Load the @champion model from the MLflow Model Registry."""
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        self._model_uri = f"models:/{MODEL_NAME}@{MODEL_ALIAS}"

        logger.info(f"Loading model from registry: {self._model_uri}")
        self._model = mlflow.pytorch.load_model(self._model_uri)
        self._model.eval()

        # Select best available compute device
        if torch.cuda.is_available():
            self._device = torch.device("cuda")
        elif torch.backends.mps.is_available():
            self._device = torch.device("mps")
        else:
            self._device = torch.device("cpu")

        self._model = self._model.to(self._device)
        logger.info(f"Model loaded on {self._device}")

    @property
    def model(self):
        return self._model

    @property
    def device(self) -> torch.device:
        return self._device

    @property
    def model_uri(self) -> str:
        return self._model_uri or "unknown"


# ---------------------------------------------------------------------------
# Grad-CAM helpers (inline to avoid import issues if gradcam_utils not present)
# ---------------------------------------------------------------------------

def _davit_reshape_transform(tensor: torch.Tensor, height: int = 14, width: int = 14):
    """Reshape ViT token sequence to 2D spatial feature map for Grad-CAM."""
    result = tensor[:, 1:, :]  # drop CLS token: (B, 196, d_model)
    result = result.reshape(result.size(0), height, width, result.size(-1))
    result = result.permute(0, 3, 1, 2)  # (B, d_model, H, W)
    return result


def _generate_gradcam_overlay(
    model,
    pil_image: Image.Image,
    device: torch.device,
) -> bytes:
    """Generate a three-panel Grad-CAM figure and return as PNG bytes.

    Returns:
        PNG image bytes (original | heatmap | overlay).
    """
    import matplotlib.cm as mpl_cm

    try:
        from pytorch_grad_cam import GradCAM
        from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
        grad_cam_available = True
    except ImportError:
        grad_cam_available = False

    original_array = np.array(pil_image.resize((224, 224)))
    input_tensor   = TRANSFORM(pil_image).unsqueeze(0).to(device)

    # Get prediction
    with torch.no_grad():
        logits    = model(input_tensor)
        probs     = torch.softmax(logits, dim=1)
        pred_idx  = int(probs.argmax(dim=1).item())
        confidence = float(probs[0, pred_idx].item())

    if grad_cam_available:
        target_layer = model.transformer.layers[-1].norm1
        targets = [ClassifierOutputTarget(pred_idx)]
        with GradCAM(
            model=model,
            target_layers=[target_layer],
            reshape_transform=_davit_reshape_transform,
        ) as cam_obj:
            grayscale = cam_obj(input_tensor=input_tensor, targets=targets)[0]
        heatmap = (mpl_cm.jet(grayscale)[:, :, :3] * 255).astype(np.uint8)
        overlay = (0.45 * heatmap + 0.55 * original_array).astype(np.uint8)
    else:
        # Fallback: return original image three times if grad-cam not installed
        heatmap = original_array.copy()
        overlay = original_array.copy()

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    titles = ["Original", "Grad-CAM", "Overlay"]
    for ax, img, title in zip(axes, [original_array, heatmap, overlay], titles):
        ax.imshow(img)
        ax.set_title(title, fontsize=11)
        ax.axis("off")

    pred_name = CLASS_NAMES[pred_idx]
    plt.suptitle(f"Prediction: {pred_name} (confidence={confidence:.1%})", fontsize=13)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return buf.read()


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str
    model_version: str
    device: str


class PredictionResponse(BaseModel):
    diagnosis: str
    confidence: float
    probabilities: dict
    model_version: str


# ---------------------------------------------------------------------------
# Lifespan (FastAPI >= 0.93 startup/shutdown pattern)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the model on startup; nothing to clean up on shutdown."""
    logger.info("Application startup: loading model from MLflow registry...")
    try:
        registry = ModelRegistry.get_instance()
        logger.info(f"Model ready.  URI: {registry.model_uri}  Device: {registry.device}")
    except Exception as exc:
        logger.error(f"Failed to load model at startup: {exc}")
        raise
    yield
    # Shutdown: nothing to release for a stateless inference server
    logger.info("Application shutdown.")


app = FastAPI(
    title="ChestScan API",
    description=(
        "Decision support API for chest X-ray pneumonia classification. "
        "Not a substitute for professional medical diagnosis. "
        "All results must be reviewed by a qualified radiologist."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _validate_upload(file: UploadFile) -> None:
    content_type = (file.content_type or "").lower()
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: {content_type!r}. Accepted: JPEG, PNG.",
        )


async def _read_image(file: UploadFile) -> Image.Image:
    raw = await file.read()
    if len(raw) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds 10 MB limit. Received {len(raw) / 1e6:.1f} MB.",
        )
    try:
        return Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cannot decode image: {exc}",
        )


def _log_prediction(prediction_id: str, predicted_class: str, confidence: float, probs: dict) -> None:
    """Log a production prediction to MLflow for downstream drift monitoring.

    Errors are swallowed — prediction logging must never block the API response.
    """
    try:
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        exp = mlflow.set_experiment("production-predictions")
        with mlflow.start_run(
            experiment_id=exp.experiment_id,
            run_name=f"predict-{prediction_id[:8]}",
            tags={"context": "production", "prediction_id": prediction_id},
        ):
            mlflow.log_params({
                "predicted_class": predicted_class,
                "prediction_id":   prediction_id,
            })
            mlflow.log_metrics({
                "confidence":    confidence,
                "prob_normal":   probs.get("NORMAL",   0.0),
                "prob_bacteria": probs.get("BACTERIA",  0.0),
                "prob_virus":    probs.get("VIRUS",    0.0),
            })
    except Exception as exc:
        logger.warning(f"Failed to log prediction to MLflow: {exc}")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint for Docker HEALTHCHECK and load balancer probes."""
    try:
        registry = ModelRegistry.get_instance()
        return HealthResponse(
            status="healthy",
            model_version=registry.model_uri,
            device=str(registry.device),
        )
    except Exception:
        return HealthResponse(
            status="unhealthy",
            model_version="unknown",
            device="unknown",
        )


@app.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    """Classify a chest X-ray image.

    Accepts a JPEG or PNG chest X-ray (max 10 MB).
    Returns the predicted class, confidence, and all class probabilities.
    Each prediction is logged to MLflow for production monitoring.
    """
    _validate_upload(file)
    pil_image = await _read_image(file)

    registry     = ModelRegistry.get_instance()
    model        = registry.model
    device       = registry.device
    model_uri    = registry.model_uri

    input_tensor = TRANSFORM(pil_image).unsqueeze(0).to(device)

    with torch.no_grad():
        logits  = model(input_tensor)
        probs   = torch.softmax(logits, dim=1).squeeze(0).cpu().numpy()

    pred_idx     = int(probs.argmax())
    pred_class   = _INTERNAL_NAMES[pred_idx]
    confidence   = float(probs[pred_idx])
    # Map internal names to display names for the response
    probs_dict   = {_INTERNAL_NAMES[i]: float(probs[i]) for i in range(len(_INTERNAL_NAMES))}
    prediction_id = str(uuid.uuid4())

    # Log to MLflow for monitoring (non-blocking)
    _log_prediction(prediction_id, pred_class, confidence, probs_dict)

    logger.info(f"[{prediction_id[:8]}] {pred_class} (confidence={confidence:.3f})")

    return PredictionResponse(
        diagnosis=CLASS_NAMES[pred_idx],
        confidence=confidence,
        probabilities=probs_dict,
        model_version=model_uri,
    )


@app.post("/explain")
async def explain(file: UploadFile = File(...)):
    """Generate a Grad-CAM explainability heatmap for a chest X-ray.

    Returns a PNG image (StreamingResponse) containing a three-panel figure:
    original X-ray | Grad-CAM heatmap | overlay.

    The heatmap highlights regions of the image that most influenced the
    model's prediction.  Clinically plausible heatmaps should highlight
    areas of opacity or consolidation within the lung fields.
    """
    _validate_upload(file)
    pil_image = await _read_image(file)

    registry = ModelRegistry.get_instance()
    model    = registry.model
    device   = registry.device

    try:
        png_bytes = _generate_gradcam_overlay(model, pil_image, device)
    except Exception as exc:
        logger.error(f"Grad-CAM generation failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Explanation generation failed: {exc}",
        )

    return StreamingResponse(io.BytesIO(png_bytes), media_type="image/png")
