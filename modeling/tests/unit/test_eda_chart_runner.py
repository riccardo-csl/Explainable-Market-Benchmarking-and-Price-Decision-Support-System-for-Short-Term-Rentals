import json
from pathlib import Path

import pandas as pd

from evaluation.eda_chart_runner import main, run_midterm_eda_chart_pipeline


def _write_listing_snapshot_fixture(repo_root: Path) -> None:
    csv_root = repo_root / "data" / "processed" / "airbnb" / "csv"
    csv_root.mkdir(parents=True, exist_ok=True)
    listing_snapshot = pd.DataFrame(
        [
            {
                "listing_id": 1,
                "city_name": "Roma",
                "period_label": "Early Spring",
                "room_type": "Entire home",
                "nightly_price": 120.0,
                "accommodates_count": 2,
                "neighbourhood_name": "Centro",
            },
            {
                "listing_id": 2,
                "city_name": "Roma",
                "period_label": "Early Summer",
                "room_type": "Private room",
                "nightly_price": 90.0,
                "accommodates_count": 2,
                "neighbourhood_name": "Centro",
            },
            {
                "listing_id": 3,
                "city_name": "Milano",
                "period_label": "Early Autumn",
                "room_type": "Hotel room",
                "nightly_price": 150.0,
                "accommodates_count": 4,
                "neighbourhood_name": "Duomo",
            },
            {
                "listing_id": 4,
                "city_name": "Napoli",
                "period_label": "Early Winter",
                "room_type": "Shared room",
                "nightly_price": 40.0,
                "accommodates_count": 1,
                "neighbourhood_name": "Mercato",
            },
            {
                "listing_id": 5,
                "city_name": "Napoli",
                "period_label": "Early Summer",
                "room_type": "Entire home",
                "nightly_price": 180.0,
                "accommodates_count": 7,
                "neighbourhood_name": "Vomero",
            },
        ]
    )
    listing_snapshot.to_csv(csv_root / "listing_snapshot.csv", index=False)


def test_midterm_eda_chart_pipeline_writes_expected_png_assets_and_manifest(tmp_path: Path) -> None:
    _write_listing_snapshot_fixture(tmp_path)

    written_paths = run_midterm_eda_chart_pipeline(
        tmp_path,
        tmp_path,
        min_neighbourhood_rows=1,
        top_n=2,
        bottom_n=2,
    )

    chart_root = tmp_path / "modeling" / "reports" / "eda" / "midterm_charts"
    expected_svgs = {
        "listing_rows_by_city.svg",
        "listing_rows_by_city_and_period.svg",
        "room_type_share.svg",
        "nightly_price_histogram.svg",
        "nightly_price_boxplot.svg",
        "median_price_by_city.svg",
        "median_price_heatmap_city_period.svg",
        "median_price_by_room_type.svg",
        "median_price_by_accommodates_band.svg",
        "neighbourhood_price_extremes.svg",
    }

    assert expected_svgs.issubset({path.name for path in written_paths})
    for filename in expected_svgs:
        chart_path = chart_root / filename
        assert chart_path.exists()
        assert chart_path.stat().st_size > 0

    manifest_path = chart_root / "midterm_eda_chart_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["chart_group"] == "midterm_eda_slides"
    assert len(manifest["charts"]) == 10


def test_midterm_eda_chart_runner_main_prints_written_paths(tmp_path: Path, capsys) -> None:
    _write_listing_snapshot_fixture(tmp_path)

    exit_code = main(
        [
            "--repo-root",
            str(tmp_path),
            "--output-root",
            str(tmp_path),
            "--min-neighbourhood-rows",
            "1",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "listing_rows_by_city.svg" in captured.out
