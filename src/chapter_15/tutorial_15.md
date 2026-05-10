## 15.13 Tutorial: Evaluating, Explaining, and Registering ChestScan

The ResNet-18 baseline from Tutorial 13 achieved roughly 91% accuracy. Before your team promotes it to production, the clinical director has asked two questions: "Is it actually catching sick patients?" and "Can you show me what the model is looking at in the X-ray?" Your job is to answer both questions with rigorous clinical evaluation and Grad-CAM visualisations — then register the approved model in the MLflow Model Registry with a governance artefact so the team knows exactly which version is in production and why it was approved.

**Concepts covered:** Sensitivity, specificity, AUC-ROC, F1, slice-based evaluation, Grad-CAM for CNN, MLflow Model Registry, model aliases, evaluation gate, model card

**Format:** Individual or pairs | **Duration:** ~2 hours | **Tool:** Python · PyTorch · pytorch-grad-cam · scikit-learn · MLflow · matplotlib · PyYAML

---

### Outline

- [Part A: Clinical Evaluation and Explainability](#part-a-clinical-evaluation-and-explainability) *(~60 min)*
- [Part B: Registry and Governance](#part-b-registry-and-governance) *(~60 min)*

---

### Learning Objectives

By the end of this tutorial, you will be able to:

1. Load a trained model from MLflow by `run_id` and evaluate it with clinical metrics: sensitivity, specificity, AUC-ROC, and per-class F1.
2. Perform slice-based evaluation to detect performance disparities across pneumonia sub-types.
3. Apply Grad-CAM to generate visual explanations that highlight the image regions driving each prediction.
4. Write an evaluation gate script that automatically enforces clinical performance thresholds.
5. Register a model version in the MLflow Model Registry and assign lifecycle aliases.
6. Attach a YAML model card as a governance artefact linked to the registered model version.

---

### Prerequisites

- Tutorial 13 completed: MLflow server running, `chest-xray-pneumonia` experiment exists, and you have noted the best run's `run_id`
- `dataset.py` from Tutorial 13 is present in the working directory

Install additional dependencies:

```bash
pip install grad-cam pyyaml
```

Verify:

```bash
python -c "from pytorch_grad_cam import GradCAM; print('grad-cam OK')"
python -c "import yaml; print('pyyaml OK')"
```

Set the tracking URI if you opened a new terminal:

```bash
export MLFLOW_TRACKING_URI=http://localhost:5000
```

---

### Part A: Clinical Evaluation and Explainability

*(~60 min)*

#### Step 1: Write `evaluate.py`

Save the following as `evaluate.py`:

```python
# evaluate.py
"""
Load the best model from MLflow by run_id and compute clinical evaluation metrics.
Logs all metrics and artefacts to a new MLflow run in the same experiment.
"""

import argparse
import io
import json

import matplotlib.pyplot as plt
import mlflow
import mlflow.pytorch
import numpy as np
import torch
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    auc,
    classification_report,
    confusion_matrix,
    f1_score,
    roc_auc_score,
    roc_curve,
)

from dataset import build_dataloaders

CLASS_NAMES = ["Normal", "Bacterial Pneumonia", "Viral Pneumonia"]
DATA_ROOT = "data/chest_xray"


def load_model_from_run(run_id: str, device: torch.device) -> torch.nn.Module:
    model_uri = f"runs:/{run_id}/model"
    model = mlflow.pytorch.load_model(model_uri, map_location=device)
    model.eval()
    return model


def collect_predictions(
    model: torch.nn.Module, loader, device: torch.device
) -> tuple[list[int], np.ndarray]:
    """Return (true_labels, softmax_probabilities)."""
    all_labels, all_probs = [], []
    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device)
            logits = model(images)
            probs = torch.softmax(logits, dim=1).cpu().numpy()
            all_labels.extend(labels.tolist())
            all_probs.append(probs)
    return all_labels, np.vstack(all_probs)


def compute_sensitivity_specificity(
    labels: list[int], preds: list[int], pneumonia_class_ids: list[int]
) -> tuple[float, float]:
    """
    Sensitivity = TP / (TP + FN) for any pneumonia label.
    Specificity = TN / (TN + FP) — normal cases correctly identified as normal.
    """
    binary_true = [1 if l in pneumonia_class_ids else 0 for l in labels]
    binary_pred = [1 if p in pneumonia_class_ids else 0 for p in preds]

    tp = sum(t == 1 and p == 1 for t, p in zip(binary_true, binary_pred))
    fn = sum(t == 1 and p == 0 for t, p in zip(binary_true, binary_pred))
    tn = sum(t == 0 and p == 0 for t, p in zip(binary_true, binary_pred))
    fp = sum(t == 0 and p == 1 for t, p in zip(binary_true, binary_pred))

    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    return sensitivity, specificity


def plot_roc_curve(labels: list[int], probs: np.ndarray) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7, 6))
    for i, name in enumerate(CLASS_NAMES):
        binary = [1 if l == i else 0 for l in labels]
        fpr, tpr, _ = roc_curve(binary, probs[:, i])
        roc_auc = auc(fpr, tpr)
        ax.plot(fpr, tpr, label=f"{name} (AUC={roc_auc:.3f})")
    ax.plot([0, 1], [0, 1], "k--", linewidth=0.8)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curves — One-vs-Rest")
    ax.legend(loc="lower right")
    plt.tight_layout()
    return fig


def evaluate(run_id: str) -> dict:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    _, _, test_loader = build_dataloaders(DATA_ROOT, batch_size=64)

    model = load_model_from_run(run_id, device)
    labels, probs = collect_predictions(model, test_loader, device)
    preds = probs.argmax(axis=1).tolist()

    # --- Core metrics ---
    sensitivity, specificity = compute_sensitivity_specificity(
        labels, preds, pneumonia_class_ids=[1, 2]
    )
    macro_auc = roc_auc_score(labels, probs, multi_class="ovr", average="macro")
    f1_per_class = f1_score(labels, preds, average=None).tolist()
    report = classification_report(labels, preds, target_names=CLASS_NAMES)

    # --- Slice: bacterial vs viral (exclude normal samples) ---
    bact_idx = [i for i, l in enumerate(labels) if l in (1, 2)]
    bact_labels = [labels[i] for i in bact_idx]
    bact_preds = [preds[i] for i in bact_idx]
    bact_f1 = f1_score(bact_labels, bact_preds, labels=[1, 2],
                       average="macro", zero_division=0)

    metrics = {
        "test_sensitivity": sensitivity,
        "test_specificity": specificity,
        "test_macro_auc": macro_auc,
        "test_f1_normal": f1_per_class[0],
        "test_f1_bacterial": f1_per_class[1],
        "test_f1_viral": f1_per_class[2],
        "test_f1_pneumonia_slice": bact_f1,
    }

    print("\n=== Evaluation Results ===")
    for k, v in metrics.items():
        print(f"  {k}: {v:.4f}")
    print("\nClassification Report:")
    print(report)

    mlflow.set_experiment("chest-xray-pneumonia")
    with mlflow.start_run(run_name=f"eval-{run_id[:8]}") as eval_run:
        mlflow.log_param("evaluated_run_id", run_id)
        mlflow.log_metrics(metrics)
        mlflow.log_text(report, "classification_report.txt")

        roc_fig = plot_roc_curve(labels, probs)
        mlflow.log_figure(roc_fig, "roc_curves.png")
        plt.close(roc_fig)

        # Confusion matrix
        cm = confusion_matrix(labels, preds)
        fig, ax = plt.subplots(figsize=(6, 5))
        ConfusionMatrixDisplay(cm, display_labels=CLASS_NAMES).plot(
            ax=ax, colorbar=False
        )
        ax.set_title("Test Set Confusion Matrix")
        plt.tight_layout()
        mlflow.log_figure(fig, "test_confusion_matrix.png")
        plt.close(fig)

        eval_run_id = eval_run.info.run_id
        print(f"\nEvaluation run_id: {eval_run_id}")

    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True, help="Training run_id from Tutorial 13")
    args = parser.parse_args()
    evaluate(args.run_id)
```

#### Step 2: Run the evaluation

Replace `<RUN_ID>` with the value you copied at the end of Tutorial 13:

```bash
python evaluate.py --run-id <RUN_ID>
```

> **Why is 91% accuracy not enough?** In medical diagnosis, a classifier that achieves 91% accuracy by predicting "Pneumonia" for every image would still miss all normal cases. The critical metric is **sensitivity**: if the model misses 30% of sick patients, it cannot be deployed in a clinical screening role regardless of overall accuracy. Check whether `test_sensitivity` is above 0.90 before proceeding.

#### Step 3: Generate Grad-CAM explanations

Install the library if you have not already:

```bash
pip install grad-cam
```

Save the following as `explain.py`:

```python
# explain.py
"""
Generate Grad-CAM heatmaps for 6 sample X-rays (2 per class) and log the
overlay grid to MLflow as an artefact.
"""

import argparse
import random

import matplotlib.pyplot as plt
import mlflow
import mlflow.pytorch
import numpy as np
import torch
from PIL import Image
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget

from dataset import ChestXRayDataset, get_transforms

CLASS_NAMES = ["Normal", "Bacterial", "Viral"]
DATA_ROOT = "data/chest_xray"
SAMPLES_PER_CLASS = 2


def load_model(run_id: str, device: torch.device) -> torch.nn.Module:
    model = mlflow.pytorch.load_model(f"runs:/{run_id}/model", map_location=device)
    model.eval()
    return model


def get_sample_paths(n_per_class: int = SAMPLES_PER_CLASS) -> list[tuple]:
    """Return (path, label) tuples, n_per_class samples per label."""
    ds = ChestXRayDataset(DATA_ROOT, split="test")
    by_class: dict[int, list] = {0: [], 1: [], 2: []}
    for path, label in ds.samples:
        by_class[label].append((path, label))
    samples = []
    for label, items in by_class.items():
        samples.extend(random.sample(items, min(n_per_class, len(items))))
    return samples


def generate_explanations(run_id: str) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model(run_id, device)

    # For ResNet-18, the last conv layer is layer4[-1]
    target_layers = [model.layer4[-1]]
    cam = GradCAM(model=model, target_layers=target_layers)

    val_transform = get_transforms("val")
    samples = get_sample_paths()

    n = len(samples)
    fig, axes = plt.subplots(n, 2, figsize=(8, n * 3))
    fig.suptitle("Grad-CAM Explanations — Test Set Samples", fontsize=13)

    for row, (img_path, true_label) in enumerate(samples):
        # Load raw image for overlay
        raw = np.array(Image.open(img_path).convert("RGB").resize((224, 224))) / 255.0
        raw = raw.astype(np.float32)

        # Prepare tensor
        tensor = val_transform(Image.open(img_path).convert("RGB")).unsqueeze(0)
        tensor = tensor.to(device)

        with torch.no_grad():
            logits = model(tensor)
            pred_label = logits.argmax(dim=1).item()
            confidence = torch.softmax(logits, dim=1)[0, pred_label].item()

        # Grad-CAM for predicted class
        grayscale_cam = cam(
            input_tensor=tensor,
            targets=[ClassifierOutputTarget(pred_label)],
        )[0]
        overlay = show_cam_on_image(raw, grayscale_cam, use_rgb=True)

        axes[row, 0].imshow(raw)
        axes[row, 0].set_title(f"True: {CLASS_NAMES[true_label]}", fontsize=9)
        axes[row, 0].axis("off")

        axes[row, 1].imshow(overlay)
        axes[row, 1].set_title(
            f"Pred: {CLASS_NAMES[pred_label]} ({confidence:.0%})", fontsize=9
        )
        axes[row, 1].axis("off")

    plt.tight_layout()

    mlflow.set_experiment("chest-xray-pneumonia")
    with mlflow.start_run(run_name=f"gradcam-{run_id[:8]}"):
        mlflow.log_param("explained_run_id", run_id)
        mlflow.log_figure(fig, "gradcam_explanations.png")
        print("Grad-CAM artefact logged to MLflow.")

    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    generate_explanations(args.run_id)
```

```bash
python explain.py --run-id <RUN_ID>
```

#### Step 4: View heatmaps in the MLflow UI

1. Go to [http://localhost:5000](http://localhost:5000)
2. Select the `gradcam-<run_id[:8]>` run
3. Click **Artifacts** → `gradcam_explanations.png`

The left column shows the original X-ray; the right column overlays the Grad-CAM heatmap. For pneumonia cases, the model should highlight diffuse opacities in the lung fields. If it highlights image borders or labels, that is a spurious-correlation warning worth documenting.

#### Step 5: Write and run the evaluation gate

Save as `gate.py`:

```python
# gate.py
"""
Evaluation gate: reads metrics from MLflow and exits with code 1 if thresholds
are not met. Intended for use in CI/CD pipelines.

Thresholds (clinical minimums for a screening tool):
  AUC    >= 0.92
  Sensitivity >= 0.90
"""

import argparse
import sys

import mlflow
from mlflow.tracking import MlflowClient

AUC_THRESHOLD = 0.92
SENSITIVITY_THRESHOLD = 0.90


def run_gate(run_id: str) -> bool:
    client = MlflowClient()
    # Search for the evaluation run that references this training run
    experiment = client.get_experiment_by_name("chest-xray-pneumonia")
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        filter_string=f"params.evaluated_run_id = '{run_id}'",
        order_by=["start_time DESC"],
        max_results=1,
    )

    if not runs:
        print(f"ERROR: No evaluation run found for training run_id={run_id}")
        print("Run evaluate.py first.")
        sys.exit(1)

    eval_run = runs[0]
    metrics = eval_run.data.metrics
    auc_val = metrics.get("test_macro_auc", 0.0)
    sensitivity = metrics.get("test_sensitivity", 0.0)

    print(f"Evaluation run: {eval_run.info.run_id}")
    print(f"  test_macro_auc   = {auc_val:.4f}  (threshold >= {AUC_THRESHOLD})")
    print(f"  test_sensitivity = {sensitivity:.4f}  (threshold >= {SENSITIVITY_THRESHOLD})")

    passed = auc_val >= AUC_THRESHOLD and sensitivity >= SENSITIVITY_THRESHOLD
    status = "PASS" if passed else "FAIL"
    print(f"\nEvaluation gate: {status}")
    return passed


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True, help="Training run_id to evaluate")
    args = parser.parse_args()

    if not run_gate(args.run_id):
        sys.exit(1)
```

```bash
python gate.py --run-id <RUN_ID>
```

A passing gate prints `Evaluation gate: PASS` and exits with code 0. A failing gate exits with code 1, which stops any CI pipeline that invokes it.

---

### Part B: Registry and Governance

*(~60 min)*

#### Step 1: Register the model in the MLflow Model Registry

```python
# register_model.py
import argparse

import mlflow
from mlflow.tracking import MlflowClient

MODEL_NAME = "davit-pneumonia-detector"


def register(run_id: str) -> str:
    model_uri = f"runs:/{run_id}/model"
    result = mlflow.register_model(model_uri=model_uri, name=MODEL_NAME)
    version = result.version
    print(f"Registered {MODEL_NAME} version {version} from run {run_id}")
    return version


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    register(args.run_id)
```

```bash
python register_model.py --run-id <RUN_ID>
```

Note the version number printed (e.g., `1`). Open [http://localhost:5000/#/models](http://localhost:5000/#/models) and confirm the model appears under **Models**.

#### Step 2: Assign the `@staging` alias

```python
# set_alias.py
import argparse

from mlflow.tracking import MlflowClient

MODEL_NAME = "davit-pneumonia-detector"


def set_alias(version: str, alias: str) -> None:
    client = MlflowClient()
    client.set_registered_model_alias(
        name=MODEL_NAME,
        alias=alias,
        version=version,
    )
    print(f"Set alias @{alias} → {MODEL_NAME} version {version}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--alias", default="staging")
    args = parser.parse_args()
    set_alias(args.version, args.alias)
```

```bash
python set_alias.py --version 1 --alias staging
```

#### Step 3: Write the model card YAML

Save the following as `model_card.yaml`, completing the bracketed fields with your actual results:

```yaml
# model_card.yaml
model_name: davit-pneumonia-detector
model_version: "1"
created_date: "2025-05-10"
framework: PyTorch
architecture: ResNet-18 (pretrained ImageNet)

training_data:
  dataset: Kaggle Chest X-Ray Pneumonia
  source: https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia
  size: 5856 images
  classes:
    - label: 0
      name: Normal
    - label: 1
      name: Bacterial Pneumonia
    - label: 2
      name: Viral Pneumonia
  split: patient-level train/val/test
  preprocessing: Resize 224×224, ImageNet normalisation

evaluation_results:
  test_macro_auc: 0.0000        # replace with actual value
  test_sensitivity: 0.0000      # replace with actual value
  test_specificity: 0.0000      # replace with actual value
  test_f1_normal: 0.0000        # replace with actual value
  test_f1_bacterial: 0.0000     # replace with actual value
  test_f1_viral: 0.0000         # replace with actual value
  evaluation_set: test split (624 images)

intended_use:
  - Screening support for radiologists reviewing chest X-rays
  - Research and educational demonstrations
  - Triage prioritisation in high-volume radiology workflows

prohibited_use:
  - Autonomous diagnosis without radiologist review
  - Use in paediatric populations (training data is predominantly adult)
  - Deployment in regions with significantly different X-ray equipment calibration

known_limitations:
  - Model trained on one institution's data; may not generalise to different equipment
  - Viral vs bacterial distinction may require clinical context beyond imaging
  - Grad-CAM explanations are approximate and should not be used as sole clinical evidence

approvals:
  clinical_review: pending
  ethics_review: pending
  deployment_approval: pending
```

#### Step 4: Log the model card as a registered model artefact

```python
# log_model_card.py
import argparse

import mlflow
from mlflow.tracking import MlflowClient

MODEL_NAME = "davit-pneumonia-detector"


def log_card(version: str, card_path: str) -> None:
    client = MlflowClient()
    client.log_artifact_in_model_version(
        name=MODEL_NAME,
        version=version,
        local_path=card_path,
    )
    print(f"Logged {card_path} to {MODEL_NAME} version {version}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--card", default="model_card.yaml")
    args = parser.parse_args()
    log_card(args.version, args.card)
```

```bash
python log_model_card.py --version 1 --card model_card.yaml
```

> **Why attach the model card to the registry version?** MLflow Model Registry versions are immutable snapshots. Attaching the model card to the version, rather than to an experiment run, means anyone who loads `models:/davit-pneumonia-detector@champion` can also retrieve the approval record, limitations, and intended-use statement from the same source.

#### Step 5: Promote to `@champion`

Simulating human approval by reassigning the alias:

```bash
python set_alias.py --version 1 --alias champion
```

In a real workflow this step would be gated on a sign-off ticket in your issue tracker. The `@staging` alias remains assigned, allowing parallel deployments to staging and production environments to coexist.

#### Step 6: Verify the model loads from the `@champion` alias

```python
# verify_registry.py
import torch
import mlflow.pytorch

MODEL_URI = "models:/davit-pneumonia-detector@champion"

device = torch.device("cpu")
model = mlflow.pytorch.load_model(MODEL_URI, map_location=device)
model.eval()

dummy = torch.randn(1, 3, 224, 224)
with torch.no_grad():
    out = model(dummy)

print(f"Output shape : {out.shape}")   # expect torch.Size([1, 3])
print(f"Probabilities: {torch.softmax(out, dim=1).tolist()}")
print("Registry load verified.")
```

```bash
python verify_registry.py
```

Expected output:

```
Output shape : torch.Size([1, 3])
Probabilities: [[0.33..., 0.33..., 0.33...]]
Registry load verified.
```

The exact probabilities will differ — the important check is that `torch.Size([1, 3])` confirms the three-class output head is intact and the model URI resolved correctly.

---

### References

- [MLflow Model Registry documentation](https://mlflow.org/docs/latest/model-registry.html)
- [pytorch-grad-cam library](https://github.com/jacobgil/pytorch-grad-cam)
- [Selvaraju et al. — Grad-CAM: Visual Explanations from Deep Networks (ICCV 2017)](https://arxiv.org/abs/1610.02391)
- [scikit-learn — roc_auc_score multiclass](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html)
- [Model Cards for Model Reporting — Mitchell et al. (2019)](https://arxiv.org/abs/1810.03993)
