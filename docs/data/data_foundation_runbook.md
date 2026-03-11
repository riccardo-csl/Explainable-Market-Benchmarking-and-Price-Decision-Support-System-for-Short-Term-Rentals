# Data Foundation Runbook

This runbook explains how to rebuild the Goal 1 data layer from the command line.

All commands below are run from the `modeling/` directory and use the repository root as both input and output root.

## Prerequisites

- Python environment with the dependencies declared in `modeling/pyproject.toml`
- repository root at `/home/arch/Scrivania/archive`

## 1. Regenerate the Source Registry and Cleaned Contracts

This step refreshes:

- `shared/contracts/data/source_dataset_registry.yaml`
- `shared/contracts/data/target_cleaned_datasets/*.yaml`
- `docs/data/source_dataset_inventory.md`
- `docs/data/cleaned_data_contracts.md`

Command:

```bash
cd /home/arch/Scrivania/archive/modeling
PYTHONPATH=src python -m data_foundation.dataset_inventory_runner \
  --repo-root /home/arch/Scrivania/archive \
  --output-root /home/arch/Scrivania/archive
```

Success looks like:

- printed paths for the registry, contracts, and generated docs
- refreshed files under `shared/contracts/data/`
- refreshed `source_dataset_inventory.md` and `cleaned_data_contracts.md`

## 2. Regenerate Raw Provenance Manifests

This step refreshes:

- `data/raw/_manifests/*.yaml`
- source registry and inventory outputs from step 1

Command:

```bash
cd /home/arch/Scrivania/archive/modeling
PYTHONPATH=src python -m data_foundation.raw_data_catalog_runner \
  --repo-root /home/arch/Scrivania/archive \
  --output-root /home/arch/Scrivania/archive \
  --import-date 2026-03-11
```

Success looks like:

- one manifest per raw dataset under `data/raw/_manifests/`
- dataset checksums and file metadata present in the manifests

Note:

`--import-date` may be changed to the actual execution date if needed.

## 3. Regenerate the Cleaned Datasets

This step rebuilds:

- `data/processed/airbnb/csv/*.csv`
- `data/processed/airbnb/parquet/*.parquet`
- `data/processed/airbnb/_manifests/*.yaml`

Command:

```bash
cd /home/arch/Scrivania/archive/modeling
PYTHONPATH=src python -m data_foundation.cleaned_dataset_runner \
  --repo-root /home/arch/Scrivania/archive \
  --output-root /home/arch/Scrivania/archive \
  --generation-date 2026-03-11
```

Success looks like:

- all five cleaned datasets exist in both CSV and Parquet form
- one processed manifest exists per cleaned dataset

## 4. Rerun Cleaned Dataset Validation

This step validates the current cleaned outputs and writes:

- `data/processed/airbnb/_quality/validation_report.yaml`
- `docs/data/cleaned_dataset_validation_summary.md`

Command:

```bash
cd /home/arch/Scrivania/archive/modeling
PYTHONPATH=src python -m data_foundation.cleaned_dataset_validation_runner \
  --repo-root /home/arch/Scrivania/archive \
  --output-root /home/arch/Scrivania/archive \
  --validation-date 2026-03-11
```

Success looks like:

- the command exits with code `0`
- the YAML quality report is written
- the Markdown validation summary is written
- the overall status in the summary is `passed`

## 5. Run the Modeling Test Suite

This verifies that the data foundation code still passes its automated checks.

Command:

```bash
cd /home/arch/Scrivania/archive/modeling
PYTHONPATH=src python -m pytest
```

Success looks like:

- all tests pass
- total coverage remains at or above `85%`

## Expected Final State

After all steps complete successfully, the repository should contain:

- canonical raw manifests
- canonical cleaned datasets
- processed dataset manifests
- a passing cleaned dataset validation report
- up-to-date contracts and data docs

## Notes for Goal 2

- Goal 2 should consume the cleaned layer in `data/processed/airbnb/`
- Goal 2 should not read the root-level legacy raw filenames
- Goal 2 should treat the contracts and cleaned validation report as the current source of truth
