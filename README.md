# Explainable Market Benchmarking for Short-Term Rentals

This repository contains the final local beta for the analytics capstone project. The system supports price decision-making for short-term rental listings by combining a benchmark-led pricing policy, comparable listings, local explanations, and a supporting machine-learning estimate.

The project is intended to run locally from a clean checkout. It includes:

- `data/`: raw and processed Airbnb datasets plus the current model artifacts.
- `modeling/`: Python pipeline for data preparation, feature engineering, model training, benchmarking, and artifact generation.
- `backend/`: FastAPI service that loads the current modeling artifacts and exposes the local beta API.
- `frontend/`: Next.js dashboard for inspecting existing listings and price-decision payloads.
- `shared/`: YAML contracts for data and modeling payloads.
- `tests/`: cross-module smoke tests for the local beta.

## Project Scope

The implemented product is a local decision-support beta. It does not claim dynamic pricing automation, occupancy forecasting, revenue optimization, elasticity modeling, authentication, persistence, or manual listing onboarding.

The main decision signal is the benchmark range built from comparable listings and aggregate fallbacks. The model estimate is intentionally shown as supporting evidence, not as the primary pricing decision.

## Requirements

- Python `3.13`
- Node.js and npm
- A shell from the repository root: `Analytic_capstone_proj`

No database or external service is required. The backend reads local parquet and model artifact files from `data/processed/airbnb/`.

## Clean Setup From Scratch

From the repository root:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e "modeling[dev]"
python -m pip install -e "backend[dev]"
```

Install the frontend dependencies:

```bash
cd frontend
npm install
cd ..
```

## Required Runtime Artifacts

The backend default artifact version is:

```text
goal2_v10_diagnostics
```

The following files must exist before starting the API:

```text
data/processed/airbnb/modeling/goal2_v10_diagnostics/inference_bundle.joblib
data/processed/airbnb/modeling/goal2_v10_diagnostics/inference_bundle_metadata.yaml
data/processed/airbnb/modeling/goal2_v10_diagnostics/price_feature_matrix.parquet
data/processed/airbnb/parquet/city_period_summary.parquet
data/processed/airbnb/parquet/neighbourhood_period_summary.parquet
```

The repository also contains the current cleaned parquet datasets used by modeling and serving:

```text
data/processed/airbnb/parquet/listing_snapshot.parquet
data/processed/airbnb/parquet/city_period_summary.parquet
data/processed/airbnb/parquet/neighbourhood_period_summary.parquet
data/processed/airbnb/parquet/neighbourhood_reference.parquet
data/processed/airbnb/parquet/neighbourhood_boundary.parquet
```

## Regenerate the Model Artifacts

This step is optional if the included `goal2_v10_diagnostics` artifacts are already present. Run it when you want to rebuild the current modeling bundle from the processed data.

```bash
source .venv/bin/activate
cd modeling
PYTHONPATH=src python -m goal2_runner \
  --repo-root .. \
  --output-root .. \
  --version goal2_v10_diagnostics \
  --sample-payload \
  --catboost-rich-categorical-experiments
cd ..
```

This writes the serving artifacts under:

```text
data/processed/airbnb/modeling/goal2_v10_diagnostics/
```

The current champion model is `catboost_challenger`. The linear baseline remains available as the fallback and explanation model.

## Run the Backend API

Open one terminal from the repository root:

```bash
source .venv/bin/activate
cd backend
PYTHONPATH=src:../modeling/src python -m uvicorn main:app --reload --port 8000
```

Optional environment variables:

```bash
export GOAL4_REPO_ROOT=/absolute/path/to/Analytic_capstone_proj
export GOAL4_ARTIFACT_VERSION=goal2_v10_diagnostics
```

API endpoints:

- `GET http://localhost:8000/health`
- `GET http://localhost:8000/api/model/metadata`
- `GET http://localhost:8000/api/listings?city_name=Roma&period_label=Early%20Spring&limit=10`
- `GET http://localhost:8000/api/price-decisions?listing_id=<id>&snapshot_date=<YYYY-MM-DD>`

Expected health response:

```json
{
  "status": "ok",
  "artifacts_available": true,
  "artifact_version": "goal2_v10_diagnostics"
}
```

## Run the Frontend Dashboard

Keep the backend running on port `8000`. Open a second terminal from the repository root:

```bash
cd frontend
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
```

Then open:

```text
http://localhost:3000
```

Dashboard workflow:

1. Select or filter listings by city and period.
2. Choose an existing listing.
3. Inspect property details, benchmark range, price positioning, model estimate interval, model-vs-benchmark agreement, comparable listings, and explanation drivers.

## Run Tests

Backend unit and integration tests:

```bash
source .venv/bin/activate
cd backend
python -m pytest -q
cd ..
```

Modeling tests:

```bash
source .venv/bin/activate
cd modeling
python -m pytest -q
cd ..
```

Frontend tests:

```bash
cd frontend
npm run test:coverage
cd ..
```

Cross-module smoke test:

```bash
source .venv/bin/activate
cd tests
python -m pytest -q
cd ..
```

## Full Professor Execution Checklist

For a complete clean run:

1. Create and activate the Python virtual environment.
2. Install `modeling` and `backend` with pip.
3. Install frontend packages with `npm install`.
4. Confirm the `goal2_v10_diagnostics` artifact files exist.
5. Optionally regenerate the modeling bundle with `goal2_runner`.
6. Run backend tests.
7. Run modeling tests.
8. Run frontend tests.
9. Run cross-module smoke tests.
10. Start the FastAPI backend on port `8000`.
11. Start the Next.js frontend on port `3000`.
12. Open the dashboard and select a listing to inspect the final price-decision workflow.

## Modeling Summary

The modeling pipeline builds one row per `(listing_id, snapshot_date)`, excludes listings with `nightly_price > 1500`, and trains three estimator families:

- `linear_baseline` with ElasticNet
- `tree_challenger` with HistGradientBoostingRegressor
- `catboost_challenger` with CatBoostRegressor

The promoted artifact version is `goal2_v10_diagnostics`. It uses `city_name`, `period_label`, and `neighbourhood_name` as direct CatBoost categorical features. The current CatBoost champion metrics are:

| Model | MAE | RMSE |
| --- | ---: | ---: |
| `linear_baseline` | 60.13 | 110.63 |
| `tree_challenger` | 49.07 | 96.71 |
| `catboost_challenger` | 47.77 | 94.06 |

Operational diagnostics for the current champion include:

| Diagnostic | Value |
| --- | ---: |
| MAPE | 32.90 |
| Prediction inside benchmark range rate | 0.592 |
| Model-vs-benchmark positioning agreement rate | 0.620 |
| Aligned-position MAE | 29.35 |
| Underpriced-position MAE | 52.31 |
| Overpriced-position MAE | 77.98 |

## Pricing Policy

The pricing response is benchmark-led:

- comparables are the preferred benchmark source;
- if comparables are sparse, the system falls back to neighbourhood-period summaries;
- if needed, it then falls back to city-period summaries;
- `benchmark_lower_bound` and `benchmark_upper_bound` are the primary decision range;
- `estimated_market_price` and the model estimate interval are supporting signals;
- `model_benchmark_agreement_label` reports whether the model estimate strongly, moderately, or weakly agrees with the benchmark range.

## Troubleshooting

If the backend health endpoint returns `artifacts_available=false`, check that the required files under `data/processed/airbnb/modeling/goal2_v10_diagnostics/` exist.

If the frontend shows an API error, confirm that the backend is running on `http://localhost:8000` and that `NEXT_PUBLIC_API_BASE_URL` matches that URL.

If tests fail after regenerating artifacts, rerun the backend and cross-module tests after stopping any stale server process using port `8000`.
