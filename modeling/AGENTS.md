# Agent instructions (scope: this directory and subdirectories)

## Scope and ownership
- This AGENTS.md applies to `/home/arch/Scrivania/archive/modeling` and below.
- This module owns feature engineering, training pipelines, evaluation logic, comparable-listing algorithms, clustering experiments, and model reports.
- Primary stack: Python.

## Expected layout
- `src/`
  Reusable modeling code.
- `src/features/`
  Feature engineering and transformations.
- `src/models/`
  Model definitions and training workflows.
- `src/evaluation/`
  Metrics, validation logic, and comparison reports.
- `src/pipelines/`
  Reproducible training and inference pipelines.
- `reports/`
  Generated evaluation outputs and model summaries.
- `tests/`
  Modeling unit and pipeline tests.

## Commands
- Use Python project tooling consistent with the root project setup once initialized.
- Preferred test framework: `pytest`.
- Prefer reproducible scripts or pipelines over ad hoc notebook execution.

## Conventions
- Keep notebooks exploratory only. Move reusable logic into importable source files.
- Separate feature engineering, model training, evaluation, and inference code.
- Use explicit filenames such as `micro_market_clusterer`, `price_estimation_trainer`, `benchmark_range_evaluator`.
- Make pipelines reproducible and deterministic where possible.
- Document assumptions and limitations for every estimator or clustering workflow.

## Testing
- Test feature transformations directly.
- Test model selection and evaluation logic with deterministic fixtures.
- Add regression coverage for any pricing rule, similarity score, or clustering heuristic.
- Keep modeling coverage at or above `85%` for source modules that are part of the productized workflow.

## Do not
- Do not leave production logic trapped inside notebooks.
- Do not use ad hoc scripts as the only execution path for training or evaluation.
- Do not claim unsupported capabilities such as occupancy forecasting or elasticity estimation.
