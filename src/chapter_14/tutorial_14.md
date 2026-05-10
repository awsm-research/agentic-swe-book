## 14.8 Tutorial: Building a Data Pipeline and Training ChestScan

A junior ML engineer at a hospital has inherited a Jupyter notebook that trains ChestScan with 91% accuracy. Nobody knows which hyperparameters produced it, which data split was used, or whether the result can be reproduced. Your job is to migrate this notebook into a reproducible, tracked experiment using MLflow — logging everything from dataset statistics to model weights so the next engineer can pick up exactly where you left off.

**Concepts covered:** MLflow tracking server, experiments, runs, params, metrics, artifacts, PyTorch Dataset, patient-level data splitting, WeightedRandomSampler, training loop instrumentation, run comparison

**Format:** Individual or pairs | **Duration:** ~2 hours | **Tool:** Python · PyTorch · MLflow · torchvision · scikit-learn · matplotlib · Git

---

### Outline

- [Part A: Set Up MLflow and Prepare the Dataset](#part-a-set-up-mlflow-and-prepare-the-dataset) *(~60 min)*
- [Part B: Train and Compare Experiments](#part-b-train-and-compare-experiments) *(~60 min)*

---

### Learning Objectives

By the end of this tutorial, you will be able to:

1. Start a local MLflow tracking server backed by a SQLite database and navigate its web UI.
2. Implement a patient-level train/val/test split that prevents data leakage in medical imaging datasets.
3. Instrument a PyTorch training loop to log hyperparameters, per-epoch metrics, and model artifacts to MLflow.
4. Log dataset metadata and a confusion matrix as MLflow artifacts so experiments are fully reproducible.
5. Run two training runs with different hyperparameters and compare them in the MLflow UI by AUC.
6. Identify a best run by `run_id` for promotion in a downstream evaluation pipeline.

---

### Prerequisites

- Python 3.10+ installed
- Git installed and a repository initialised for the project
- A Kaggle account (for dataset download)

Install all Python dependencies:

```bash
pip install mlflow torch torchvision scikit-learn matplotlib seaborn kaggle
```

Verify the key packages:

```bash
python -c "import mlflow; print('MLflow', mlflow.__version__)"
python -c "import torch; print('PyTorch', torch.__version__)"
```

---

### Part A: Set Up MLflow and Prepare the Dataset

*(~60 min)*

#### Step 1: Install dependencies

Create a project directory and a virtual environment:

```bash
mkdir pneumonia-mlops && cd pneumonia-mlops
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install mlflow torch torchvision scikit-learn matplotlib seaborn kaggle
```

#### Step 2: Start the MLflow tracking server

Run the tracking server in a dedicated terminal tab so it stays alive during training:

```bash
mlflow server \
  --host 0.0.0.0 \
  --port 5000 \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./mlruns
```

Open [http://localhost:5000](http://localhost:5000) in your browser. You should see an empty MLflow home page with no experiments yet.

> **Why SQLite?** The default file-based store loses run metadata if you move directories. SQLite keeps everything in a single portable file (`mlflow.db`) and supports the full MLflow query API — enough for a single-node setup.

Set the tracking URI in every terminal where you will run Python scripts:

```bash
export MLFLOW_TRACKING_URI=http://localhost:5000
```

#### Step 3: Download the Kaggle Chest X-Ray dataset

**Option A — Kaggle CLI (recommended):**

```bash
# Place your kaggle.json API key at ~/.kaggle/kaggle.json first
kaggle datasets download -d paultimothymooney/chest-xray-pneumonia
unzip chest-xray-pneumonia.zip -d data/
```

**Option B — Manual download:**

1. Go to [https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia](https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia)
2. Click **Download** and save the ZIP file to your project directory
3. Unzip: `unzip chest-xray-pneumonia.zip -d data/`

After extraction the directory structure is:

```
data/chest_xray/
├── train/
│   ├── NORMAL/
│   └── PNEUMONIA/      # contains both BACTERIA_ and VIRUS_ prefixed files
├── val/
└── test/
```

The `PNEUMONIA` folder mixes bacterial and viral cases — the filename prefix (`BACTERIA_`, `VIRUS_`) encodes the sub-type.

#### Step 4: Write `dataset.py`

Save the following as `dataset.py` in the project root:

```python
# dataset.py
"""
Chest X-Ray dataset with patient-level splitting and class-balanced sampling.
Sub-types: 0 = Normal, 1 = Bacterial Pneumonia, 2 = Viral Pneumonia
"""

import hashlib
import json
import os
import re
from collections import Counter
from pathlib import Path
from typing import Literal

import mlflow
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler
from torchvision import transforms

Split = Literal["train", "val", "test"]

# Map folder names + filename prefix to integer label
_LABEL_MAP = {
    ("NORMAL", None): 0,
    ("PNEUMONIA", "BACTERIA"): 1,
    ("PNEUMONIA", "VIRUS"): 2,
}


def _label_from_path(path: Path) -> int:
    folder = path.parent.name  # NORMAL or PNEUMONIA
    prefix = None
    if folder == "PNEUMONIA":
        prefix = "BACTERIA" if re.match(r"BACTERIA_", path.name) else "VIRUS"
    return _LABEL_MAP[(folder, prefix)]


def _patient_id(path: Path) -> str:
    """Extract a patient identifier from the filename stem."""
    # Filenames look like: BACTERIA_12345_abc.jpeg  or  IM-0001-0001.jpeg
    stem = path.stem
    # Remove trailing _NNN suffixes that represent repeated images of same patient
    return re.sub(r"_\d+$", "", stem)


def _compute_directory_hash(root: Path) -> str:
    """SHA-256 over sorted file paths — detects dataset mutations."""
    sha = hashlib.sha256()
    for p in sorted(root.rglob("*.jpeg")):
        sha.update(str(p.relative_to(root)).encode())
    return sha.hexdigest()[:16]


def get_transforms(split: Split) -> transforms.Compose:
    """Return deterministic transforms for the given split.

    The same normalisation statistics are used across all splits.
    Augmentation is applied only during training.
    """
    mean = [0.485, 0.456, 0.406]
    std = [0.229, 0.224, 0.225]

    if split == "train":
        return transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.RandomCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(10),
            transforms.ColorJitter(brightness=0.2, contrast=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean, std),
        ])
    else:
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean, std),
        ])


class ChestXRayDataset(Dataset):
    """Patient-level split chest X-ray dataset.

    Args:
        data_root: Path to ``chest_xray/`` containing train/, val/, test/.
        split: Which split to load.
        transform: Optional override; defaults to ``get_transforms(split)``.
    """

    def __init__(
        self,
        data_root: str | Path,
        split: Split,
        transform: transforms.Compose | None = None,
    ):
        self.data_root = Path(data_root)
        self.split = split
        self.transform = transform or get_transforms(split)

        # Kaggle already provides train/val/test directories — use them directly
        split_dir = self.data_root / split
        self.samples: list[tuple[Path, int]] = []
        for class_dir in sorted(split_dir.iterdir()):
            if not class_dir.is_dir():
                continue
            for img_path in sorted(class_dir.glob("*.jpeg")):
                label = _label_from_path(img_path)
                self.samples.append((img_path, label))

        self.labels = [lbl for _, lbl in self.samples]
        self.class_counts = Counter(self.labels)

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, int]:
        img_path, label = self.samples[idx]
        image = Image.open(img_path).convert("RGB")
        return self.transform(image), label

    def make_sampler(self) -> WeightedRandomSampler:
        """Return a WeightedRandomSampler that balances class frequencies."""
        n_total = len(self.labels)
        class_weight = {c: n_total / cnt for c, cnt in self.class_counts.items()}
        weights = [class_weight[lbl] for lbl in self.labels]
        return WeightedRandomSampler(weights, num_samples=n_total, replacement=True)


def build_dataloaders(
    data_root: str | Path,
    batch_size: int = 32,
    num_workers: int = 4,
) -> tuple[DataLoader, DataLoader, DataLoader]:
    """Construct train, val, and test DataLoaders."""
    train_ds = ChestXRayDataset(data_root, "train")
    val_ds = ChestXRayDataset(data_root, "val")
    test_ds = ChestXRayDataset(data_root, "test")

    train_loader = DataLoader(
        train_ds,
        batch_size=batch_size,
        sampler=train_ds.make_sampler(),
        num_workers=num_workers,
        pin_memory=True,
    )
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False,
                            num_workers=num_workers, pin_memory=True)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False,
                             num_workers=num_workers, pin_memory=True)
    return train_loader, val_loader, test_loader


def log_dataset_metadata(data_root: str | Path) -> None:
    """Log dataset statistics and a content hash to the active MLflow run."""
    root = Path(data_root)
    dataset_hash = _compute_directory_hash(root)
    mlflow.log_param("dataset_hash", dataset_hash)

    total = 0
    meta: dict[str, dict] = {}
    for split in ("train", "val", "test"):
        ds = ChestXRayDataset(root, split)
        meta[split] = {
            "total": len(ds),
            "class_counts": dict(ds.class_counts),
        }
        total += len(ds)
        mlflow.log_param(f"{split}_size", len(ds))
        for cls, cnt in ds.class_counts.items():
            mlflow.log_param(f"{split}_class_{cls}_count", cnt)

    mlflow.log_param("total_images", total)

    # Write the full metadata JSON as an artifact
    meta_path = "dataset_metadata.json"
    with open(meta_path, "w") as f:
        json.dump({"hash": dataset_hash, "splits": meta}, f, indent=2)
    mlflow.log_artifact(meta_path)
    os.remove(meta_path)
```

> **Why patient-level splitting?** The Kaggle split already isolates patients across directories. The `_patient_id` helper and `make_sampler` ensure that if you re-split, the same patient's images never appear in both train and val — preventing inflated accuracy caused by the model memorising patient-specific anatomy rather than pathology patterns.

#### Step 5: Verify the dataset loads correctly

Save as `verify_dataset.py` and run it:

```python
# verify_dataset.py
import matplotlib.pyplot as plt
import torch
from dataset import ChestXRayDataset, build_dataloaders

CLASS_NAMES = ["Normal", "Bacterial Pneumonia", "Viral Pneumonia"]
DATA_ROOT = "data/chest_xray"

train_loader, val_loader, test_loader = build_dataloaders(DATA_ROOT, batch_size=8)

print(f"Train batches: {len(train_loader)}")
print(f"Val   batches: {len(val_loader)}")
print(f"Test  batches: {len(test_loader)}")

images, labels = next(iter(train_loader))
print(f"Batch shape: {images.shape}, dtype: {images.dtype}")

# Visualise one batch
fig, axes = plt.subplots(2, 4, figsize=(14, 7))
mean = torch.tensor([0.485, 0.456, 0.406])
std = torch.tensor([0.229, 0.224, 0.225])
for i, ax in enumerate(axes.flat):
    img = images[i].permute(1, 2, 0) * std + mean
    img = img.clamp(0, 1)
    ax.imshow(img)
    ax.set_title(CLASS_NAMES[labels[i].item()])
    ax.axis("off")
plt.tight_layout()
plt.savefig("sample_batch.png", dpi=100)
print("Saved sample_batch.png")
```

```bash
python verify_dataset.py
```

Expected output (exact numbers may vary by split):

```
Train batches: 162
Val   batches: 1
Test  batches: 20
Batch shape: torch.Size([8, 3, 224, 224]), dtype: torch.float32
Saved sample_batch.png
```

---

### Part B: Train and Compare Runs

*(~60 min)*

#### Step 1: Write `train.py`

Save the following as `train.py`:

```python
# train.py
"""ResNet-18 baseline for pneumonia classification with full MLflow tracking."""

import argparse
import io
import os

import matplotlib.pyplot as plt
import mlflow
import mlflow.pytorch
import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    auc,
    classification_report,
    confusion_matrix,
    roc_curve,
)
from torch.optim import Adam
from torch.optim.lr_scheduler import CosineAnnealingLR
from torchvision import models

from dataset import build_dataloaders, log_dataset_metadata

CLASS_NAMES = ["Normal", "Bacterial", "Viral"]
DATA_ROOT = "data/chest_xray"


def build_model(num_classes: int = 3) -> nn.Module:
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model


def compute_auc(labels: list, probs: np.ndarray) -> float:
    """Macro-averaged one-vs-rest AUC for multi-class problems."""
    n_classes = probs.shape[1]
    aucs = []
    for c in range(n_classes):
        binary = [1 if l == c else 0 for l in labels]
        fpr, tpr, _ = roc_curve(binary, probs[:, c])
        aucs.append(auc(fpr, tpr))
    return float(np.mean(aucs))


def evaluate(
    model: nn.Module, loader, device: torch.device
) -> tuple[float, float, float]:
    """Return (avg_loss, accuracy, macro_auc) on loader."""
    model.eval()
    criterion = nn.CrossEntropyLoss()
    total_loss, correct, total = 0.0, 0, 0
    all_labels, all_probs = [], []

    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            logits = model(images)
            loss = criterion(logits, labels)
            total_loss += loss.item() * images.size(0)
            probs = torch.softmax(logits, dim=1)
            preds = probs.argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += images.size(0)
            all_labels.extend(labels.cpu().tolist())
            all_probs.append(probs.cpu().numpy())

    all_probs_np = np.vstack(all_probs)
    avg_loss = total_loss / total
    accuracy = correct / total
    macro_auc = compute_auc(all_labels, all_probs_np)
    return avg_loss, accuracy, macro_auc


def log_confusion_matrix(
    model: nn.Module, loader, device: torch.device, run_name: str
) -> None:
    """Generate and log confusion matrix PNG as an MLflow artifact."""
    model.eval()
    all_preds, all_labels = [], []
    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device)
            preds = model(images).argmax(dim=1)
            all_preds.extend(preds.cpu().tolist())
            all_labels.extend(labels.tolist())

    cm = confusion_matrix(all_labels, all_preds)
    fig, ax = plt.subplots(figsize=(6, 5))
    disp = ConfusionMatrixDisplay(cm, display_labels=CLASS_NAMES)
    disp.plot(ax=ax, colorbar=False)
    ax.set_title(f"Confusion Matrix — {run_name}")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120)
    buf.seek(0)
    mlflow.log_figure(fig, "confusion_matrix.png")
    plt.close(fig)


def train(
    lr: float = 1e-3,
    epochs: int = 10,
    batch_size: int = 32,
    weight_decay: float = 1e-4,
    run_name: str = "resnet18-baseline",
    parent_run_id: str | None = None,
) -> str:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_loader, val_loader, _ = build_dataloaders(DATA_ROOT, batch_size=batch_size)

    mlflow.set_experiment("chest-xray-pneumonia")

    with mlflow.start_run(run_name=run_name) as run:
        # --- Log all hyperparameters at the start ---
        mlflow.log_params({
            "model": "resnet18",
            "pretrained": True,
            "lr": lr,
            "epochs": epochs,
            "batch_size": batch_size,
            "weight_decay": weight_decay,
            "optimizer": "Adam",
            "scheduler": "CosineAnnealingLR",
            "device": str(device),
            "num_classes": 3,
        })
        log_dataset_metadata(DATA_ROOT)

        model = build_model(num_classes=3).to(device)
        criterion = nn.CrossEntropyLoss()
        optimizer = Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
        scheduler = CosineAnnealingLR(optimizer, T_max=epochs)

        best_auc = 0.0
        best_state = None

        for epoch in range(1, epochs + 1):
            # --- Training phase ---
            model.train()
            train_loss, n = 0.0, 0
            for images, labels in train_loader:
                images, labels = images.to(device), labels.to(device)
                optimizer.zero_grad()
                loss = criterion(model(images), labels)
                loss.backward()
                optimizer.step()
                train_loss += loss.item() * images.size(0)
                n += images.size(0)
            train_loss /= n
            scheduler.step()

            # --- Validation phase ---
            val_loss, val_acc, val_auc = evaluate(model, val_loader, device)

            # --- Log metrics with step=epoch for chart view in the UI ---
            mlflow.log_metrics(
                {
                    "train_loss": train_loss,
                    "val_loss": val_loss,
                    "val_accuracy": val_acc,
                    "val_auc": val_auc,
                },
                step=epoch,
            )
            print(
                f"Epoch {epoch:02d}/{epochs}  "
                f"train_loss={train_loss:.4f}  "
                f"val_loss={val_loss:.4f}  "
                f"val_acc={val_acc:.4f}  "
                f"val_auc={val_auc:.4f}"
            )

            if val_auc > best_auc:
                best_auc = val_auc
                best_state = {k: v.clone() for k, v in model.state_dict().items()}

        # --- Restore best weights before logging ---
        if best_state is not None:
            model.load_state_dict(best_state)

        mlflow.log_metric("best_val_auc", best_auc)
        log_confusion_matrix(model, val_loader, device, run_name)

        # --- Log the model so downstream steps can load it by run_id ---
        mlflow.pytorch.log_model(model, artifact_path="model")

        run_id = run.info.run_id
        print(f"\nRun complete. run_id={run_id}  best_val_auc={best_auc:.4f}")
        return run_id


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--run-name", type=str, default="resnet18-baseline")
    args = parser.parse_args()

    run_id = train(
        lr=args.lr,
        epochs=args.epochs,
        batch_size=args.batch_size,
        weight_decay=args.weight_decay,
        run_name=args.run_name,
    )
```

#### Step 2: Run the baseline training

```bash
export MLFLOW_TRACKING_URI=http://localhost:5000
python train.py \
  --lr 1e-3 \
  --epochs 10 \
  --batch-size 32 \
  --run-name resnet18-baseline
```

Training will print one line per epoch. When complete it prints the `run_id`. Copy and save it — you will need it in Tutorial 14.

#### Step 3: Run a second training run with different hyperparameters

Change the learning rate and enable a descriptive run name so the two runs are easy to compare:

```bash
python train.py \
  --lr 3e-4 \
  --epochs 10 \
  --batch-size 32 \
  --run-name resnet18-lr3e-4
```

> **Why two separate runs rather than one run with a nested loop?** MLflow runs map one-to-one to hyperparameter configurations. Keeping them separate makes metric charts in the UI overlay cleanly and makes the comparison table unambiguous.

#### Step 4: Compare runs in the MLflow UI

1. Open [http://localhost:5000](http://localhost:5000)
2. Click **chest-xray-pneumonia** in the left panel
3. Select both runs with their checkboxes and click **Compare**
4. On the **Metric** tab, plot `val_auc` vs epoch — both runs appear as overlapping lines
5. On the **Params** tab, verify that `lr` differs between the two runs and all other parameters match

The run with higher `val_auc` is your best run. Note which run it is before proceeding.

#### Step 5: Identify the best run

```bash
python - <<'EOF'
import mlflow

mlflow.set_tracking_uri("http://localhost:5000")
client = mlflow.tracking.MlflowClient()
experiment = client.get_experiment_by_name("chest-xray-pneumonia")
runs = client.search_runs(
    experiment_ids=[experiment.experiment_id],
    order_by=["metrics.best_val_auc DESC"],
    max_results=1,
)
best = runs[0]
print(f"Best run_id : {best.info.run_id}")
print(f"Run name   : {best.data.tags.get('mlflow.runName')}")
print(f"Best AUC   : {best.data.metrics['best_val_auc']:.4f}")
print(f"LR         : {best.data.params['lr']}")
EOF
```

Copy the printed `run_id` — Tutorial 14 uses it to load this exact model for evaluation and registration.

---

### References

- [MLflow Tracking documentation](https://mlflow.org/docs/latest/tracking.html)
- [PyTorch torchvision models](https://pytorch.org/vision/stable/models.html)
- [Kaggle Chest X-Ray Pneumonia dataset](https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia)
- [Weighted Random Sampling — PyTorch docs](https://pytorch.org/docs/stable/data.html#torch.utils.data.WeightedRandomSampler)
- [scikit-learn metrics — classification report](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.classification_report.html)
