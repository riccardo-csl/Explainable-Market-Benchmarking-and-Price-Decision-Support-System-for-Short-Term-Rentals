# Agent instructions (scope: this directory and subdirectories)

## Scope and ownership
- This AGENTS.md applies to `/home/arch/Scrivania/archive/data` and below.
- This module owns raw datasets, processed datasets, external imports, dataset manifests, and data provenance metadata.

## Expected layout
- `raw/`
  Immutable source datasets.
- `raw/_manifests/`
  Provenance metadata for each canonical raw dataset.
- `processed/`
  Derived datasets created from repeatable transformations.
- `external/`
  Additional acquired or third-party data sources.

## Conventions
- Treat files in `raw/` as immutable inputs.
- Treat files in `raw/_manifests/` as the machine-readable source of provenance and integrity metadata for canonical raw files.
- Never overwrite source data in place.
- Document provenance, schema, and transformation lineage for any processed output.
- Use descriptive filenames and include version or date information when relevant.

## Testing and validation
- Add data validation checks for any new processed dataset.
- Verify schema shape, null handling, duplicates, and key assumptions for derived outputs.

## Do not
- Do not place code here unless it is data-specific metadata or validation config.
- Do not store undocumented generated files.
