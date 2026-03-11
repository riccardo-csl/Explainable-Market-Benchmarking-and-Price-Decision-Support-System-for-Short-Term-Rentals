"""Runner for minimal cleaned dataset validation."""

from __future__ import annotations

import argparse
from pathlib import Path

from .cleaned_dataset_validation import render_validation_summary_markdown, validate_cleaned_datasets
from .report_writer import write_yaml


def run_cleaned_dataset_validation(
    repo_root: Path,
    output_root: Path | None = None,
    validation_date: str | None = None,
) -> tuple[list[Path], str]:
    resolved_repo_root = repo_root.resolve()
    resolved_output_root = resolved_repo_root if output_root is None else output_root.resolve()

    report = validate_cleaned_datasets(
        output_root=resolved_output_root,
        validation_date=validation_date,
    )

    yaml_path = resolved_output_root / "data" / "processed" / "airbnb" / "_quality" / "validation_report.yaml"
    markdown_path = resolved_output_root / "docs" / "data" / "cleaned_dataset_validation_summary.md"

    write_yaml(yaml_path, report.to_dict())
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(render_validation_summary_markdown(report), encoding="utf-8")

    return [yaml_path, markdown_path], report.overall_status


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate cleaned processed datasets against minimal structural guarantees."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[3],
        help="Path to the repository root.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help="Optional output root. Defaults to the repository root.",
    )
    parser.add_argument(
        "--validation-date",
        type=str,
        default=None,
        help="Optional ISO date override for the validation report.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    written_paths, overall_status = run_cleaned_dataset_validation(
        repo_root=args.repo_root,
        output_root=args.output_root,
        validation_date=args.validation_date,
    )
    for path in written_paths:
        print(path)
    return 0 if overall_status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
