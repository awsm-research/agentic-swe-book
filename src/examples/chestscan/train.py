# train.py
# Training script for the ChestScan pneumonia detector.
#
# Trains either a ResNet-18 baseline or DAViT hybrid CNN+ViT model, tracking
# all hyperparameters, per-epoch metrics, artefacts, and the final model to MLflow.
#
# Usage:
#   python train.py --model resnet18 --data-root ./chest_xray --epochs 30
#   python train.py --model davit --data-root ./chest_xray --epochs 30 --lr 1e-4

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mlflow
import mlflow.pytorch
import numpy as np
import seaborn as sns
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.models as tv_models
from mlflow.models.signature import infer_signature
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

from dataset import CLASS_NAMES, ChestXRayDataset, build_dataloaders
from transforms import get_val_transforms

# Internal short names that match the dataset class indices
_INTERNAL_NAMES = ["NORMAL", "BACTERIA", "VIRUS"]


# ---------------------------------------------------------------------------
# Device
# ---------------------------------------------------------------------------

def get_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


# ---------------------------------------------------------------------------
# Model factory
# ---------------------------------------------------------------------------

def build_resnet18(num_classes: int = 3, pretrained: bool = True) -> nn.Module:
    """ResNet-18 fine-tuned for chest X-ray classification.

    Replaces the final fully connected layer with a dropout + linear head
    sized for num_classes outputs.
    """
    weights = tv_models.ResNet18_Weights.IMAGENET1K_V1 if pretrained else None
    model = tv_models.resnet18(weights=weights)
    in_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(p=0.3),
        nn.Linear(in_features, num_classes),
    )
    return model


class DAViT(nn.Module):
    """Domain-Adapted Vision Transformer for chest X-ray classification.

    Architecture:
        CNN backbone (ResNet-34, layers 1-3)
        → patch tokens (14×14 spatial grid, 196 tokens)
        → linear projection to d_model dimensions
        → CLS token prepended
        → positional encoding added
        → Transformer encoder (num_layers layers, nhead attention heads)
        → classification head on CLS token output
    """

    def __init__(
        self,
        num_classes: int = 3,
        d_model: int = 256,
        nhead: int = 4,
        num_layers: int = 6,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.d_model = d_model

        # CNN backbone: ResNet-34 up through layer3
        # Output for 224×224 input: (B, 256, 14, 14)
        backbone = tv_models.resnet34(weights=tv_models.ResNet34_Weights.IMAGENET1K_V1)
        self.cnn_backbone = nn.Sequential(
            backbone.conv1,
            backbone.bn1,
            backbone.relu,
            backbone.maxpool,
            backbone.layer1,
            backbone.layer2,
            backbone.layer3,
        )
        cnn_out_channels = 256

        # Project CNN spatial features to transformer token dimension
        self.patch_proj = nn.Linear(cnn_out_channels, d_model)

        # Learnable CLS token (accumulated global context)
        self.cls_token = nn.Parameter(torch.zeros(1, 1, d_model))
        nn.init.trunc_normal_(self.cls_token, std=0.02)

        # Positional encoding: 1 CLS + 14×14 = 197 positions
        self.pos_embedding = nn.Parameter(torch.zeros(1, 197, d_model))
        nn.init.trunc_normal_(self.pos_embedding, std=0.02)

        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 4,
            dropout=dropout,
            activation="gelu",
            batch_first=True,
            norm_first=True,
        )
        self.transformer = nn.TransformerEncoder(
            encoder_layer,
            num_layers=num_layers,
            norm=nn.LayerNorm(d_model),
        )

        # Classification head — applied to CLS token only
        self.classifier = nn.Sequential(
            nn.LayerNorm(d_model),
            nn.Dropout(p=dropout),
            nn.Linear(d_model, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B = x.size(0)

        # CNN feature extraction: (B, 256, 14, 14)
        features = self.cnn_backbone(x)

        # Flatten spatial dimensions to token sequence: (B, 196, 256)
        tokens = features.flatten(2).permute(0, 2, 1)

        # Project to transformer dimension: (B, 196, d_model)
        tokens = self.patch_proj(tokens)

        # Prepend CLS token: (B, 197, d_model)
        cls = self.cls_token.expand(B, -1, -1)
        tokens = torch.cat([cls, tokens], dim=1)

        # Add positional encoding
        tokens = tokens + self.pos_embedding

        # Transformer encoding: (B, 197, d_model)
        encoded = self.transformer(tokens)

        # Classify from CLS token: (B, num_classes)
        return self.classifier(encoded[:, 0])


# ---------------------------------------------------------------------------
# Training utilities
# ---------------------------------------------------------------------------

def compute_auc(labels: np.ndarray, probs: np.ndarray) -> float:
    try:
        return float(roc_auc_score(labels, probs, multi_class="ovr", average="macro"))
    except ValueError:
        return 0.0


def train_one_epoch(
    model: nn.Module,
    loader,
    optimizer: optim.Optimizer,
    criterion: nn.Module,
    device: torch.device,
    scaler,
) -> float:
    model.train()
    total_loss = 0.0
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        with torch.autocast(device_type=device.type, enabled=(device.type == "cuda")):
            logits = model(images)
            loss = criterion(logits, labels)
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
        total_loss += loss.item() * images.size(0)
    return total_loss / len(loader.dataset)


@torch.no_grad()
def evaluate(
    model: nn.Module,
    loader,
    criterion: nn.Module,
    device: torch.device,
) -> Dict[str, Any]:
    model.eval()
    total_loss = 0.0
    all_labels, all_preds, all_probs = [], [], []

    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        logits = model(images)
        loss = criterion(logits, labels)
        total_loss += loss.item() * images.size(0)
        probs = torch.softmax(logits, dim=1)
        preds = probs.argmax(dim=1)
        all_labels.extend(labels.cpu().numpy())
        all_preds.extend(preds.cpu().numpy())
        all_probs.extend(probs.cpu().numpy())

    all_labels = np.array(all_labels)
    all_preds = np.array(all_preds)
    all_probs = np.array(all_probs)

    return {
        "loss": total_loss / len(loader.dataset),
        "accuracy": float((all_preds == all_labels).mean()),
        "auc": compute_auc(all_labels, all_probs),
        "labels": all_labels,
        "preds": all_preds,
        "probs": all_probs,
    }


def plot_confusion_matrix(
    labels: np.ndarray,
    preds: np.ndarray,
    save_path: str,
) -> None:
    cm = confusion_matrix(labels, preds, labels=list(range(len(_INTERNAL_NAMES))))
    cm_norm = cm.astype(float) / np.maximum(cm.sum(axis=1, keepdims=True), 1)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for ax, data, title, fmt in zip(
        axes,
        [cm, cm_norm],
        ["Confusion Matrix (counts)", "Confusion Matrix (normalised)"],
        ["d", ".2f"],
    ):
        sns.heatmap(
            data,
            annot=True,
            fmt=fmt,
            cmap="Blues",
            xticklabels=CLASS_NAMES,
            yticklabels=CLASS_NAMES,
            ax=ax,
        )
        ax.set_title(title)
        ax.set_xlabel("Predicted")
        ax.set_ylabel("True")

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_training_curves(
    train_losses: list,
    val_losses: list,
    val_aucs: list,
    save_path: str,
) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    epochs = range(1, len(train_losses) + 1)

    ax1.plot(epochs, train_losses, label="Train Loss", linewidth=2)
    ax1.plot(epochs, val_losses, label="Val Loss", linewidth=2, linestyle="--")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Loss")
    ax1.set_title("Training and Validation Loss")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.plot(epochs, val_aucs, label="Val AUC", linewidth=2, color="green")
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("AUC-ROC")
    ax2.set_title("Validation AUC Over Training")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


# ---------------------------------------------------------------------------
# Main training function
# ---------------------------------------------------------------------------

def train(config: Dict[str, Any]) -> str:
    """Full training loop with MLflow tracking.

    Logs hyperparameters, dataset metadata, per-epoch metrics, confusion matrix,
    training curves, and the final model to MLflow.

    Args:
        config: training configuration dictionary.

    Returns:
        The MLflow run_id for the completed run.
    """
    device = get_device()
    print(f"Using device: {device}")

    mlflow.set_tracking_uri(config["mlflow_uri"])
    mlflow.set_experiment(config["experiment_name"])

    with mlflow.start_run(run_name=config["run_name"]) as run:
        run_id = run.info.run_id

        # Log all hyperparameters before training starts.
        # This ensures a crashed run still has its configuration recorded.
        mlflow.log_params({
            "model": config["model"],
            "learning_rate": config["lr"],
            "batch_size": config["batch_size"],
            "epochs": config["epochs"],
            "optimizer": "AdamW",
            "weight_decay": config["weight_decay"],
            "image_size": 224,
            "num_classes": 3,
            "class_names": str(CLASS_NAMES),
            "pretrained": True,
            "early_stopping_patience": config.get("patience", 10),
            "dataset_source": "kaggle:paultimothymooney/chest-xray-pneumonia",
        })
        mlflow.set_tags({
            "dataset": "chest-xray-pneumonia-kaggle",
            "task": "3-class-classification",
        })

        # Build dataloaders
        loaders = build_dataloaders(
            config["data_root"],
            batch_size=config["batch_size"],
            num_workers=config.get("num_workers", 4),
        )

        # Log dataset metadata for provenance tracking
        train_ds_for_hash = ChestXRayDataset(
            os.path.join(config["data_root"], "train"),
            transform=get_val_transforms(),
        )
        mlflow.log_params({
            "dataset_hash": train_ds_for_hash.compute_hash(),
            "n_train_images": len(loaders["train"].dataset),
            "n_val_images": len(loaders["val"].dataset),
            "n_test_images": len(loaders["test"].dataset),
        })

        # Build model
        if config["model"] == "resnet18":
            model = build_resnet18(num_classes=3, pretrained=True)
            optimizer = optim.AdamW(
                model.parameters(),
                lr=config["lr"],
                weight_decay=config["weight_decay"],
            )
        elif config["model"] == "davit":
            model = DAViT(num_classes=3, d_model=256, nhead=4, num_layers=6, dropout=0.1)
            backbone_params = list(model.cnn_backbone.parameters())
            head_params = [p for p in model.parameters()
                           if not any(p is bp for bp in backbone_params)]
            # Differential learning rate: backbone at 10× lower lr than transformer head
            optimizer = optim.AdamW(
                [
                    {"params": backbone_params, "lr": config["lr"] * 0.1},
                    {"params": head_params, "lr": config["lr"]},
                ],
                weight_decay=config["weight_decay"],
            )
        else:
            raise ValueError(f"Unknown model: {config['model']}. Choose 'resnet18' or 'davit'.")

        model = model.to(device)

        # Weighted cross-entropy: addresses class imbalance at the loss level.
        # Combined with WeightedRandomSampler in the dataloader this gives double
        # protection against the majority-class bias.
        class_counts = torch.tensor([1583.0, 2780.0, 1493.0])
        class_weights = (class_counts.sum() / (len(_INTERNAL_NAMES) * class_counts)).to(device)
        criterion = nn.CrossEntropyLoss(weight=class_weights, label_smoothing=0.1)

        scheduler = optim.lr_scheduler.CosineAnnealingLR(
            optimizer, T_max=config["epochs"], eta_min=1e-7
        )
        scaler = torch.cuda.amp.GradScaler(enabled=(device.type == "cuda"))

        # Training loop with early stopping on val AUC
        best_val_auc = 0.0
        best_epoch = 0
        patience = config.get("patience", 10)
        patience_counter = 0
        best_model_path = Path(f"/tmp/{run_id}_best.pt")
        train_losses, val_losses, val_aucs = [], [], []

        for epoch in range(config["epochs"]):
            train_loss = train_one_epoch(
                model, loaders["train"], optimizer, criterion, device, scaler
            )
            val_metrics = evaluate(model, loaders["val"], criterion, device)
            scheduler.step()

            train_losses.append(train_loss)
            val_losses.append(val_metrics["loss"])
            val_aucs.append(val_metrics["auc"])

            # Log metrics with step= so MLflow renders learning curves
            mlflow.log_metrics(
                {
                    "train_loss": train_loss,
                    "val_loss": val_metrics["loss"],
                    "val_accuracy": val_metrics["accuracy"],
                    "val_auc": val_metrics["auc"],
                    "lr": scheduler.get_last_lr()[0],
                },
                step=epoch,
            )

            print(
                f"Epoch {epoch + 1:03d}/{config['epochs']} | "
                f"train_loss={train_loss:.4f} | "
                f"val_loss={val_metrics['loss']:.4f} | "
                f"val_acc={val_metrics['accuracy']:.4f} | "
                f"val_auc={val_metrics['auc']:.4f}"
            )

            if val_metrics["auc"] > best_val_auc:
                best_val_auc = val_metrics["auc"]
                best_epoch = epoch
                patience_counter = 0
                torch.save(model.state_dict(), best_model_path)
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print(f"Early stopping at epoch {epoch + 1} (patience={patience})")
                    break

        # Load best checkpoint and evaluate on held-out test set
        model.load_state_dict(torch.load(best_model_path, map_location=device))
        test_metrics = evaluate(model, loaders["test"], criterion, device)

        mlflow.log_metrics({
            "test_accuracy": test_metrics["accuracy"],
            "test_auc": test_metrics["auc"],
            "best_val_auc": best_val_auc,
            "best_epoch": best_epoch,
        })

        print(
            f"\nTest AUC: {test_metrics['auc']:.4f} | "
            f"Test Accuracy: {test_metrics['accuracy']:.4f}"
        )

        # Confusion matrix artefact
        cm_path = f"/tmp/{run_id}_confusion_matrix.png"
        plot_confusion_matrix(test_metrics["labels"], test_metrics["preds"], cm_path)
        mlflow.log_artifact(cm_path, artifact_path="plots")

        # Training curve artefact
        curves_path = f"/tmp/{run_id}_training_curves.png"
        plot_training_curves(train_losses, val_losses, val_aucs, curves_path)
        mlflow.log_artifact(curves_path, artifact_path="plots")

        # Classification report JSON
        report = classification_report(
            test_metrics["labels"],
            test_metrics["preds"],
            target_names=CLASS_NAMES,
            output_dict=True,
        )
        report_path = f"/tmp/{run_id}_classification_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        mlflow.log_artifact(report_path, artifact_path="evaluation")

        # Log the PyTorch model with input signature for the Model Registry
        sample_input = torch.zeros(1, 3, 224, 224)
        model_cpu = model.cpu()
        with torch.no_grad():
            sample_output = model_cpu(sample_input).numpy()
        signature = infer_signature(sample_input.numpy(), sample_output)

        mlflow.pytorch.log_model(
            model_cpu,
            artifact_path="model",
            registered_model_name="chestscan-pneumonia-detector",
            signature=signature,
            input_example=sample_input.numpy(),
        )

        print(f"\nRun complete. Run ID: {run_id}")
        return run_id


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train chest X-ray classifier with MLflow tracking"
    )
    parser.add_argument(
        "--model",
        choices=["resnet18", "davit"],
        default="resnet18",
        help="Model architecture (default: resnet18)",
    )
    parser.add_argument(
        "--data-root",
        default="./chest_xray",
        help="Path to chest_xray directory (must contain train/, val/, test/)",
    )
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--patience", type=int, default=10, help="Early stopping patience")
    parser.add_argument("--num-workers", type=int, default=4)
    parser.add_argument("--mlflow-uri", default="http://localhost:5000")
    parser.add_argument("--experiment-name", default="chestscan-v1")
    args = parser.parse_args()

    config = {
        "model": args.model,
        "data_root": args.data_root,
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "lr": args.lr,
        "weight_decay": args.weight_decay,
        "patience": args.patience,
        "num_workers": args.num_workers,
        "mlflow_uri": args.mlflow_uri,
        "experiment_name": args.experiment_name,
        "run_name": f"{args.model}-lr{args.lr}-bs{args.batch_size}",
    }

    train(config)
