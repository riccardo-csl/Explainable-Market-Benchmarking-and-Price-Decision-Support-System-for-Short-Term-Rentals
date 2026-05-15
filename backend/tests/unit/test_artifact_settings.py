from pathlib import Path

from config.artifact_settings import Goal2ArtifactSettings


def test_required_paths_report_missing_artifacts(tmp_path: Path) -> None:
    settings = Goal2ArtifactSettings(repo_root=tmp_path, artifact_version="missing")

    missing_names = {path.name for path in settings.missing_paths()}

    assert "inference_bundle.joblib" in missing_names
    assert "price_feature_matrix.parquet" in missing_names
    assert settings.artifact_root == tmp_path / "data" / "processed" / "airbnb" / "modeling" / "missing"


def test_default_goal2_v10_diagnostics_artifacts_exist_for_local_beta() -> None:
    settings = Goal2ArtifactSettings.from_environment()

    assert settings.artifact_version == "goal2_v10_diagnostics"
    assert settings.missing_paths() == []
