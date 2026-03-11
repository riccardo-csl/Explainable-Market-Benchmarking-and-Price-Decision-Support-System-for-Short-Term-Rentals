# Goal 2 Operational Plan: Price Estimation and Benchmarking Engine

## Goal

Build the modeling core of the project: an explainable price estimation and market benchmarking engine that uses the cleaned Airbnb datasets to produce market-aligned price estimates, benchmark ranges, comparable listing support, and model evaluation artifacts that can later be integrated into the backend and dashboard.

## Assumptions and Constraints

- The cleaned datasets produced in `data/processed/airbnb/` are the canonical analytical inputs.
- Goal 2 is about price estimation and benchmarking, not true revenue management.
- No occupancy, booking conversion, elasticity, or dynamic pricing claims will be implemented or implied.
- The preferred modeling stack is Python with `pandas`, `scikit-learn`, and standard experiment tooling inside `modeling/`.
- The system must remain interpretable enough to explain the main drivers of the estimated price.
- Every new modeling component must ship with tests, and project coverage must remain at or above `85%`.

## Research (Current State)

- Cleaned analytical datasets already exist under `data/processed/airbnb/csv/` and `data/processed/airbnb/parquet/`.
- The current cleaning logic and dataset generation live in [cleaned_dataset_builder.py](/home/arch/Scrivania/archive/modeling/src/data_foundation/cleaned_dataset_builder.py), [cleaned_dataset_runner.py](/home/arch/Scrivania/archive/modeling/src/data_foundation/cleaned_dataset_runner.py), and [normalization.py](/home/arch/Scrivania/archive/modeling/src/data_foundation/normalization.py).
- Cleaned output contracts already exist under [target_cleaned_datasets](/home/arch/Scrivania/archive/shared/contracts/data/target_cleaned_datasets).
- The most useful human-readable data mapping now lives in [raw_to_cleaned_feature_mapping.md](/home/arch/Scrivania/archive/docs/data/raw_to_cleaned_feature_mapping.md).
- There is not yet any dedicated Goal 2 modeling package for feature engineering, training, evaluation, explainability, comparable listings, or model artifact packaging.

## Analysis

### Options

1. Build a pure ML price regressor and treat the benchmark as a post-processing view.
   This is simple to implement, but it weakens interpretability and gives a thin answer to the benchmarking part of the goal.

2. Build only a comparable-listing benchmark engine without a supervised model.
   This is easy to explain, but it underuses the data and makes the project look weaker technically.

3. Build a hybrid system with three parts: a supervised price estimator, a comparable-listing engine, and a benchmark-range layer.
   This is the strongest option because it matches the project goal, stays explainable, and gives multiple useful outputs for the product.

### Decision

Chosen approach: option 3, a hybrid modeling engine.

Why:

- it aligns with the current PoS wording
- it uses the cleaned datasets well
- it supports both a predicted price and a market benchmark
- it remains defensible given the available data
- it gives natural outputs for Goal 3 integration

### Risks and Edge Cases

- High-cardinality neighbourhood labels may overfit if encoded naively.
- Small local slices may produce unstable benchmark ranges.
- Cross-city differences may dominate weaker property-level features.
- Leakage can happen if grouped benchmark fields are used carelessly in listing-level prediction.
- Venice-only fields such as `neighbourhood_group_name` should not become global modeling assumptions.
- Feature engineering can drift away from the cleaned contracts if the pipeline is not kept modular.

### Open Questions

There are no blocking questions for planning. The implementation can proceed under the assumptions above.

## End-to-End Phase Plan

## Phase 1: Modeling Scope Freeze and Acceptance Gates

The first phase should lock the exact Goal 2 outputs before code is written. The team should define what the engine must return and what will count as a successful first version.

Expected outputs:

- one documented modeling scope note in `docs/modeling/`
- one acceptance checklist for Goal 2
- one target output definition covering:
  - estimated market price
  - benchmark range
  - comparable listings
  - price positioning label
  - explanation payload

Recommended implementation paths:

- `docs/modeling/price_estimation_scope.md`
- `shared/contracts/modeling/` for future model output contracts

Exit criteria:

- the team agrees on target outputs and non-goals
- the selected evaluation metrics are frozen
- the implementation order for the remaining phases is approved

## Phase 2: Modeling Dataset Assembly

This phase should create the listing-level modeling table that all later training and evaluation steps will use. The goal is to build one reproducible dataset with stable joins and explicit exclusions.

Work to complete:

- load `listing_snapshot`
- decide which fields are raw modeling inputs and which are metadata only
- join city-level and neighbourhood-level benchmark context only where safe and non-leaky
- document any excluded columns and why they were excluded
- produce one canonical modeling dataset and one metadata report

Recommended derived outputs:

- `data/processed/airbnb/modeling/listing_price_model_input.parquet`
- `docs/modeling/model_input_spec.md`

Recommended code locations:

- `modeling/src/feature_engineering/model_input_builder.py`
- `modeling/src/feature_engineering/model_input_contracts.py`

Exit criteria:

- one canonical modeling dataset exists
- row counts and join rates are documented
- leakage-sensitive fields are marked or excluded

Tests:

- unit tests for join logic and exclusions
- integration test that builds the modeling dataset from the cleaned CSV or Parquet layer

## Phase 3: Exploratory Analysis and Leakage Audit

This phase should answer two questions before feature engineering expands: what drives price in the cleaned data, and which variables are unsafe or unstable for supervised modeling.

Work to complete:

- inspect target distribution for `nightly_price`
- profile missingness and outliers
- inspect city-level and neighbourhood-level distribution shifts
- check which columns are too sparse, too noisy, or too target-adjacent
- audit candidate context features for leakage risk
- define the baseline train-validation-test strategy

Recommended outputs:

- exploratory notebook for temporary analysis only
- reproducible summary code in normal source files
- one markdown report with charts exported or summarized

Recommended code locations:

- `modeling/src/evaluation/data_profile_report.py`
- `modeling/src/evaluation/leakage_audit.py`
- `docs/modeling/price_model_data_profile.md`

Exit criteria:

- the target variable is profiled and understood
- the split strategy is frozen
- leakage-sensitive fields are explicitly listed

Tests:

- unit tests for profiling helpers
- regression tests for leakage-audit rules

## Phase 4: Feature Engineering Layer

This is the phase where new modeling features should be created. It should be strictly separated from data cleaning. The output should be a feature matrix that can be reused across multiple models.

Feature groups to implement first:

- structural listing features:
  - `accommodates_count`
  - `beds_count`
  - `bedrooms_count`
  - `bathrooms_count`
  - `room_type`
  - `bathroom_type`
- host and review features:
  - `host_listing_count`
  - `is_superhost`
  - `total_reviews`
  - `reviews_last_twelve_months`
  - `reviews_per_month`
  - review score family
- temporal context:
  - `period_label`
  - snapshot-based seasonal indicators
- location context:
  - `city_name`
  - `neighbourhood_name`
  - latitude and longitude transforms
  - distance-to-centroid style features
  - optional city-conditional macro-area features
- benchmark context:
  - neighbourhood median price context
  - city median price context
  - local spread metrics

Feature rules:

- Venice-specific fields such as `neighbourhood_group_name` may be used only as city-conditional features or Venice-only analysis fields
- grouped summary features must be introduced carefully to avoid building circular target proxies
- all engineered features must be versioned and documented

Recommended code locations:

- `modeling/src/feature_engineering/listing_feature_builder.py`
- `modeling/src/feature_engineering/location_feature_builder.py`
- `modeling/src/feature_engineering/context_feature_builder.py`
- `modeling/src/feature_engineering/feature_registry.py`

Recommended outputs:

- `data/processed/airbnb/modeling/price_feature_matrix.parquet`
- `docs/modeling/feature_catalog.md`

Exit criteria:

- one reusable feature matrix exists
- every engineered feature is documented
- the first feature set is small enough to remain interpretable

Tests:

- unit tests for each feature builder
- regression tests for deterministic feature generation
- integration test for full feature matrix generation

## Phase 5: Comparable Listings Engine

This phase should build the non-parametric part of the system: given a listing, find the most relevant comparable listings and use them to support market benchmarking and explanation.

Work to complete:

- define similarity rules and weights
- choose the minimum set of similarity dimensions
- build a nearest-neighbour or rules-based comparable retrieval engine
- produce a ranked comparable set with similarity scores
- ensure the output is readable enough for UI use later

Minimum comparable dimensions:

- city
- neighbourhood or local location proxy
- room type
- accommodates count
- beds and bedrooms where available
- review quality proxies

Recommended code locations:

- `modeling/src/benchmarking/listing_similarity_engine.py`
- `modeling/src/benchmarking/comparable_listing_selector.py`

Recommended outputs:

- comparable selection artifacts
- similarity score schema
- sample comparable outputs for documentation

Exit criteria:

- the engine returns stable comparable sets for a test sample
- similarity logic is documented and explainable

Tests:

- unit tests for similarity scoring
- edge-case tests for sparse or missing feature combinations
- integration test returning comparable listings for fixture inputs

## Phase 6: Baseline Model Training

This phase should establish the baseline supervised estimators that all later comparisons will use.

Models to implement first:

- regularized linear regression baseline
- one tree-based baseline such as random forest or gradient boosting

Modeling rules:

- use the same feature matrix for all baseline models
- define one standard evaluation split strategy
- keep the first pass narrow and interpretable

Recommended code locations:

- `modeling/src/price_estimation/price_model_trainer.py`
- `modeling/src/price_estimation/model_registry.py`
- `modeling/src/price_estimation/training_config.py`

Recommended outputs:

- trained baseline model artifacts
- one model comparison report
- one experiment summary table

Exit criteria:

- at least two baseline models are trained successfully
- MAE and RMSE are available on held-out data
- feature importances or coefficients can be inspected

Tests:

- unit tests for training configuration and data preparation
- integration tests for end-to-end training on fixtures

## Phase 7: Model Comparison and Selection

This phase should choose the primary estimation model using explicit criteria instead of informal preference.

Selection criteria:

- out-of-sample MAE
- out-of-sample RMSE
- stability across cities
- stability across seasonal snapshots
- interpretability of the feature effects
- operational simplicity for later integration

Work to complete:

- run model comparison on the frozen split strategy
- compare global performance and per-city performance
- document failure modes and biased error pockets
- choose one primary model and one fallback model

Recommended code locations:

- `modeling/src/evaluation/model_comparison_report.py`
- `modeling/src/evaluation/per_city_error_report.py`

Recommended outputs:

- `docs/modeling/model_selection_report.md`
- one serialized evaluation artifact for later use by Goal 3

Exit criteria:

- one primary model is selected
- one fallback model is documented
- the choice is justified by metrics and interpretability, not only raw accuracy

Tests:

- regression tests for metric calculations
- integration tests for comparison report generation

## Phase 8: Benchmark Range and Price Positioning Layer

This phase should convert model and comparable outputs into product-facing signals. The goal is to move from pure prediction to decision support.

Work to complete:

- define benchmark range logic
- define the underpriced / aligned / overpriced decision rule
- combine comparable results and model estimate into one pricing view
- document how benchmark range differs from point estimate

Recommended outputs:

- point estimate
- benchmark lower bound
- benchmark upper bound
- price positioning label
- supporting comparable listings

Recommended code locations:

- `modeling/src/benchmarking/benchmark_range_calculator.py`
- `modeling/src/benchmarking/price_positioning_service.py`

Exit criteria:

- the engine can produce a complete decision-support payload for one listing
- the benchmark range logic is consistent and documented

Tests:

- unit tests for range calculation
- edge-case tests for sparse comparables
- regression tests for positioning thresholds

## Phase 9: Explainability and Error Analysis

This phase should make the system defensible and inspectable. The goal is not only to know the estimated price, but also to explain why it was produced and where the model is weak.

Work to complete:

- produce global feature importance summaries
- produce local explanation payloads for sample listings
- segment errors by city, room type, and price band
- identify failure cases where the comparable engine or model is weak
- document safe interpretation boundaries

Recommended code locations:

- `modeling/src/explainability/feature_effect_report.py`
- `modeling/src/explainability/local_explanation_builder.py`
- `modeling/src/evaluation/error_slice_report.py`

Recommended outputs:

- `docs/modeling/explainability_report.md`
- `docs/modeling/error_analysis_report.md`
- reusable explanation payloads for backend integration

Exit criteria:

- the primary drivers of price are documented
- local explanation payloads exist for representative examples
- model weaknesses are explicitly recorded

Tests:

- unit tests for explanation payload formatters
- regression tests for error-slice calculations

## Phase 10: Packaging, Reproducibility, and Handoff

The last phase should turn the modeling work into something that Goal 3 can consume without re-implementing logic.

Work to complete:

- package the selected model and any required preprocessing artifacts
- define the input and output schema for inference
- freeze model versioning and artifact naming
- produce one inference-ready service payload specification
- document runtime assumptions for backend integration

Recommended code locations:

- `modeling/src/price_estimation/inference_bundle_builder.py`
- `shared/contracts/modeling/price_estimation_payload.yaml`
- `docs/modeling/model_handoff.md`

Recommended outputs:

- versioned model artifact bundle
- versioned inference schema
- backend handoff document

Exit criteria:

- a backend engineer can call the model without reverse-engineering notebook logic
- model inputs, outputs, and versioning are documented
- all Goal 2 artifacts are reproducible from source data and code

Tests:

- integration test for artifact serialization and reload
- inference smoke test using the packaged bundle

## Test Strategy Across the Whole Goal

The Goal 2 implementation should use three test layers:

- unit tests for feature transforms, similarity logic, metric calculations, and payload builders
- integration tests for dataset assembly, feature matrix generation, training, evaluation, and inference packaging
- regression tests for leakage checks, range calculations, and known edge-case listings

The recommended test locations are:

- `modeling/tests/unit/`
- `modeling/tests/integration/`
- `tests/` only if later phases require cross-module or end-to-end coverage

## Suggested Delivery Order

The safest implementation order is:

1. Phase 1 and Phase 2
2. Phase 3
3. Phase 4
4. Phase 5
5. Phase 6
6. Phase 7
7. Phase 8
8. Phase 9
9. Phase 10

This order keeps the work modular and avoids training models before the feature and benchmark foundations are stable.

## Definition of Done for Goal 2

Goal 2 should be considered complete only when all of the following are true:

- one canonical modeling dataset and one reusable feature matrix exist
- at least one regularized linear baseline and one tree-based baseline have been trained and compared
- one primary model and one fallback model have been selected using explicit criteria
- the comparable listings engine returns stable results
- the benchmark range and price positioning logic are implemented
- explainability and error analysis artifacts exist
- the inference bundle and payload schema are documented for backend handoff
- tests pass and coverage remains at or above `85%`
