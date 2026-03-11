"""Cleaned dataset pipeline runner."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from .cleaned_dataset_builder import build_cleaned_datasets
from .processed_output import write_processed_dataset
from .raw_dataset_loader import load_raw_datasets
from .source_registry import source_dataset_descriptors, target_dataset_contracts


def run_cleaned_dataset_pipeline(
    repo_root: Path,
    output_root: Path | None = None,
    generation_date: str | None = None,
) -> list[Path]:
    resolved_repo_root = repo_root.resolve()
    resolved_output_root = resolved_repo_root if output_root is None else output_root.resolve()
    resolved_generation_date = generation_date or date.today().isoformat()

    descriptors = source_dataset_descriptors()
    contracts = target_dataset_contracts()
    raw_datasets = load_raw_datasets(descriptors, resolved_repo_root)
    cleaned_datasets = build_cleaned_datasets(raw_datasets, contracts)
    contract_map = {contract.name: contract for contract in contracts}

    written_paths: list[Path] = []
    for dataset_name, dataframe in cleaned_datasets.items():
        output_paths, _manifest = write_processed_dataset(
            dataset_name=dataset_name,
            dataframe=dataframe,
            source_datasets=contract_map[dataset_name].source_datasets,
            output_root=resolved_output_root,
            generation_date=resolved_generation_date,
        )
        written_paths.extend(output_paths)

    return written_paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate cleaned datasets and processed output manifests."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[3],
        help="Path to the repository root that contains canonical raw datasets.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help="Optional output root. Defaults to the repository root.",
    )
    parser.add_argument(
        "--generation-date",
        type=str,
        default=None,
        help="Optional ISO date override for processed dataset manifests.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    written_paths = run_cleaned_dataset_pipeline(
        repo_root=args.repo_root,
        output_root=args.output_root,
        generation_date=args.generation_date,
    )
    for path in written_paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
