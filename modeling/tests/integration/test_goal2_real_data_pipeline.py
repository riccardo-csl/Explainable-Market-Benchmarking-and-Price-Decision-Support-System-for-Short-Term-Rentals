from pathlib import Path

import pandas as pd

from benchmarking.price_positioning_service import build_price_decision_payload
from feature_engineering.feature_matrix_builder import build_feature_frame
from feature_engineering.model_input_builder import build_model_input_table, load_goal2_source_tables
from price_estimation.inference_bundle_builder import build_inference_bundle, load_inference_bundle
from price_estimation.price_model_trainer import train_models_from_feature_frame
from price_estimation.training_config import Goal2TrainingConfig


REPO_ROOT = Path(__file__).resolve().parents[3]


def test_goal2_pipeline_builds_real_feature_frame_and_sample_payload(tmp_path: Path) -> None:
    sources = load_goal2_source_tables(REPO_ROOT)
    model_input = build_model_input_table(
        sources["listing_snapshot"],
        sources["neighbourhood_reference"],
    )
    feature_frame = build_feature_frame(model_input.dataframe)

    assert len(feature_frame) == 281105
    assert feature_frame["nightly_price"].max() <= 1500.0
    assert "distance_to_city_center_km" in feature_frame.columns
    assert "venezia_group_name" in feature_frame.columns

    sampled_listing_ids = feature_frame["listing_id"].drop_duplicates().head(1200)
    subset = feature_frame[feature_frame["listing_id"].isin(sampled_listing_ids)].reset_index(drop=True)
    training_result = train_models_from_feature_frame(
        subset,
        config=Goal2TrainingConfig(
            tree_max_iter=80,
            catboost_iterations=40,
            importance_sample_size=250,
            benchmark_diagnostic_sample_size=50,
        ),
        neighbourhood_period_summary=sources["neighbourhood_period_summary"],
        city_period_summary=sources["city_period_summary"],
    )
    version_root = tmp_path / "data" / "processed" / "airbnb" / "modeling" / "goal2_subset"
    bundle_paths = build_inference_bundle(training_result, version_root, bundle_version="goal2_subset")
    bundle = load_inference_bundle(bundle_paths["bundle"])

    champion_pipeline = bundle["champion_pipeline"]
    feature_columns = bundle["feature_columns"]
    target_listing = training_result.test_frame.iloc[0]
    estimated_market_price = float(champion_pipeline.predict(pd.DataFrame([target_listing[feature_columns].to_dict()]))[0])
    payload = build_price_decision_payload(
        feature_frame=subset,
        target_listing=target_listing,
        estimated_market_price=estimated_market_price,
        champion_model_name=bundle["champion_model_name"],
        fallback_model_name=bundle["fallback_model_name"],
        linear_explanation_context=training_result.linear_explanation_context,
        neighbourhood_period_summary=sources["neighbourhood_period_summary"],
        city_period_summary=sources["city_period_summary"],
        model_estimate_interval_calibration=bundle["model_estimate_interval_calibration"],
    )

    assert bundle_paths["bundle"].exists()
    assert bundle_paths["bundle"].parent.name == "goal2_subset"
    assert payload["primary_decision_signal"] == "benchmark_range"
    assert payload["decision_policy"] == "benchmark_led_positioning"
    assert payload["model_estimate_role"] == "supporting_signal"
    assert payload["model_estimate_lower_bound"] <= payload["estimated_market_price"]
    assert payload["model_estimate_upper_bound"] >= payload["estimated_market_price"]
    assert payload["model_estimate_interval_source"] == "heldout_residual_quantiles"
    assert payload["model_benchmark_agreement_label"] in {"strong", "medium", "weak"}
    assert payload["model_benchmark_gap_amount"] >= 0.0
    assert payload["price_positioning_label"] in {"underpriced", "aligned", "overpriced"}
    assert len(payload["selected_comparables"]) <= 10
    assert payload["champion_model_name"] in {"linear_baseline", "tree_challenger", "catboost_challenger"}
    assert training_result.catboost_artifact.evaluation.benchmark_positioning_mae
    assert training_result.catboost_artifact.evaluation.model_prediction_inside_benchmark_rate is not None
    assert training_result.catboost_artifact.evaluation.model_positioning_agreement_rate is not None
    assert training_result.catboost_artifact.evaluation.metadata["prediction_interval"]["source"] == "heldout_residual_quantiles"
