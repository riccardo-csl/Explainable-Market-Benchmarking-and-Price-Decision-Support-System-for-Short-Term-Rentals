from pathlib import Path

import pandas as pd
import yaml

from data_foundation.cleaned_dataset_runner import run_cleaned_dataset_pipeline


REPO_ROOT = Path(__file__).resolve().parents[3]
CONTRACT_ROOT = REPO_ROOT / "shared" / "contracts" / "data" / "target_cleaned_datasets"


def test_cleaned_outputs_match_contract_column_order(tmp_path: Path) -> None:
    run_cleaned_dataset_pipeline(REPO_ROOT, tmp_path, generation_date="2026-03-11")

    for contract_path in sorted(CONTRACT_ROOT.glob("*.yaml")):
        contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
        dataset_name = contract["name"]
        expected_columns = [field["name"] for field in contract["fields"]]
        dataframe = pd.read_parquet(
            tmp_path / "data" / "processed" / "airbnb" / "parquet" / f"{dataset_name}.parquet"
        )
        assert list(dataframe.columns) == expected_columns
