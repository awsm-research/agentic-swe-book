# evaluate.py
# Clinical evaluation script for the ChestScan pneumonia detector.
#
# Loads a trained model from MLflow by run_id, runs inference on the test split,
# computes the full clinical metric suite, logs everything to a new MLflow run,
# and saves ROC curve artefacts.
#
# Usage:
#   python evaluate.py --run-id <RUN_ID> --data-root ./chest_xray
#   python evaluate.py --run-id <RUN_ID> --data-root ./chest_xray --mlflow-uri http://localhost:5000

import argparse
from typing import Dict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mlflow
import mlflow.pytorch
import numpy as np
import torch
from sklearn.metrics import (
    confusion_matrix,
    precision_recall_fscore_support,
    roc_auc_score,
    roc_curve,
)

from dataset import build_dataloaders

# Internal keys that match the dataset class indices
_INTERNAL_NAMES = ["NORMAL", "BACTERIA", "VIRUS"]


# ---------------------------------------------------------------------------
# Metric computation
# ---------------------------------------------------------------------------

def compute_clinical_metrics(
    labels: np.ndarray,
    preds: np.ndarray,
    probs: np.ndarray,
    prefix: str = "test",
) -> Dict[str, float]:
    """Compute the full suite of clinical evaluation metrics.

    Args:
        labels: true class indices, shape (N,).
        preds:  predicted class indices, shape (N,).
        probs:  softmax probabilities, shape (N, num_classes).
        prefix: metric name prefix (e.g. "test", "val", "final_test").

    Returns:
        Dictionary mapping metric_name → float value.
    """
    metrics: Dict[str, float] = {}
    n_classes = len(_INTERNAL_NAMES)

    # Overall accuracy
    metrics[f"{prefix}_accuracy"] = float((preds == labels).mean())

    # Per-class precision, recall, F1 from sklearn
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, preds, labels=list(range(n_classes)), zero_division=0
    )
    for i, cls in enumerate(_INTERNAL_NAMES):
        cls_lower = cls.lower()
        metrics[f"{prefix}_precision_{cls_lower}"] = float(precision[i])
        metrics[f"{prefix}_recall_{cls_lower}"]    = float(recall[i])
        metrics[f"{prefix}_f1_{cls_lower}"]        = float(f1[i])

    # Macro averages
    metrics[f"{prefix}_macro_f1"]        = float(f1.mean())
    metrics[f"{prefix}_macro_recall"]    = float(recall.mean())
    metrics[f"{prefix}_macro_precision"] = float(precision.mean())

    # AUC-ROC (macro OvR — robust to class imbalance)
    try:
        auc = roc_auc_score(labels, probs, multi_class="ovr", average="macro")
        metrics[f"{prefix}_auc"] = float(auc)
    except ValueError:
        metrics[f"{prefix}_auc"] = 0.0

    # Clinical binary metrics: pneumonia (BACTERIA+VIRUS) vs. NORMAL
    binary_labels = (labels > 0).astype(int)   # 0 = Normal, 1 = Pneumonia
    binary_preds  = (preds > 0).astype(int)
    binary_probs  = probs[:, 1] + probs[:, 2]  # P(pneumonia) = P(bacteria) + P(virus)

    tn, fp, fn, tp = confusion_matrix(binary_labels, binary_preds, labels=[0, 1]).ravel()
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0  # recall for pneumonia
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0  # recall for normal
    ppv = tp / (tp + fp) if (tp + fp) > 0 else 0.0           # precision for pneumonia
    npv = tn / (tn + fn) if (tn + fn) > 0 else 0.0           # precision for normal

    metrics[f"{prefix}_sensitivity"] = float(sensitivity)
    metrics[f"{prefix}_specificity"] = float(specificity)
    metrics[f"{prefix}_ppv"]         = float(ppv)
    metrics[f"{prefix}_npv"]         = float(npv)

    # Binary AUC (pneumonia vs. normal)
    try:
        binary_auc = roc_auc_score(binary_labels, binary_probs)
        metrics[f"{prefix}_binary_auc"] = float(binary_auc)
    except ValueError:
        metrics[f"{prefix}_binary_auc"] = 0.0

    return metrics


def evaluate_by_slice(
    labels: np.ndarray,
    preds: np.ndarray,
    probs: np.ndarray,
) -> None:
    """Compute per-class slice evaluation and log to the active MLflow run.

    Slice-based evaluation reveals class-level failures that aggregate
    metrics conceal.  For example, overall sensitivity may pass the gate
    while viral pneumonia recall is substantially lower.
    """
    print("\n--- SLICE EVALUATION ---")
    for i, cls in enumerate(_INTERNAL_NAMES):
        cls_mask = labels == i
        if cls_mask.sum() == 0:
            continue
        cls_preds = preds[cls_mask]
        cls_labels = labels[cls_mask]
        recall = float((cls_preds == cls_labels).mean())
        n = int(cls_mask.sum())
        print(f"  {cls:<10}: n={n:>4}, recall={recall:.4f}")
        mlflow.log_metric(f"test_slice_recall_{cls.lower()}", recall)

    # Bacterial vs. viral separation metrics
    pneu_mask = labels > 0
    if pneu_mask.sum() > 0:
        pneu_labels = labels[pneu_mask]
        pneu_probs  = probs[pneu_mask]
        bv_labels   = (pneu_labels == 2).astype(int)  # 1 = virus, 0 = bacteria
        bv_probs    = pneu_probs[:, 2] / np.maximum(pneu_probs[:, 1] + pneu_probs[:, 2], 1e-9)
        try:
            bv_auc = roc_auc_score(bv_labels, bv_probs)
            print(f"  Bacterial vs. Viral AUC: {bv_auc:.4f}")
            mlflow.log_metric("test_bacterial_vs_viral_auc", float(bv_auc))
        except ValueError:
            pass


# ---------------------------------------------------------------------------
# ROC curve plot
# ---------------------------------------------------------------------------

def plot_roc_curves(
    labels: np.ndarray,
    probs: np.ndarray,
    save_path: str,
    operating_sensitivity: float = 0.90,
) -> None:
    """Save a two-panel ROC figure (per-class OvR + binary pneumonia/normal)."""
    _, axes = plt.subplots(1, 2, figsize=(14, 5))
    colors = ["#e41a1c", "#377eb8", "#4daf4a"]

    # Per-class OvR ROC curves
    ax = axes[0]
    for i, (cls, color) in enumerate(zip(_INTERNAL_NAMES, colors)):
        binary_y = (labels == i).astype(int)
        try:
            fpr, tpr, _ = roc_curve(binary_y, probs[:, i])
            auc = roc_auc_score(binary_y, probs[:, i])
            ax.plot(fpr, tpr, color=color, linewidth=2, label=f"{cls} (AUC={auc:.3f})")
        except ValueError:
            pass
    ax.plot([0, 1], [0, 1], "k--", linewidth=1, alpha=0.5)
    ax.set_xlabel("False Positive Rate (1 - Specificity)")
    ax.set_ylabel("True Positive Rate (Sensitivity)")
    ax.set_title("Per-Class ROC Curves (One-vs-Rest)")
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)

    # Binary pneumonia/normal ROC with operating point
    ax = axes[1]
    binary_labels = (labels > 0).astype(int)
    binary_probs  = probs[:, 1] + probs[:, 2]
    try:
        fpr, tpr, _ = roc_curve(binary_labels, binary_probs)
        auc = roc_auc_score(binary_labels, binary_probs)
        ax.plot(fpr, tpr, color="#984ea3", linewidth=2,
                label=f"Pneumonia vs Normal (AUC={auc:.3f})")
        idx = np.argmin(np.abs(tpr - operating_sensitivity))
        ax.scatter(
            fpr[idx], tpr[idx], color="red", zorder=5, s=100,
            label=f"Operating point (Sensitivity={tpr[idx]:.2f})",
        )
    except ValueError:
        pass

    ax.plot([0, 1], [0, 1], "k--", linewidth=1, alpha=0.5)
    ax.set_xlabel("False Positive Rate (1 - Specificity)")
    ax.set_ylabel("True Positive Rate (Sensitivity)")
    ax.set_title("Binary ROC: Pneumonia vs Normal")
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)

    plt.suptitle("ChestScan — ROC Analysis", fontsize=13, y=1.02)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


# ---------------------------------------------------------------------------
# High-level evaluation function
# ---------------------------------------------------------------------------

def evaluate_model(
    run_id: str,
    data_root: str,
    mlflow_uri: str = "http://localhost:5000",
    prefix: str = "test",
) -> Dict[str, float]:
    """Load model from MLflow by run_id and evaluate on the test split.

    Logs all clinical metrics and ROC curve artefacts to a new MLflow run
    in the 'chestscan-evaluation' experiment.

    Args:
        run_id:      the MLflow run_id that logged the model to evaluate.
        data_root:   path to the chest_xray dataset directory.
        mlflow_uri:  MLflow tracking server URI.
        prefix:      metric name prefix.

    Returns:
        Dictionary of computed metric_name → float.
    """
    mlflow.set_tracking_uri(mlflow_uri)

    print(f"Loading model from run: {run_id}")
    model = mlflow.pytorch.load_model(f"runs:/{run_id}/model")
    model.eval()

    device = (
        torch.device("cuda") if torch.cuda.is_available()
        else torch.device("mps") if torch.backends.mps.is_available()
        else torch.device("cpu")
    )
    model = model.to(device)
    print(f"Model loaded. Device: {device}")

    # Build test dataloader
    loaders = build_dataloaders(data_root, batch_size=32, num_workers=4)

    # Collect predictions
    all_labels, all_preds, all_probs = [], [], []
    with torch.no_grad():
        for images, labels in loaders["test"]:
            images = images.to(device)
            logits = model(images)
            probs  = torch.softmax(logits, dim=1)
            preds  = probs.argmax(dim=1)
            all_labels.extend(labels.numpy())
            all_preds.extend(preds.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())

    labels_arr = np.array(all_labels)
    preds_arr  = np.array(all_preds)
    probs_arr  = np.array(all_probs)

    # Log everything to a new evaluation run
    mlflow.set_experiment("chestscan-evaluation")
    with mlflow.start_run(run_name=f"eval-{run_id[:8]}") as eval_run:
        mlflow.log_param("source_run_id", run_id)
        mlflow.log_param("eval_dataset", data_root)

        # Full clinical metric suite
        metrics = compute_clinical_metrics(labels_arr, preds_arr, probs_arr, prefix=prefix)
        mlflow.log_metrics(metrics)

        # Slice-based evaluation
        evaluate_by_slice(labels_arr, preds_arr, probs_arr)

        # ROC curve artefact
        roc_path = f"/tmp/eval_{run_id[:8]}_roc_curves.png"
        plot_roc_curves(labels_arr, probs_arr, roc_path)
        mlflow.log_artifact(roc_path, artifact_path="plots")

        # Print summary
        print(f"\n--- {prefix.upper()} METRICS ---")
        print(f"  AUC:         {metrics.get(f'{prefix}_auc', 0):.4f}")
        print(f"  Accuracy:    {metrics.get(f'{prefix}_accuracy', 0):.4f}")
        print(f"  Sensitivity: {metrics.get(f'{prefix}_sensitivity', 0):.4f}")
        print(f"  Specificity: {metrics.get(f'{prefix}_specificity', 0):.4f}")
        print(f"  PPV:         {metrics.get(f'{prefix}_ppv', 0):.4f}")
        print(f"  NPV:         {metrics.get(f'{prefix}_npv', 0):.4f}")
        print(f"  Macro F1:    {metrics.get(f'{prefix}_macro_f1', 0):.4f}")
        print(f"\nEvaluation run ID: {eval_run.info.run_id}")

    return metrics


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Evaluate a ChestScan model checkpoint against clinical quality metrics"
    )
    parser.add_argument(
        "--run-id",
        required=True,
        help="MLflow run_id of the training run to evaluate",
    )
    parser.add_argument(
        "--data-root",
        default="./chest_xray",
        help="Path to chest_xray dataset directory",
    )
    parser.add_argument(
        "--mlflow-uri",
        default="http://localhost:5000",
        help="MLflow tracking server URI",
    )
    args = parser.parse_args()

    evaluate_model(args.run_id, args.data_root, args.mlflow_uri)
