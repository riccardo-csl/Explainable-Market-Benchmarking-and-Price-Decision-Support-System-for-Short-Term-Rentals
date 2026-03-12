import json
from pathlib import Path

from evaluation.eda_chart_runner import run_midterm_eda_chart_pipeline


REPO_ROOT = Path(__file__).resolve().parents[3]


def test_real_data_midterm_eda_chart_pipeline_writes_all_expected_assets(tmp_path: Path) -> None:
    written_paths = run_midterm_eda_chart_pipeline(REPO_ROOT, tmp_path)

    chart_root = tmp_path / "modeling" / "reports" / "eda" / "midterm_charts"
    expected_names = {
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
        "midterm_eda_chart_manifest.json",
    }

    assert expected_names == {path.name for path in written_paths}
    for asset_name in expected_names:
        asset_path = chart_root / asset_name
        assert asset_path.exists()
        assert asset_path.stat().st_size > 0

    manifest = json.loads((chart_root / "midterm_eda_chart_manifest.json").read_text(encoding="utf-8"))
    chart_ids = {chart["chart_id"] for chart in manifest["charts"]}
    assert chart_ids == {
        "rows_by_city",
        "rows_by_city_and_period",
        "room_type_share",
        "nightly_price_histogram",
        "nightly_price_boxplot",
        "median_price_by_city",
        "median_price_heatmap_city_period",
        "median_price_by_room_type",
        "median_price_by_accommodates_band",
        "neighbourhood_price_extremes",
    }
