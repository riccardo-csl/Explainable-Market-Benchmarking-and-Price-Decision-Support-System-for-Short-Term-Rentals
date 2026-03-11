from pathlib import Path

import yaml

from data_foundation.cleaned_dataset_runner import run_cleaned_dataset_pipeline
from data_foundation.cleaned_dataset_validation_runner import main, run_cleaned_dataset_validation


FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "source_dataset_samples"


def test_cleaned_dataset_validation_runner_writes_quality_reports(tmp_path: Path) -> None:
    run_cleaned_dataset_pipeline(
        FIXTURE_ROOT,
        tmp_path,
        generation_date="2026-03-11",
    )

    written_paths, overall_status = run_cleaned_dataset_validation(
        FIXTURE_ROOT,
        tmp_path,
        validation_date="2026-03-11",
    )

    yaml_path = tmp_path / "data" / "processed" / "airbnb" / "_quality" / "validation_report.yaml"
    markdown_path = tmp_path / "docs" / "data" / "cleaned_dataset_validation_summary.md"

    assert yaml_path in written_paths
    assert markdown_path in written_paths
    assert overall_status == "passed"

    report = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    assert report["overall_status"] == "passed"
    assert report["validation_date"] == "2026-03-11"


def test_cleaned_dataset_validation_main_returns_success_for_valid_fixture(
    tmp_path: Path,
    capsys,
) -> None:
    run_cleaned_dataset_pipeline(
        FIXTURE_ROOT,
        tmp_path,
        generation_date="2026-03-11",
    )

    exit_code = main(
        [
            "--repo-root",
            str(FIXTURE_ROOT),
            "--output-root",
            str(tmp_path),
            "--validation-date",
            "2026-03-11",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "cleaned_dataset_validation_summary.md" in captured.out
