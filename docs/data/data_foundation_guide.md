# Data Foundation Guide

This is the main entrypoint for the project data layer.

If you are starting Goal 2, this is the first document to read. It tells you what data exists, where it lives, how it is validated, and which supporting documents to use next.

## What Goal 1 Produced

Goal 1 established the full analytical data foundation for the project:

- canonical raw datasets under `data/raw/airbnb/`
- source provenance manifests under `data/raw/_manifests/`
- canonical cleaned datasets under `data/processed/airbnb/`
- processed dataset manifests under `data/processed/airbnb/_manifests/`
- cleaned dataset quality validation under `data/processed/airbnb/_quality/`
- machine-readable contracts under `shared/contracts/data/`
- human-readable documentation under `docs/data/`

The purpose of this layer is to support:

- market benchmarking
- price estimation
- comparable listing logic
- downstream backend and dashboard integration

It does not support true revenue management claims such as occupancy forecasting or dynamic pricing validation.

## Raw Layer

The canonical raw layer lives under `data/raw/airbnb/`.

Current source datasets:

- `listing_snapshots.csv`
- `city_period_summary.csv`
- `neighbourhood_period_summary.csv`
- `neighbourhood_reference.csv`
- `neighbourhood_boundaries.geojson`

These files are treated as immutable inputs.

Supporting metadata:

- raw provenance manifests live in `data/raw/_manifests/`
- source inventory and source relationships are documented in [source_dataset_inventory.md](/home/arch/Scrivania/archive/docs/data/source_dataset_inventory.md)

## Cleaned Layer

The canonical cleaned layer lives under `data/processed/airbnb/`.

Main outputs:

- `csv/` contains readable exports
- `parquet/` contains analytical outputs for code and modeling
- `_manifests/` contains processed dataset metadata
- `_quality/` contains validation reports

Current cleaned datasets:

- `listing_snapshot`
- `city_period_summary`
- `neighbourhood_period_summary`
- `neighbourhood_reference`
- `neighbourhood_boundary`

The cleaned datasets are contract-driven and were validated in Goal 1.

## Which Document to Read Next

Use the following documents based on what you need.

If you need to understand the raw inputs:

- read [source_dataset_inventory.md](/home/arch/Scrivania/archive/docs/data/source_dataset_inventory.md)

If you need the formal cleaned schema:

- read [cleaned_data_contracts.md](/home/arch/Scrivania/archive/docs/data/cleaned_data_contracts.md)

If you need to know how raw fields became cleaned fields:

- read [raw_to_cleaned_feature_mapping.md](/home/arch/Scrivania/archive/docs/data/raw_to_cleaned_feature_mapping.md)

If you need the short cleaned-only reference for modeling or backend work:

- read [cleaned_dataset_dictionary.md](/home/arch/Scrivania/archive/docs/data/cleaned_dataset_dictionary.md)

If you need the assumptions that Goal 2 must respect:

- read [modeling_data_assumptions.md](/home/arch/Scrivania/archive/docs/data/modeling_data_assumptions.md)

If you need to rebuild the full data layer:

- read [data_foundation_runbook.md](/home/arch/Scrivania/archive/docs/data/data_foundation_runbook.md)

If you need the latest validation status:

- read [cleaned_dataset_validation_summary.md](/home/arch/Scrivania/archive/docs/data/cleaned_dataset_validation_summary.md)

## Data Flow

The data flow established in Goal 1 is:

1. source datasets are registered and profiled
2. raw files are cataloged and traced with provenance manifests
3. cleaned datasets are built from canonical raw inputs
4. cleaned outputs are checked against contracts and minimal semantic guarantees
5. Goal 2 consumes the cleaned layer, not the raw files

## What Goal 2 Should Treat as Stable

Goal 2 should assume the following interfaces are stable:

- raw dataset locations in `data/raw/airbnb/`
- cleaned dataset locations in `data/processed/airbnb/`
- dataset contracts in `shared/contracts/data/target_cleaned_datasets/`
- cleaned field names and primary keys

Goal 2 should not rebuild its own ad hoc copies of the cleaned layer.

## Practical Recommendation

For most engineering tasks after Goal 1, the most useful reading order is:

1. [data_foundation_guide.md](/home/arch/Scrivania/archive/docs/data/data_foundation_guide.md)
2. [cleaned_dataset_dictionary.md](/home/arch/Scrivania/archive/docs/data/cleaned_dataset_dictionary.md)
3. [raw_to_cleaned_feature_mapping.md](/home/arch/Scrivania/archive/docs/data/raw_to_cleaned_feature_mapping.md)
4. [modeling_data_assumptions.md](/home/arch/Scrivania/archive/docs/data/modeling_data_assumptions.md)
