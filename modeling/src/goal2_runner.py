"""CLI runner for Goal 2 artifact generation."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from benchmarking.price_positioning_service import build_price_decision_payload
from feature_engineering.feature_matrix_builder import build_feature_matrix_artifact_versioned
from feature_engineering.model_input_builder import (
    build_model_input_artifact_versioned,
    load_goal2_source_tables,
)
from price_estimation.inference_bundle_builder import build_inference_bundle
from price_estimation.price_model_trainer import train_goal2_models
from price_estimation.training_config import Goal2TrainingConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Goal 2 modeling and benchmarking pipelines.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Repository root containing canonical Goal 1 outputs.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help="Optional output root. Defaults to the repository root.",
    )
    parser.add_argument(
        "--sample-payload",
        action="store_true",
        help="Generate one sample price decision payload after training.",
    )
    parser.add_argument(
        "--version",
        type=str,
        default="goal2_v10_diagnostics",
        help="Version folder name for Goal 2 artifacts.",
    )
    parser.add_argument(
        "--catboost-loss-experiments",
        action="store_true",
        help="Include CatBoost MAE and Huber loss candidates in the validation search.",
    )
    parser.add_argument(
        "--catboost-log-target-experiments",
        action="store_true",
        help="Include CatBoost log1p target-transform candidates in the validation search.",
    )
    parser.add_argument(
        "--catboost-rich-categorical-experiments",
        action="store_true",
        help="Let CatBoost use city, period, and neighbourhood as direct categorical features.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()
    output_root = repo_root if args.output_root is None else args.output_root.resolve()
    version_root = output_root / "data" / "processed" / "airbnb" / "modeling" / args.version

    written_paths = []
    model_input_paths = build_model_input_artifact_versioned(
        repo_root,
        output_root=output_root,
        version=args.version,
    )
    feature_paths = build_feature_matrix_artifact_versioned(
        repo_root,
        output_root=output_root,
        version=args.version,
    )
    training_config = Goal2TrainingConfig(
        catboost_loss_experiments_enabled=args.catboost_loss_experiments,
        catboost_log_target_experiments_enabled=args.catboost_log_target_experiments,
        catboost_rich_categorical_experiments_enabled=args.catboost_rich_categorical_experiments,
        catboost_tuning_max_candidates=(
            6
            + (3 if args.catboost_loss_experiments else 0)
            + (3 if args.catboost_log_target_experiments else 0)
        ),
    )
    training_result = train_goal2_models(repo_root, config=training_config)
    bundle_paths = build_inference_bundle(training_result, version_root, bundle_version=args.version)
    written_paths.extend(model_input_paths.values())
    written_paths.extend(feature_paths.values())
    written_paths.extend(bundle_paths.values())

    if args.sample_payload:
        sources = load_goal2_source_tables(repo_root)
        target_listing = training_result.test_frame.iloc[0]
        artifact_by_name = {
            artifact.model_name: artifact
            for artifact in training_result.model_artifacts
        }
        champion_pipeline = artifact_by_name[training_result.comparison.champion_model_name].pipeline
        champion_artifact = artifact_by_name[training_result.comparison.champion_model_name]
        champion_feature_columns = artifact_by_name[
            training_result.comparison.champion_model_name
        ].raw_feature_columns
        estimated_market_price = float(
            champion_pipeline.predict(training_result.test_frame.iloc[[0]][champion_feature_columns])[0]
        )
        payload = build_price_decision_payload(
            feature_frame=training_result.feature_frame,
            target_listing=target_listing,
            estimated_market_price=estimated_market_price,
            champion_model_name=training_result.comparison.champion_model_name,
            fallback_model_name=training_result.comparison.fallback_model_name,
            linear_explanation_context=training_result.linear_explanation_context,
            neighbourhood_period_summary=sources["neighbourhood_period_summary"],
            city_period_summary=sources["city_period_summary"],
            model_estimate_interval_calibration=champion_artifact.evaluation.metadata.get("prediction_interval"),
        )
        payload_path = version_root / "sample_price_decision_payload.yaml"
        payload_path.parent.mkdir(parents=True, exist_ok=True)
        with payload_path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(payload, handle, sort_keys=False, allow_unicode=True)
        written_paths.append(payload_path)

    for path in written_paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
