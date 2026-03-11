"""Dataset inventory orchestration and contract generation."""

from __future__ import annotations

import argparse
from pathlib import Path

from .inspector import inspect_dataset
from .report_writer import (
    render_cleaned_contracts_markdown,
    render_source_inventory_markdown,
    render_source_registry_yaml,
    render_target_contract_yaml,
    write_yaml,
)
from .source_registry import (
    source_dataset_descriptors,
    source_dataset_relationships,
    target_dataset_contracts,
)


def run_dataset_inventory(repo_root: Path, output_root: Path | None = None) -> list[Path]:
    resolved_repo_root = repo_root.resolve()
    resolved_output_root = resolved_repo_root if output_root is None else output_root.resolve()

    descriptors = source_dataset_descriptors()
    profiles = {
        descriptor.name: inspect_dataset(descriptor, resolved_repo_root)
        for descriptor in descriptors
    }
    relationships = source_dataset_relationships()
    contracts = target_dataset_contracts()

    written_paths: list[Path] = []

    registry_path = resolved_output_root / "shared" / "contracts" / "data" / "source_dataset_registry.yaml"
    write_yaml(registry_path, render_source_registry_yaml(descriptors, profiles, relationships))
    written_paths.append(registry_path)

    target_contract_root = resolved_output_root / "shared" / "contracts" / "data" / "target_cleaned_datasets"
    for contract in contracts:
        contract_path = target_contract_root / f"{contract.name}.yaml"
        write_yaml(contract_path, render_target_contract_yaml(contract))
        written_paths.append(contract_path)

    inventory_path = resolved_output_root / "docs" / "data" / "source_dataset_inventory.md"
    inventory_path.parent.mkdir(parents=True, exist_ok=True)
    inventory_path.write_text(
        render_source_inventory_markdown(descriptors, profiles, relationships),
        encoding="utf-8",
    )
    written_paths.append(inventory_path)

    contracts_path = resolved_output_root / "docs" / "data" / "cleaned_data_contracts.md"
    contracts_path.write_text(
        render_cleaned_contracts_markdown(contracts),
        encoding="utf-8",
    )
    written_paths.append(contracts_path)

    return written_paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate the dataset inventory and cleaned data contracts."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[3],
        help="Path to the repository root that contains the source datasets.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help="Optional output root. Defaults to the repository root.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    written_paths = run_dataset_inventory(args.repo_root, args.output_root)
    for path in written_paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
