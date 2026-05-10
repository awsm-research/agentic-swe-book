# gate.py
# Automated evaluation gate for the ChestScan pneumonia detector.
#
# Reads metrics from a completed MLflow run and exits non-zero if any
# clinical quality threshold is not met.  Designed to be called from CI/CD
# pipelines — a non-zero exit code blocks downstream steps (e.g., model registration).
#
# Usage:
#   python gate.py --run-id <RUN_ID>
#   python gate.py --run-id <RUN_ID> --mlflow-uri http://localhost:5000
#
# Exit codes:
#   0 — All thresholds passed.  Model may proceed to registration.
#   1 — One or more thresholds failed.  Pipeline must stop.

import argparse
import sys
from typing import Dict, Tuple

import mlflow
from mlflow.tracking import MlflowClient


# ---------------------------------------------------------------------------
# Clinical quality thresholds
# Edit these to match the deployment requirements for your institution.
# ---------------------------------------------------------------------------
THRESHOLDS: Dict[str, Tuple[str, float]] = {
    "test_auc":         (">=", 0.92),   # Strong overall discrimination
    "test_sensitivity": (">=", 0.90),   # Maximum tolerable false-negative rate for pneumonia
    "test_specificity": (">=", 0.70),   # Minimum correct identification of normal patients
    "test_macro_f1":    (">=", 0.85),   # Balanced performance across all three classes
}


# ---------------------------------------------------------------------------
# Gate logic
# ---------------------------------------------------------------------------

def fetch_run_metrics(client: MlflowClient, run_id: str) -> Dict[str, float]:
    """Fetch all logged metrics from a completed MLflow run."""
    run = client.get_run(run_id)
    return dict(run.data.metrics)


def check_threshold(operator: str, threshold: float, value: float) -> bool:
    """Return True if value satisfies the threshold condition."""
    if operator == ">=":
        return value >= threshold
    if operator == "<=":
        return value <= threshold
    if operator == ">":
        return value > threshold
    if operator == "<":
        return value < threshold
    raise ValueError(f"Unsupported operator: {operator!r}")


def run_gate(run_id: str, mlflow_uri: str) -> bool:
    """Run all evaluation gate checks for the specified MLflow run.

    Prints a detailed pass/fail report for every threshold.

    Args:
        run_id:     the MLflow run to evaluate.
        mlflow_uri: tracking server URI.

    Returns:
        True if all thresholds pass, False if any fail.
    """
    mlflow.set_tracking_uri(mlflow_uri)
    client = MlflowClient(tracking_uri=mlflow_uri)

    print(f"Evaluation Gate")
    print(f"Run ID:       {run_id}")
    print(f"Tracking URI: {mlflow_uri}")
    print("-" * 65)

    metrics = fetch_run_metrics(client, run_id)
    all_passed = True
    failed_metrics = []

    for metric_name, (operator, threshold) in THRESHOLDS.items():
        if metric_name not in metrics:
            print(f"  MISSING  {metric_name:<28} — not found in run metrics")
            all_passed = False
            failed_metrics.append(metric_name)
            continue

        value = metrics[metric_name]
        passed = check_threshold(operator, threshold, value)
        status = "PASS" if passed else "FAIL"
        symbol = "+" if passed else "x"

        print(
            f"  [{symbol}] {status:<6}  {metric_name:<28} "
            f"{operator} {threshold:.4f}   (actual: {value:.4f})"
        )

        if not passed:
            all_passed = False
            failed_metrics.append(metric_name)

    print("-" * 65)

    if all_passed:
        print("GATE PASSED — All clinical quality thresholds met.")
        print(f"Run {run_id} is eligible for registration and promotion.")
    else:
        print(f"GATE FAILED — {len(failed_metrics)} threshold(s) not met: {failed_metrics}")
        print("Model will NOT be registered.  Investigate and retrain.")

    return all_passed


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Evaluation gate for ChestScan pneumonia detector"
    )
    parser.add_argument(
        "--run-id",
        required=True,
        help="MLflow Run ID of the training run to gate",
    )
    parser.add_argument(
        "--mlflow-uri",
        default="http://localhost:5000",
        help="MLflow tracking server URI (default: http://localhost:5000)",
    )
    args = parser.parse_args()

    passed = run_gate(args.run_id, args.mlflow_uri)
    sys.exit(0 if passed else 1)
