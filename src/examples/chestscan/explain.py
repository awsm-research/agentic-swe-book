# explain.py
# Grad-CAM explainability script for the ChestScan pneumonia detector.
#
# Loads a trained model from MLflow by run_id, generates Grad-CAM heatmaps
# for representative test images, and logs them as MLflow artefacts.
#
# Usage:
#   python explain.py --run-id <RUN_ID> --data-root ./chest_xray
#   python explain.py --run-id <RUN_ID> --data-root ./chest_xray --n-samples 6

import argparse
import random
from typing import Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import mlflow
import mlflow.pytorch
import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget

from dataset import CLASS_NAMES, ChestXRayDataset
from transforms import get_val_transforms

# Internal short names matching class indices 0, 1, 2
_INTERNAL_NAMES = ["NORMAL", "BACTERIA", "VIRUS"]


# ---------------------------------------------------------------------------
# Grad-CAM helpers
# ---------------------------------------------------------------------------

def davit_reshape_transform(tensor: torch.Tensor, height: int = 14, width: int = 14):
    """Reshape ViT token sequence to 2D spatial feature map for Grad-CAM.

    The DAViT transformer output has shape (B, 197, d_model):
      token[0]   = CLS token (global summary — not spatially localised)
      token[1:]  = 196 spatial patch tokens arranged as a 14×14 grid

    pytorch-grad-cam expects activations of shape (B, C, H, W).
    We discard the CLS token and reshape the remaining 196 tokens.

    Args:
        tensor: transformer output, shape (B, 197, d_model).
        height: spatial height of the patch grid (default 14 for 224×224 input).
        width:  spatial width of the patch grid (default 14 for 224×224 input).

    Returns:
        Reshaped tensor of shape (B, d_model, height, width).
    """
    result = tensor[:, 1:, :]                                     # drop CLS: (B, 196, d_model)
    result = result.reshape(result.size(0), height, width, result.size(-1))  # (B, 14, 14, d_model)
    result = result.permute(0, 3, 1, 2)                           # (B, d_model, 14, 14)
    return result


def get_gradcam_target_layer(model: nn.Module) -> nn.Module:
    """Return the target layer for Grad-CAM in DAViT.

    We target the LayerNorm (norm1) of the last transformer encoder layer.
    This is the final spatial representation before the classification head
    and produces the most semantically meaningful heatmaps.
    """
    return model.transformer.layers[-1].norm1


def generate_gradcam(
    model: nn.Module,
    image_path: str,
    target_class: Optional[int] = None,
    device: Optional[torch.device] = None,
) -> Tuple[np.ndarray, np.ndarray, int, float]:
    """Generate a Grad-CAM heatmap for a single X-ray image.

    Args:
        model:        trained DAViT model (eval mode).
        image_path:   path to the input chest X-ray image.
        target_class: class index to explain. If None, uses the predicted class.
        device:       compute device. Defaults to CPU.

    Returns:
        Tuple of:
          - original_array: uint8 RGB image, shape (224, 224, 3).
          - heatmap_array:  uint8 RGB jet-colourmap heatmap, shape (224, 224, 3).
          - predicted_class: predicted class index (int).
          - confidence: predicted class probability (float in [0, 1]).
    """
    if device is None:
        device = torch.device("cpu")

    model.eval()
    model.to(device)

    transform = get_val_transforms()
    pil_image = Image.open(image_path).convert("RGB")
    original_array = np.array(pil_image.resize((224, 224)))
    input_tensor = transform(pil_image).unsqueeze(0).to(device)

    # Get prediction
    with torch.no_grad():
        logits = model(input_tensor)
        probs = torch.softmax(logits, dim=1)
        pred_class = int(probs.argmax(dim=1).item())
        confidence = float(probs[0, pred_class].item())

    if target_class is None:
        target_class = pred_class

    # Grad-CAM with reshape transform for ViT spatial tokens
    target_layer = get_gradcam_target_layer(model)
    targets = [ClassifierOutputTarget(target_class)]

    with GradCAM(
        model=model,
        target_layers=[target_layer],
        reshape_transform=davit_reshape_transform,
    ) as cam_obj:
        grayscale_cam = cam_obj(input_tensor=input_tensor, targets=targets)
        grayscale_cam = grayscale_cam[0]  # (H, W), values in [0, 1]

    # Convert to RGB heatmap using the jet colormap
    heatmap_array = (cm.jet(grayscale_cam)[:, :, :3] * 255).astype(np.uint8)

    return original_array, heatmap_array, pred_class, confidence


def overlay_heatmap(
    original: np.ndarray,
    heatmap: np.ndarray,
    alpha: float = 0.5,
) -> np.ndarray:
    """Blend the Grad-CAM heatmap over the original image.

    Args:
        original: uint8 RGB image array.
        heatmap:  uint8 RGB heatmap array (same shape as original).
        alpha:    heatmap opacity (0 = image only, 1 = heatmap only).

    Returns:
        Blended uint8 RGB image.
    """
    return (alpha * heatmap + (1 - alpha) * original).astype(np.uint8)


def plot_gradcam_panel(
    original: np.ndarray,
    heatmap: np.ndarray,
    pred_class: int,
    confidence: float,
    save_path: str,
    true_class: Optional[int] = None,
) -> plt.Figure:
    """Create a three-panel figure: original image | Grad-CAM heatmap | overlay.

    Args:
        original:   uint8 RGB original image array.
        heatmap:    uint8 RGB heatmap array.
        pred_class: predicted class index.
        confidence: prediction confidence in [0, 1].
        save_path:  path to save the PNG figure.
        true_class: true class index (optional — if provided, adds CORRECT/INCORRECT label).

    Returns:
        The matplotlib Figure (for use with mlflow.log_figure).
    """
    overlay = overlay_heatmap(original, heatmap)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    titles = ["Original X-Ray", "Grad-CAM Heatmap", "Overlay"]
    images = [original, heatmap, overlay]

    for ax, img, title in zip(axes, images, titles):
        ax.imshow(img)
        ax.set_title(title, fontsize=12)
        ax.axis("off")

    pred_name = CLASS_NAMES[pred_class]
    sup_title = f"Prediction: {pred_name} (confidence={confidence:.1%})"

    if true_class is not None:
        true_name = CLASS_NAMES[true_class]
        status = "CORRECT" if true_class == pred_class else "INCORRECT"
        sup_title += f" | True: {true_name} [{status}]"

    plt.suptitle(sup_title, fontsize=13, y=1.02)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")

    return fig


# ---------------------------------------------------------------------------
# Batch Grad-CAM for MLflow logging
# ---------------------------------------------------------------------------

def generate_and_log_gradcam_samples(
    model: nn.Module,
    test_ds: ChestXRayDataset,
    n_samples: int = 6,
    device: Optional[torch.device] = None,
) -> None:
    """Generate Grad-CAM heatmaps for representative test images and log to MLflow.

    Selects approximately equal samples from each class.
    Logs each panel as both a file artefact and a figure directly via mlflow.log_figure.

    Args:
        model:     trained DAViT model.
        test_ds:   ChestXRayDataset for the test split.
        n_samples: total number of samples to generate (divided equally among classes).
        device:    compute device.
    """
    if device is None:
        device = torch.device("cpu")

    # Collect samples per class
    class_samples = {i: [] for i in range(len(_INTERNAL_NAMES))}
    for img_path, label in test_ds.samples:
        class_samples[label].append((str(img_path), label))

    selected = []
    per_class = max(n_samples // len(_INTERNAL_NAMES), 1)
    for cls_idx, samples in class_samples.items():
        selected.extend(random.sample(samples, min(per_class, len(samples))))

    print(f"Generating Grad-CAM for {len(selected)} test images...")
    for i, (img_path, true_label) in enumerate(selected):
        original, heatmap, pred_class, confidence = generate_gradcam(
            model, img_path, device=device
        )
        save_path = f"/tmp/gradcam_sample_{i:02d}.png"
        fig = plot_gradcam_panel(
            original, heatmap, pred_class, confidence, save_path, true_label
        )

        # Log as file artefact (for download from MLflow UI)
        mlflow.log_artifact(save_path, artifact_path="gradcam")

        # Log as figure (renders inline in MLflow UI)
        mlflow.log_figure(fig, f"gradcam/gradcam_sample_{i:02d}.png")
        plt.close(fig)

    print(f"Logged {len(selected)} Grad-CAM panels to MLflow artefact store.")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate Grad-CAM explainability heatmaps for ChestScan"
    )
    parser.add_argument(
        "--run-id",
        required=True,
        help="MLflow run_id of the model to explain",
    )
    parser.add_argument(
        "--data-root",
        default="./chest_xray",
        help="Path to chest_xray dataset directory",
    )
    parser.add_argument(
        "--n-samples",
        type=int,
        default=6,
        help="Number of test images to explain (2 per class by default)",
    )
    parser.add_argument(
        "--mlflow-uri",
        default="http://localhost:5000",
        help="MLflow tracking server URI",
    )
    args = parser.parse_args()

    mlflow.set_tracking_uri(args.mlflow_uri)

    print(f"Loading model from run: {args.run_id}")
    model = mlflow.pytorch.load_model(f"runs:/{args.run_id}/model")
    model.eval()

    device = (
        torch.device("cuda") if torch.cuda.is_available()
        else torch.device("mps") if torch.backends.mps.is_available()
        else torch.device("cpu")
    )
    model = model.to(device)

    test_ds = ChestXRayDataset(
        f"{args.data_root}/test",
        transform=get_val_transforms(),
    )

    # Log heatmaps back to the original training run
    with mlflow.start_run(run_id=args.run_id):
        generate_and_log_gradcam_samples(
            model, test_ds, n_samples=args.n_samples, device=device
        )

    print("Done. Heatmaps logged to MLflow.")
