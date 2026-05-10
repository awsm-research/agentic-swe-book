"""
MedChat deployment gate — Chapter 19.

Reads RAGAS and LLM-judge scores from the most recent MLflow runs in the
'medchat-evaluation' experiment and applies hard quality thresholds.

Exit codes:
    0  — all thresholds met; deployment is approved.
    1  — one or more thresholds failed; deployment is blocked.

Usage:
    export MLFLOW_TRACKING_URI="http://localhost:5000"
    python eval/gate.py

Thresholds:
    faithfulness       >= 0.85
    answer_relevancy   >= 0.80
    hallucination_rate <= 0.05   (derived as 1 - faithfulness)
"""

from __future__ import annotations

import os
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import mlflow

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("medchat.gate")

MLFLOW_EXPERIMENT = "medchat-evaluation"

# ── Gate thresholds ────────────────────────────────────────────────────────────

RAGAS_THRESHOLDS = {
    "faithfulness": 0.85,
    "answer_relevancy": 0.80,
    "context_precision": 0.75,
    "context_recall": 0.70,
}

HALLUCINATION_RATE_MAX = 0.05  # = 1 - faithfulness threshold

JUDGE_THRESHOLDS = {
    "avg_factual_accuracy": 3.5,
    "avg_clinical_safety": 4.0,
    "avg_source_citation": 3.0,
    "avg_response_clarity": 3.5,
}


# ── MLflow helpers ─────────────────────────────────────────────────────────────


def _get_latest_run_metrics(run_name_prefix: str) -> dict[str, float]:
    """
    Fetch metrics from the most recent MLflow run whose name starts with
    *run_name_prefix* in the MLFLOW_EXPERIMENT experiment.

    Returns an empty dict if no matching run is found.
    """
    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000")
    mlflow.set_tracking_uri(tracking_uri)

    client = mlflow.MlflowClient()
    experiment = client.get_experiment_by_name(MLFLOW_EXPERIMENT)
    if experiment is None:
        logger.error(f"MLflow experiment '{MLFLOW_EXPERIMENT}' not found.")
        return {}

    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        filter_string=f"tags.mlflow.runName LIKE '{run_name_prefix}%'",
        order_by=["start_time DESC"],
        max_results=1,
    )
    if not runs:
        logger.warning(f"No runs found with prefix '{run_name_prefix}'.")
        return {}

    return runs[0].data.metrics


# ── Gate logic ─────────────────────────────────────────────────────────────────


def run_gate() -> int:
    """
    Evaluate RAGAS and judge metrics against thresholds.

    Returns 0 if all thresholds pass, 1 if any fail.
    """
    failures: list[str] = []

    # ── RAGAS metrics ──────────────────────────────────────────────────────────
    logger.info("Fetching latest RAGAS run metrics from MLflow…")
    ragas_metrics = _get_latest_run_metrics("ragas-")

    if not ragas_metrics:
        logger.error("No RAGAS run found. Cannot evaluate deployment gate.")
        return 1

    print("\n" + "=" * 65)
    print("DEPLOYMENT GATE REPORT")
    print("=" * 65)
    print("\n[RAGAS Metrics]")

    for metric, threshold in RAGAS_THRESHOLDS.items():
        score = ragas_metrics.get(metric)
        if score is None:
            msg = f"  {metric:<25s}: NOT FOUND — gate fails."
            print(msg)
            failures.append(f"RAGAS '{metric}' metric not found in latest run.")
            continue
        status = "PASS" if score >= threshold else "FAIL"
        print(
            f"  {metric:<25s}: {score:.3f}  (threshold >= {threshold:.3f})  [{status}]"
        )
        if score < threshold:
            failures.append(
                f"RAGAS {metric}: {score:.3f} < threshold {threshold:.3f}"
            )

    # Hallucination rate (derived from faithfulness)
    faithfulness_score = ragas_metrics.get("faithfulness", 1.0)
    hallucination_rate = 1.0 - faithfulness_score
    h_status = "PASS" if hallucination_rate <= HALLUCINATION_RATE_MAX else "FAIL"
    print(
        f"  {'hallucination_rate':<25s}: {hallucination_rate:.3f}  "
        f"(threshold <= {HALLUCINATION_RATE_MAX:.3f})  [{h_status}]"
    )
    if hallucination_rate > HALLUCINATION_RATE_MAX:
        failures.append(
            f"Hallucination rate {hallucination_rate:.3f} > max {HALLUCINATION_RATE_MAX:.3f}"
        )

    # ── LLM judge metrics ──────────────────────────────────────────────────────
    logger.info("Fetching latest judge run metrics from MLflow…")
    judge_metrics = _get_latest_run_metrics("judge-")

    if judge_metrics:
        print("\n[LLM Judge Average Scores (scale 1–5)]")
        for metric, threshold in JUDGE_THRESHOLDS.items():
            score = judge_metrics.get(metric)
            if score is None:
                print(f"  {metric:<30s}: NOT FOUND — skipped.")
                continue
            status = "PASS" if score >= threshold else "FAIL"
            print(
                f"  {metric:<30s}: {score:.2f}  "
                f"(threshold >= {threshold:.2f})  [{status}]"
            )
            if score < threshold:
                failures.append(
                    f"Judge {metric}: {score:.2f} < threshold {threshold:.2f}"
                )
    else:
        logger.warning("No judge run found. Skipping judge threshold checks.")

    # ── Final verdict ──────────────────────────────────────────────────────────
    print()
    if failures:
        print(f"[GATE FAILED] {len(failures)} threshold(s) not met:")
        for msg in failures:
            print(f"  - {msg}")
        print("\nDeployment is BLOCKED. Resolve quality issues before deploying.")
        return 1
    else:
        print("[GATE PASSED] All thresholds met. Deployment is APPROVED.")
        return 0


# ── Entry point ────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    sys.exit(run_gate())
