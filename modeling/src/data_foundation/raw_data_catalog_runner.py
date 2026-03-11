"""Canonical raw data organization and provenance generation."""

from __future__ import annotations

import argparse
from pathlib import Path

from .dataset_inventory_runner import run_dataset_inventory
from .provenance import build_raw_dataset_manifest
from .report_writer import write_yaml
from .source_registry import source_dataset_descriptors


def run_raw_data_catalog(
    repo_root: Path,
    output_root: Path | None = None,
    import_date: str | None = None,
) -> list[Path]:
    resolved_repo_root = repo_root.resolve()
    resolved_output_root = resolved_repo_root if output_root is None else output_root.resolve()

    descriptors = source_dataset_descriptors()
    manifests = [
        build_raw_dataset_manifest(descriptor, resolved_repo_root, import_date=import_date)
        for descriptor in descriptors
    ]

    written_paths: list[Path] = []
    manifest_root = resolved_output_root / "data" / "raw" / "_manifests"
    for manifest in manifests:
        manifest_path = manifest_root / f"{manifest.dataset_name}.yaml"
        write_yaml(manifest_path, manifest.to_dict())
        written_paths.append(manifest_path)

    written_paths.extend(run_dataset_inventory(resolved_repo_root, resolved_output_root))
    return written_paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate canonical raw data manifests and refresh the dataset registry."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[3],
        help="Path to the repository root that contains the canonical raw datasets.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help="Optional output root. Defaults to the repository root.",
    )
    parser.add_argument(
        "--import-date",
        type=str,
        default=None,
        help="Optional ISO date override for manifest generation.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    written_paths = run_raw_data_catalog(
        args.repo_root,
        args.output_root,
        import_date=args.import_date,
    )
    for path in written_paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
