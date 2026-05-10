# dataset.py
# PyTorch Dataset for the Kaggle Chest X-Ray Pneumonia dataset.
#
# Directory structure expected:
#   chest_xray/
#   ├── train/
#   │   ├── NORMAL/         (JPEG images)
#   │   └── PNEUMONIA/      (BACTERIA_* and VIRUS_* prefixed JPEG images)
#   ├── val/
#   │   ├── NORMAL/
#   │   └── PNEUMONIA/
#   └── test/
#       ├── NORMAL/
#       └── PNEUMONIA/

import os
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch
from PIL import Image
from torch.utils.data import ConcatDataset, DataLoader, Dataset, WeightedRandomSampler, random_split

import mlflow

# Three-class taxonomy used throughout the project
CLASS_NAMES = ["Normal", "Bacterial Pneumonia", "Viral Pneumonia"]

# Internal short keys used in the PNEUMONIA directory naming convention
_INTERNAL_NAMES = ["NORMAL", "BACTERIA", "VIRUS"]
_CLASS_TO_IDX = {name: idx for idx, name in enumerate(_INTERNAL_NAMES)}


class ChestXRayDataset(Dataset):
    """PyTorch Dataset for the Kaggle Chest X-Ray Pneumonia dataset.

    Maps the two-directory layout (NORMAL / PNEUMONIA) to three class labels:
        0 — Normal
        1 — Bacterial Pneumonia  (filenames containing 'BACTERIA')
        2 — Viral Pneumonia      (filenames containing 'VIRUS')

    Attributes:
        samples: List of (Path, int) tuples — (image_path, class_index).
    """

    def __init__(self, root_dir: str, transform=None):
        self.root_dir = Path(root_dir)
        self.transform = transform
        self.samples: List[Tuple[Path, int]] = []
        self._build_index()

    def _build_index(self) -> None:
        normal_dir = self.root_dir / "NORMAL"
        pneumonia_dir = self.root_dir / "PNEUMONIA"

        if normal_dir.exists():
            images = sorted(normal_dir.glob("*.jpeg")) + sorted(normal_dir.glob("*.jpg"))
            for p in images:
                self.samples.append((p, _CLASS_TO_IDX["NORMAL"]))

        if pneumonia_dir.exists():
            images = sorted(pneumonia_dir.glob("*.jpeg")) + sorted(pneumonia_dir.glob("*.jpg"))
            for p in images:
                fname = p.stem.upper()
                if "BACTERIA" in fname:
                    self.samples.append((p, _CLASS_TO_IDX["BACTERIA"]))
                elif "VIRUS" in fname:
                    self.samples.append((p, _CLASS_TO_IDX["VIRUS"]))
                else:
                    # Fallback: unknown PNEUMONIA files treated as bacterial
                    self.samples.append((p, _CLASS_TO_IDX["BACTERIA"]))

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        img_path, label = self.samples[idx]
        image = Image.open(img_path).convert("RGB")
        if self.transform is not None:
            image = self.transform(image)
        return image, label

    def compute_hash(self) -> str:
        """SHA-256 fingerprint of all sorted file paths.

        Use as a dataset version identifier — logs to MLflow to make every
        training run traceable to the exact dataset version it was trained on.
        """
        paths = sorted(str(p) for p, _ in self.samples)
        return hashlib.sha256("\n".join(paths).encode()).hexdigest()[:16]


def build_dataloaders(
    data_root: str,
    batch_size: int = 32,
    num_workers: int = 4,
) -> Dict[str, DataLoader]:
    """Build train/val/test DataLoaders with class-balanced sampling for training.

    Strategy:
      - Load the canonical Kaggle train/ and val/ directories.
      - Merge them into a ConcatDataset, then re-split 90/10 (train/val).
        This gives a larger, more stable validation set than Kaggle's 16-image val split.
      - Compute a WeightedRandomSampler from the post-merge train indices so the
        training loader over-samples minority classes (viral pneumonia) automatically.
      - The test/ directory is always held out and never merged.

    Args:
        data_root: path to the chest_xray root directory containing train/, val/, test/.
        batch_size: images per batch.
        num_workers: DataLoader worker processes.

    Returns:
        Dict with keys "train", "val", "test" mapping to DataLoader instances.
    """
    from transforms import get_train_transforms, get_val_transforms

    train_ds = ChestXRayDataset(
        os.path.join(data_root, "train"),
        transform=get_train_transforms(),
    )
    val_ds = ChestXRayDataset(
        os.path.join(data_root, "val"),
        transform=get_val_transforms(),
    )
    test_ds = ChestXRayDataset(
        os.path.join(data_root, "test"),
        transform=get_val_transforms(),
    )

    # Merge original train + val, then re-split 90/10
    combined = ConcatDataset([train_ds, val_ds])
    n_val = max(int(0.10 * len(combined)), 1)
    n_train = len(combined) - n_val
    generator = torch.Generator().manual_seed(42)
    train_split, val_split = random_split(combined, [n_train, n_val], generator=generator)

    # Class-balanced sampler: weights from post-merge train_split indices.
    # We must use combined_samples (not just train_ds.samples) because the merge
    # changes which images fall into the training portion.
    combined_samples = train_ds.samples + val_ds.samples  # all (path, label) pairs
    train_labels = [combined_samples[i][1] for i in train_split.indices]
    train_counts = np.bincount(train_labels, minlength=len(_INTERNAL_NAMES))
    train_weights_per_class = 1.0 / np.maximum(train_counts, 1)
    sample_weights = torch.tensor(
        [train_weights_per_class[label] for label in train_labels],
        dtype=torch.float,
    )
    sampler = WeightedRandomSampler(
        weights=sample_weights,
        num_samples=len(train_split),
        replacement=True,
    )

    return {
        "train": DataLoader(
            train_split,
            batch_size=batch_size,
            sampler=sampler,
            num_workers=num_workers,
            pin_memory=True,
        ),
        "val": DataLoader(
            val_split,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=True,
        ),
        "test": DataLoader(
            test_ds,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=True,
        ),
    }


def log_dataset_metadata(
    loaders: Dict[str, DataLoader],
    data_root: str,
) -> None:
    """Log dataset provenance metadata to the active MLflow run.

    Records source URL, dataset fingerprint, class distribution, and split sizes
    so every training run is fully traceable to the dataset version it used.

    Args:
        loaders: dict of DataLoader instances returned by build_dataloaders().
        data_root: path to the dataset root directory.
    """
    from transforms import get_val_transforms

    # Build a fresh index-only dataset to compute the hash
    train_index_ds = ChestXRayDataset(
        os.path.join(data_root, "train"),
        transform=get_val_transforms(),
    )
    dataset_hash = train_index_ds.compute_hash()

    mlflow.log_params({
        "dataset_source": "https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia",
        "dataset_origin": "Guangzhou Women and Children Medical Centre",
        "dataset_hash": dataset_hash,
        "n_train": len(loaders["train"].dataset),
        "n_val": len(loaders["val"].dataset),
        "n_test": len(loaders["test"].dataset),
        "n_classes": len(CLASS_NAMES),
        "class_names": str(CLASS_NAMES),
    })

    # Per-class counts from the raw training directory
    train_labels = [label for _, label in train_index_ds.samples]
    counts = np.bincount(train_labels, minlength=len(_INTERNAL_NAMES))
    for cls, count in zip(_INTERNAL_NAMES, counts):
        mlflow.log_metric(f"train_count_{cls.lower()}", int(count))

    mlflow.set_tags({
        "data_root": data_root,
        "dataset_version": dataset_hash,
    })
