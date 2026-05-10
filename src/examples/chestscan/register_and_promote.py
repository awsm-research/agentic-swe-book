# register_and_promote.py
# Full model registration and promotion workflow for the ChestScan pneumonia detector.
#
# Stages:
#   1. Automated evaluation gate — reads metrics from MLflow, exits if thresholds not met.
#   2. Register model in MLflow Model Registry.
#   3. Assign @staging alias — model is visible but not yet serving production traffic.
#   4. Prompt for human clinical review (radiologist reviews Grad-CAM heatmaps in MLflow UI).
#   5. If approved: promote to @champion — serving code picks up the new version automatically.
#
# Usage:
#   python register_and_promote.py --run-id <RUN_ID>
#   python register_and_promote.py --run-id <RUN_ID> --auto-promote  # CI only

import argparse
import sys

import mlflow
from mlflow.tracking import MlflowClient

from gate import run_gate


# ---------------------------------------------------------------------------
# Registry operations
# ---------------------------------------------------------------------------

def promote_to_champion(
    model_name: str,
    version: int,
    client: MlflowClient,
) -> None:
    """Assign the @champion alias to the specified model version.

    Removes any existing @champion alias first (only one version can hold it).
    The serving code references models:/chestscan-pneumonia-detector@champion — this
    operation updates what that URI resolves to without any code change in the backend.

    Args:
        model_name: registered model name in the MLflow registry.
        version:    version number to promote.
        client:     MlflowClient instance.
    """
    # Remove existing champion alias if it exists
    try:
        current = client.get_model_version_by_alias(model_name, "champion")
        current_version = current.version
        client.delete_registered_model_alias(model_name, "champion")
        client.update_model_version(
            name=model_name,
            version=current_version,
            description=f"Archived: superseded by version {version}",
        )
        print(f"  Archived previous @champion (version {current_version})")
    except mlflow.exceptions.MlflowException:
        print("  No existing @champion — this is the first production model.")

    # Promote new version
    client.set_registered_model_alias(model_name, "champion", version)
    print(f"  @champion -> version {version}")

    # Remove @staging alias (model has graduated to production)
    try:
        client.delete_registered_model_alias(model_name, "staging")
    except mlflow.exceptions.MlflowException:
        pass


def register_and_stage(
    run_id: str,
    model_name: str,
    client: MlflowClient,
) -> int:
    """Register a model from a completed training run and assign @staging alias.

    Args:
        run_id:     source MLflow training run ID.
        model_name: name to register the model under in the registry.
        client:     MlflowClient instance.

    Returns:
        The integer version number assigned by the registry.
    """
    model_uri = f"runs:/{run_id}/model"
    mv = mlflow.register_model(
        model_uri=model_uri,
        name=model_name,
        tags={
            "source_run_id": run_id,
            "architecture": "davit",
            "framework": "pytorch",
            "task": "chest-xray-3class",
        },
    )
    version = int(mv.version)
    client.set_registered_model_alias(model_name, "staging", version)
    print(f"  Registered version {version} with alias @staging")
    return version


def human_review_prompt(
    model_name: str,
    version: int,
    mlflow_uri: str,
) -> bool:
    """Interactive prompt for human clinical review before promotion.

    The reviewer should inspect Grad-CAM heatmaps in the MLflow UI to confirm
    that heatmaps highlight clinically plausible lung regions rather than
    image borders, text annotations, or radiograph markers.

    Args:
        model_name: registered model name.
        version:    model version to review.
        mlflow_uri: MLflow UI base URL.

    Returns:
        True if the reviewer approves promotion, False otherwise.
    """
    print()
    print("=" * 65)
    print("HUMAN CLINICAL REVIEW REQUIRED")
    print("=" * 65)
    print(f"Model:   {model_name}  version {version}")
    print(f"Review:  {mlflow_uri}/#/models/{model_name}/versions/{version}")
    print()
    print("Navigate to the Artifacts tab and open the 'gradcam/' folder.")
    print("Verify that heatmaps highlight areas of opacity or consolidation")
    print("within the lung fields — NOT image borders, labels, or markers.")
    print()
    response = input("Approve promotion to @champion? [yes/no]: ").strip().lower()
    return response in ("yes", "y")


# ---------------------------------------------------------------------------
# Main workflow
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Register and promote a ChestScan model version to @champion"
    )
    parser.add_argument(
        "--run-id",
        required=True,
        help="MLflow run_id of the training run to register",
    )
    parser.add_argument(
        "--model-name",
        default="chestscan-pneumonia-detector",
        help="Registered model name in the MLflow Model Registry",
    )
    parser.add_argument(
        "--mlflow-uri",
        default="http://localhost:5000",
        help="MLflow tracking server URI",
    )
    parser.add_argument(
        "--auto-promote",
        action="store_true",
        help="Skip the human review prompt (use in CI with caution — not for clinical deployment)",
    )
    args = parser.parse_args()

    mlflow.set_tracking_uri(args.mlflow_uri)
    client = MlflowClient(tracking_uri=args.mlflow_uri)

    # Stage 1: Automated evaluation gate
    print("Stage 1: Automated Evaluation Gate")
    print("-" * 65)
    passed = run_gate(args.run_id, args.mlflow_uri)
    if not passed:
        print("\nGate failed.  Model will not be registered.  Exiting.")
        sys.exit(1)

    # Stage 2: Register model and assign @staging
    print("\nStage 2: Registering Model in MLflow Registry")
    print("-" * 65)
    version = register_and_stage(args.run_id, args.model_name, client)

    # Stage 3: Human clinical review (or auto-promote for CI)
    if args.auto_promote:
        approved = True
        print("\nAuto-promote flag set — skipping human review.")
        print("WARNING: only use --auto-promote in automated CI pipelines.")
    else:
        approved = human_review_prompt(args.model_name, version, args.mlflow_uri)

    if approved:
        print("\nStage 3: Promoting to @champion")
        print("-" * 65)
        promote_to_champion(args.model_name, version, client)
        print(
            f"\nPromotion complete.\n"
            f"Serving URI: models:/{args.model_name}@champion -> version {version}"
        )
    else:
        print("\nPromotion declined by reviewer.")
        print(f"Model remains at @staging (version {version}) for further review.")
        sys.exit(1)


if __name__ == "__main__":
    main()
