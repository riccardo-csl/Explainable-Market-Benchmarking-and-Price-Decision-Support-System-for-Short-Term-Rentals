# Goal 2 Scope

Goal 2 implements an explainable market benchmarking and price decision-support engine for short-term rentals.

The implemented scope includes:

- canonical Goal 2 modeling input assembly from the cleaned Goal 1 datasets
- reusable feature engineering for listing-level price estimation
- grouped train and test splitting by `listing_id`
- two baseline estimators:
  - `linear_baseline` using `ElasticNet`
  - `tree_challenger` using `HistGradientBoostingRegressor`
- explicit champion and fallback model selection
- comparable listing retrieval
- benchmark range calculation with robust comparable and aggregate fallbacks
- price positioning classification
- local explanation payloads backed by the linear baseline
- serialized inference bundle and shared payload contracts

The implemented scope does not include:

- backend API serving
- frontend dashboard integration
- occupancy, revenue, or elasticity modeling
- dynamic pricing claims
- event- or lead-time-aware forecasting

## Selection Policy

- `linear_baseline` remains the default champion unless the tree challenger improves held-out MAE by at least 5 percent and does not materially worsen city-level stability.
- Both models are retained in the bundle so that Goal 3 can expose a documented fallback path.

## Benchmark Policy

- if comparables are numerous, use quartile-based local benchmark ranges
- if comparables are moderate, use median plus or minus scaled MAD
- if comparables are sparse, fall back to neighbourhood-period summary and then city-period summary

## Explanation Policy

- global model comparison uses held-out MAE and RMSE with sliced reporting
- local explanation payloads are generated from linear contributions for readability and operational stability

## Artifact Versioning

- every persisted Goal 2 run is saved in its own version folder
- the version folder name is provided by the runner through `--version`
- the current repository-backed reference version is `goal2_v4`
