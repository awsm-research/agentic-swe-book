# monitor.py
# Production drift detection for the ChestScan pneumonia detector.
#
# Reads production predictions logged by the FastAPI backend to the
# 'production-predictions' MLflow experiment, computes Population Stability
# Index (PSI) relative to the training class distribution baseline, and
# alerts when drift exceeds the configured threshold.
#
# Usage:
#   python monitor.py --experiment-name production-inference --n-recent 100
#   python monitor.py --mlflow-uri http://localhost:5000 --lookback-days 7
#
# Exit codes:
#   0 — No significant drift detected.
#   2 — Drift detected — retraining evaluation recommended.

import argparse
import sys
from datetime import datetime, timedelta
from typing import Any, Dict

import numpy as np
import mlflow
from mlflow.tracking import MlflowClient


# ---------------------------------------------------------------------------
# Training distribution baseline
# Derived from the Kaggle Chest X-Ray Pneumonia dataset class counts:
#   Normal:   1,583 / 5,856 = 27.0 %
#   Bacteria: 2,780 / 5,856 = 47.5 %
#   Virus:    1,493 / 5,856 = 25.5 %
# ---------------------------------------------------------------------------
TRAINING_CLASS_DISTRIBUTION: Dict[str, float] = {
    "NORMAL":   0.270,
    "BACTERIA": 0.475,
    "VIRUS":    0.255,
}

# PSI thresholds (standard industry values)
PSI_ALERT_THRESHOLD   = 0.20   # Significant drift — investigate and consider retraining
PSI_WARNING_THRESHOLD = 0.10   # Moderate drift — monitor closely

# Minimum predictions needed for reliable PSI estimation
MIN_PREDICTIONS = 100


# ---------------------------------------------------------------------------
# PSI computation
# ---------------------------------------------------------------------------

def compute_psi(
    expected: np.ndarray,
    actual: np.ndarray,
    buckets: int = 10,
) -> float:
    """Compute Population Stability Index between two continuous distributions.

    PSI = sum_i [ (actual_i - expected_i) * ln(actual_i / expected_i) ]

    Interpretation:
      PSI < 0.10:  No significant shift.
      0.10 - 0.20: Moderate shift — monitor closely.
      >= 0.20:     Significant shift — investigate and consider retraining.

    Args:
        expected: reference distribution samples (e.g., training confidences).
        actual:   production distribution samples.
        buckets:  number of histogram bins.

    Returns:
        PSI value as a float.
    """
    epsilon = 1e-6
    min_val = min(expected.min(), actual.min())
    max_val = max(expected.max(), actual.max())
    bins = np.linspace(min_val - epsilon, max_val + epsilon, buckets + 1)

    expected_counts, _ = np.histogram(expected, bins=bins)
    actual_counts, _   = np.histogram(actual, bins=bins)

    expected_pct = (expected_counts + epsilon) / (len(expected) + epsilon * buckets)
    actual_pct   = (actual_counts + epsilon) / (len(actual) + epsilon * buckets)

    return float(np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct)))


def compute_class_psi(production_class_counts: Dict[str, int]) -> float:
    """Compute PSI for the prediction class distribution.

    Uses a discrete PSI formula that compares the observed production
    class proportions against the training baseline proportions.

    Args:
        production_class_counts: dict mapping class name -> count.

    Returns:
        PSI value as a float.
    """
    total = sum(production_class_counts.values())
    if total == 0:
        return 0.0

    epsilon = 1e-6
    psi = 0.0
    for cls in ["NORMAL", "BACTERIA", "VIRUS"]:
        expected_pct = TRAINING_CLASS_DISTRIBUTION.get(cls, epsilon)
        actual_count = production_class_counts.get(cls, 0)
        actual_pct   = actual_count / total + epsilon
        psi += (actual_pct - expected_pct) * np.log(actual_pct / expected_pct)

    return float(psi)


# ---------------------------------------------------------------------------
# Data fetching from MLflow
# ---------------------------------------------------------------------------

def fetch_production_predictions(
    client: MlflowClient,
    experiment_name: str,
    n_recent: int = 100,
    lookback_days: int = 7,
    mlflow_uri: str = "http://localhost:5000",
) -> Dict[str, Any]:
    """Fetch recent production predictions logged by the FastAPI backend.

    Args:
        client:          MlflowClient instance.
        experiment_name: name of the production predictions experiment.
        n_recent:        maximum number of recent runs to fetch.
        lookback_days:   only consider runs from the last N days.
        mlflow_uri:      tracking server URI.

    Returns:
        Dict with aggregated prediction data, or empty dict if no data.
    """
    mlflow.set_tracking_uri(mlflow_uri)

    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment is None:
        print(f"No experiment named '{experiment_name}' found.")
        print("No production predictions have been logged yet.")
        return {}

    cutoff_ms = int((datetime.now() - timedelta(days=lookback_days)).timestamp() * 1000)

    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        filter_string=f"attributes.start_time > {cutoff_ms}",
        max_results=n_recent,
        order_by=["attributes.start_time DESC"],
    )

    if not runs:
        print(f"No predictions found in the last {lookback_days} days.")
        return {}

    print(f"Found {len(runs)} production predictions (last {lookback_days} days).")

    class_counts: Dict[str, int] = {"NORMAL": 0, "BACTERIA": 0, "VIRUS": 0}
    confidences: list = []
    prob_normals, prob_bacterias, prob_viruses = [], [], []

    for run in runs:
        params  = run.data.params
        metrics = run.data.metrics

        pred_class = params.get("predicted_class", "").upper()
        if pred_class in class_counts:
            class_counts[pred_class] += 1

        conf = metrics.get("confidence")
        if conf is not None:
            confidences.append(float(conf))

        for key, lst in [
            ("prob_normal",   prob_normals),
            ("prob_bacteria", prob_bacterias),
            ("prob_virus",    prob_viruses),
        ]:
            val = metrics.get(key)
            if val is not None:
                lst.append(float(val))

    return {
        "n_predictions": len(runs),
        "class_counts":  class_counts,
        "confidences":   np.array(confidences) if confidences else np.array([]),
        "prob_normals":  np.array(prob_normals),
        "prob_bacterias": np.array(prob_bacterias),
        "prob_viruses":  np.array(prob_viruses),
    }


# ---------------------------------------------------------------------------
# Main drift detection routine
# ---------------------------------------------------------------------------

def run_drift_detection(
    mlflow_uri: str = "http://localhost:5000",
    experiment_name: str = "production-predictions",
    n_recent: int = 100,
    lookback_days: int = 7,
) -> bool:
    """Run drift detection on recent production predictions.

    Args:
        mlflow_uri:      tracking server URI.
        experiment_name: production predictions experiment name.
        n_recent:        maximum number of recent predictions to analyse.
        lookback_days:   time window in days.

    Returns:
        True if significant drift is detected (PSI >= PSI_ALERT_THRESHOLD).
    """
    mlflow.set_tracking_uri(mlflow_uri)
    client = MlflowClient(tracking_uri=mlflow_uri)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Drift Detection Report — {timestamp}")
    print(f"Experiment: {experiment_name}")
    print(f"Lookback:   {lookback_days} days  |  Max samples: {n_recent}")
    print("-" * 65)

    data = fetch_production_predictions(
        client, experiment_name, n_recent, lookback_days, mlflow_uri
    )

    if not data:
        print("No data available.  Skipping drift check.")
        return False

    n = data["n_predictions"]
    if n < MIN_PREDICTIONS:
        print(
            f"Insufficient data ({n} predictions). "
            f"Minimum required: {MIN_PREDICTIONS}.  Skipping drift check."
        )
        return False

    class_counts = data["class_counts"]
    confidences  = data["confidences"]

    # --- Class distribution summary ---
    print(f"\nProduction class distribution (n={n}):")
    for cls, count in class_counts.items():
        pct      = count / n if n > 0 else 0.0
        baseline = TRAINING_CLASS_DISTRIBUTION.get(cls, 0.0)
        delta    = pct - baseline
        print(
            f"  {cls:<12}: {count:>5} ({pct:.1%})  "
            f"| training baseline: {baseline:.1%}  "
            f"| delta: {delta:+.1%}"
        )

    # --- PSI computation ---
    class_psi = compute_class_psi(class_counts)

    # Confidence PSI: compare against a synthetic reference from training-time performance
    # (model confidence should cluster in [0.75, 0.98] for a well-calibrated model)
    rng = np.random.default_rng(seed=42)
    confidence_reference = rng.uniform(0.75, 0.98, size=1000)
    confidence_psi = (
        compute_psi(confidence_reference, confidences)
        if len(confidences) >= 10
        else 0.0
    )

    print(f"\nDrift Metrics:")
    print(f"  Class Distribution PSI : {class_psi:.4f}")
    print(f"  Confidence PSI         : {confidence_psi:.4f}")
    print(f"  Warning threshold      : PSI >= {PSI_WARNING_THRESHOLD}")
    print(f"  Alert threshold        : PSI >= {PSI_ALERT_THRESHOLD}")

    # --- Evaluation ---
    drift_detected = False
    for name, psi_val in [("Class Distribution", class_psi), ("Confidence", confidence_psi)]:
        if psi_val >= PSI_ALERT_THRESHOLD:
            print(
                f"\n  DRIFT DETECTED: {name} PSI = {psi_val:.4f} "
                f"(>= alert threshold {PSI_ALERT_THRESHOLD})"
            )
            print("  Retraining evaluation is strongly recommended.")
            drift_detected = True
        elif psi_val >= PSI_WARNING_THRESHOLD:
            print(
                f"\n  WARNING: {name} PSI = {psi_val:.4f} "
                f"(moderate drift range). Monitor closely."
            )

    print("-" * 65)
    if drift_detected:
        print("DRIFT DETECTED — run retraining pipeline and compare against current @champion.")
    else:
        print("No significant drift detected.  Model is stable.")

    return drift_detected


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Production drift detector for the ChestScan pneumonia detector"
    )
    parser.add_argument(
        "--mlflow-uri",
        default="http://localhost:5000",
        help="MLflow tracking server URI",
    )
    parser.add_argument(
        "--experiment-name",
        default="production-predictions",
        help="MLflow experiment name where production predictions are logged",
    )
    parser.add_argument(
        "--n-recent",
        type=int,
        default=100,
        help="Maximum number of recent predictions to analyse",
    )
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=7,
        help="Time window in days (default: 7)",
    )
    args = parser.parse_args()

    drift = run_drift_detection(
        mlflow_uri=args.mlflow_uri,
        experiment_name=args.experiment_name,
        n_recent=args.n_recent,
        lookback_days=args.lookback_days,
    )
    sys.exit(2 if drift else 0)
