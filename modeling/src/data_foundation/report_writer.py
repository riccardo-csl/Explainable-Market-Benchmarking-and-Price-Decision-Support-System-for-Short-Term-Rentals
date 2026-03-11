"""Writers for markdown and YAML artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import yaml

from .contracts import (
    DatasetRelationship,
    ObservedDatasetProfile,
    SourceDatasetDescriptor,
    TargetDatasetContract,
)


def write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False, allow_unicode=True)


def render_source_registry_yaml(
    descriptors: Iterable[SourceDatasetDescriptor],
    profiles: dict[str, ObservedDatasetProfile],
    relationships: Iterable[DatasetRelationship],
) -> dict:
    descriptor_map = {descriptor.name: descriptor for descriptor in descriptors}
    return {
        "source_datasets": [
            {
                **descriptor_map[dataset_name].to_dict(),
                "observed_profile": profiles[dataset_name].to_dict(),
            }
            for dataset_name in descriptor_map
        ],
        "relationships": [relationship.to_dict() for relationship in relationships],
    }


def render_target_contract_yaml(contract: TargetDatasetContract) -> dict:
    return contract.to_dict()


def _markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    header_line = "| " + " | ".join(headers) + " |"
    divider_line = "| " + " | ".join("---" for _ in headers) + " |"
    body_lines = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([header_line, divider_line, *body_lines])


def render_source_inventory_markdown(
    descriptors: Iterable[SourceDatasetDescriptor],
    profiles: dict[str, ObservedDatasetProfile],
    relationships: Iterable[DatasetRelationship],
) -> str:
    descriptor_map = {descriptor.name: descriptor for descriptor in descriptors}
    lines = [
        "# Source Dataset Inventory",
        "",
        "This document describes the inventory of the raw source datasets currently available in the repository. "
        "It records what each source file contains, how it is expected to be used, and which limitations must be carried forward into later stages.",
        "",
    ]

    overview_rows: list[list[str]] = []
    for dataset_name, descriptor in descriptor_map.items():
        profile = profiles[dataset_name]
        volume = str(profile.row_count or profile.feature_count or 0)
        overview_rows.append(
            [
                descriptor.name,
                descriptor.file_format,
                descriptor.grain,
                volume,
                descriptor.relative_path,
            ]
        )

    lines.extend(
        [
            "## Dataset Overview",
            "",
            _markdown_table(["Dataset", "Format", "Grain", "Rows/Features", "Path"], overview_rows),
            "",
        ]
    )

    for dataset_name, descriptor in descriptor_map.items():
        profile = profiles[dataset_name]
        lines.extend(
            [
                f"## {descriptor.name}",
                "",
                descriptor.description,
                "",
                f"- Raw path: `{descriptor.relative_path}`",
                f"- Original filename: `{descriptor.original_filename}`",
                f"- Format: `{descriptor.file_format}`",
                f"- Grain: `{descriptor.grain}`",
                f"- Role: `{descriptor.role}`",
                f"- Source category: `{descriptor.source_category}`",
                f"- Steward: `{descriptor.steward}`",
                f"- Immutable input: `{'yes' if descriptor.immutable else 'no'}`",
                f"- Rows/Features: `{profile.row_count or profile.feature_count or 0}`",
                "",
            ]
        )

        if profile.coverage:
            lines.append("### Coverage")
            lines.append("")
            for key, values in profile.coverage.items():
                preview = ", ".join(values[:10])
                lines.append(f"- {key}: {preview}")
            lines.append("")

        if profile.candidate_keys:
            lines.append("### Candidate Keys")
            lines.append("")
            key_rows = [
                [", ".join(result.columns), "yes" if result.is_unique else "no", str(result.duplicate_key_count)]
                for result in profile.candidate_keys
            ]
            lines.append(_markdown_table(["Columns", "Unique", "Duplicate Keys"], key_rows))
            lines.append("")

        field_rows = [
            [
                field.name,
                field.inferred_type,
                "yes" if field.nullable else "no",
                "yes" if field.likely_categorical else "no",
                ", ".join(field.sample_values) if field.sample_values else "-",
            ]
            for field in profile.fields
        ]
        lines.extend(
            [
                "### Fields",
                "",
                _markdown_table(["Field", "Type", "Nullable", "Likely Categorical", "Sample Values"], field_rows),
                "",
            ]
        )

        if descriptor.known_limitations:
            lines.append("### Known Limitations")
            lines.append("")
            for note in descriptor.known_limitations:
                lines.append(f"- {note}")
            lines.append("")

    lines.extend(["## Dataset Relationships", ""])
    relationship_rows = [
        [
            relationship.from_dataset,
            relationship.to_dataset,
            relationship.relation_type,
            ", ".join(relationship.join_columns),
            relationship.notes,
        ]
        for relationship in relationships
    ]
    lines.extend(
        [
            _markdown_table(
                ["From", "To", "Relation Type", "Join Columns", "Notes"],
                relationship_rows,
            ),
            "",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def render_cleaned_contracts_markdown(contracts: Iterable[TargetDatasetContract]) -> str:
    lines = [
        "# Cleaned Data Contracts",
        "",
        "This document describes the canonical cleaned analytical tables that later stages must produce. "
        "The target contracts are defined early so that cleaning, validation, modeling, and backend integration work against a stable interface.",
        "",
    ]
    for contract in contracts:
        lines.extend(
            [
                f"## {contract.name}",
                "",
                contract.description,
                "",
                f"- Grain: `{contract.grain}`",
                f"- Primary key: `{', '.join(contract.primary_key)}`",
                f"- Source datasets: `{', '.join(contract.source_datasets)}`",
                "",
            ]
        )

        field_rows = [
            [
                field.name,
                field.data_type,
                "yes" if field.nullable else "no",
                ", ".join(field.source_columns) if field.source_columns else "-",
                field.description,
            ]
            for field in contract.fields
        ]
        lines.extend(
            [
                _markdown_table(
                    ["Field", "Type", "Nullable", "Source Columns", "Description"],
                    field_rows,
                ),
                "",
            ]
        )

        if contract.notes:
            lines.append("Notes:")
            for note in contract.notes:
                lines.append(f"- {note}")
            lines.append("")

    return "\n".join(lines).strip() + "\n"
