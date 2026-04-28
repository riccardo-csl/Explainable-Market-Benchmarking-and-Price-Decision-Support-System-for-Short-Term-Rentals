# Goal 2 Model Handoff

Goal 2 hands off a serialized inference bundle plus shared YAML contracts for Goal 3 backend integration.

## Versioned Artifact Layout

All persisted Goal 2 artifacts are stored under:

- `data/processed/airbnb/modeling/<version>/`

The current repository-backed reference bundle is:

- `data/processed/airbnb/modeling/goal2_v4/`

Earlier local experiment versions are intentionally not retained as project
artifacts. If a future run supersedes `goal2_v4`, update this document and the
backend integration target together.

The expected files inside one version folder are:

- `listing_price_model_input.parquet`
- `listing_price_model_input.csv`
- `listing_price_model_input_metadata.yaml`
- `price_feature_matrix.parquet`
- `price_feature_matrix.csv`
- `price_feature_matrix_metadata.yaml`
- `inference_bundle.joblib`
- `inference_bundle_metadata.yaml`
- `sample_price_decision_payload.yaml`

## Bundle Contents

- champion pipeline
- fallback pipeline
- ordered feature columns
- target and grouping metadata
- model comparison metrics
- linear explanation context

## Shared Contracts

- `shared/contracts/modeling/price_decision_payload.yaml`
- `shared/contracts/modeling/comparable_listing.yaml`
- `shared/contracts/modeling/model_bundle_metadata.yaml`

## Expected Backend Responsibilities in Goal 3

- load the serialized bundle
- accept listing-level input aligned to the Goal 2 feature schema
- produce a benchmark-led pricing response containing benchmark range, positioning label, comparables, local explanation, and a supporting point estimate
- surface champion and fallback metadata for traceability

## Decision Framing

Goal 2 payloads are intentionally benchmark-led.

- `benchmark_lower_bound` and `benchmark_upper_bound` are the primary decision signals
- `price_positioning_label` is derived against the benchmark range
- `estimated_market_price` is retained as a supporting model signal
- payloads explicitly declare this through:
  - `primary_decision_signal`
  - `decision_policy`
  - `decision_signal_summary`
  - `model_estimate_role`

## Important Boundaries

- the bundle expects Goal 1 cleaned field names and Goal 2 derived feature names
- the backend should not recreate ad hoc feature logic outside the modeling module
- benchmark fallback behavior must remain consistent with Goal 2:
  - comparables first
  - neighbourhood-period summary second
  - city-period summary third
