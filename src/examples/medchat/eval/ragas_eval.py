"""
MedChat RAGAS evaluation — Chapter 19.

Runs the four core RAGAS metrics (faithfulness, answer_relevancy,
context_precision, context_recall) over the evaluation dataset and logs
all scores to an MLflow experiment.

Usage:
    export OPENAI_API_KEY="sk-..."
    export DATABASE_URL="postgresql://user:pass@localhost/medchat"
    export MLFLOW_TRACKING_URI="http://localhost:5000"
    python eval/ragas_eval.py
"""

from __future__ import annotations

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Allow importing from the parent medchat directory
sys.path.insert(0, str(Path(__file__).parent.parent))

import mlflow
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from datasets import Dataset

from eval_dataset import get_eval_data, generate_eval_answers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("medchat.ragas_eval")

# ── Quality thresholds (used by the deployment gate) ──────────────────────────

THRESHOLDS = {
    "faithfulness": 0.85,
    "answer_relevancy": 0.80,
    "context_precision": 0.75,
    "context_recall": 0.70,
}

MLFLOW_EXPERIMENT = "medchat-evaluation"


# ── Build RAGAS dataset ────────────────────────────────────────────────────────


def build_ragas_dataset(eval_answers: list[dict]) -> Dataset:
    """
    Convert the eval_answers list into a HuggingFace Dataset suitable for RAGAS.

    RAGAS expects columns: question, answer, contexts (list[str]), ground_truth.
    """
    return Dataset.from_dict(
        {
            "question": [row["question"] for row in eval_answers],
            "answer": [row["answer"] for row in eval_answers],
            "contexts": [row["contexts"] for row in eval_answers],
            "ground_truth": [row["ground_truth"] for row in eval_answers],
        }
    )


# ── Run evaluation ─────────────────────────────────────────────────────────────


def run_ragas_evaluation(
    dataset: Dataset,
    run_name: str | None = None,
) -> dict[str, float]:
    """
    Evaluate the dataset with all four RAGAS metrics and log to MLflow.

    Args:
        dataset:  HuggingFace Dataset with question/answer/contexts/ground_truth.
        run_name: Optional MLflow run name (auto-generated if None).

    Returns:
        Dict mapping metric name to float score.
    """
    if run_name is None:
        run_name = f"ragas-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(MLFLOW_EXPERIMENT)

    with mlflow.start_run(run_name=run_name):
        mlflow.log_params(
            {
                "dataset_size": len(dataset),
                "metrics": "faithfulness,answer_relevancy,context_precision,context_recall",
            }
        )

        logger.info(f"Running RAGAS on {len(dataset)} examples…")

        result = evaluate(
            dataset=dataset,
            metrics=[
                faithfulness,
                answer_relevancy,
                context_precision,
                context_recall,
            ],
        )

        scores: dict[str, float] = {
            "faithfulness": float(result["faithfulness"]),
            "answer_relevancy": float(result["answer_relevancy"]),
            "context_precision": float(result["context_precision"]),
            "context_recall": float(result["context_recall"]),
        }

        mlflow.log_metrics(scores)

        # Log threshold pass/fail per metric
        all_passed = True
        for metric, score in scores.items():
            threshold = THRESHOLDS.get(metric, 0.0)
            passed = score >= threshold
            mlflow.log_metric(f"{metric}_passed", float(passed))
            if not passed:
                all_passed = False
                logger.warning(
                    f"THRESHOLD FAIL: {metric} = {score:.3f} "
                    f"(threshold: {threshold:.3f})"
                )
            else:
                logger.info(
                    f"Threshold OK:   {metric} = {score:.3f} "
                    f"(threshold: {threshold:.3f})"
                )

        mlflow.log_metric("all_thresholds_passed", float(all_passed))

        # Save the per-row detail as a CSV artifact
        try:
            detail_path = "ragas_results_detail.csv"
            result.to_pandas().to_csv(detail_path, index=False)
            mlflow.log_artifact(detail_path)
        except Exception as exc:
            logger.warning(f"Could not save detail CSV: {exc}")

    return scores


# ── Pretty-print results ───────────────────────────────────────────────────────


def print_results(scores: dict[str, float]) -> None:
    print("\n" + "=" * 55)
    print("RAGAS Evaluation Results")
    print("=" * 55)
    for metric, score in scores.items():
        threshold = THRESHOLDS.get(metric, 0.0)
        status = "PASS" if score >= threshold else "FAIL"
        print(
            f"  {metric:<25s}: {score:.3f}  "
            f"(threshold {threshold:.3f})  [{status}]"
        )
    print("=" * 55)


# ── Entry point ────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    eval_data = get_eval_data()
    logger.info(f"Generating RAG answers for {len(eval_data)} evaluation questions…")
    eval_answers = generate_eval_answers(eval_data)

    dataset = build_ragas_dataset(eval_answers)
    scores = run_ragas_evaluation(dataset)
    print_results(scores)
