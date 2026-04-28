from pathlib import Path

from goal2_runner import main


def test_goal2_runner_prints_written_paths(monkeypatch, tmp_path: Path, capsys) -> None:
    def fake_model_input(repo_root: Path, *, output_root: Path, version: str | None):
        path = output_root / "data" / "processed" / "airbnb" / "modeling" / version / "model_input.parquet"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
        return {"parquet": path}

    def fake_feature_matrix(repo_root: Path, *, output_root: Path, version: str | None):
        path = output_root / "data" / "processed" / "airbnb" / "modeling" / version / "feature_matrix.parquet"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
        return {"parquet": path}

    class DummyComparison:
        champion_model_name = "linear_baseline"
        fallback_model_name = "tree_challenger"

        @staticmethod
        def to_dict():
            return {"evaluations": {}}

    class DummyArtifact:
        model_name = "linear_baseline"
        raw_feature_columns = ["f1"]
        pipeline = None

    class DummyTrainingResult:
        comparison = DummyComparison()
        linear_artifact = DummyArtifact()
        tree_artifact = DummyArtifact()
        test_frame = None
        feature_frame = None
        linear_explanation_context = {}

    def fake_train(repo_root: Path):
        return DummyTrainingResult()

    def fake_bundle(training_result, output_root: Path, *, bundle_version: str):
        path = output_root / "inference_bundle.joblib"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
        return {"bundle": path}

    monkeypatch.setattr("goal2_runner.build_model_input_artifact_versioned", fake_model_input)
    monkeypatch.setattr("goal2_runner.build_feature_matrix_artifact_versioned", fake_feature_matrix)
    monkeypatch.setattr("goal2_runner.train_goal2_models", fake_train)
    monkeypatch.setattr("goal2_runner.build_inference_bundle", fake_bundle)

    exit_code = main(
        [
            "--repo-root",
            str(tmp_path),
            "--output-root",
            str(tmp_path / "out"),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "model_input.parquet" in captured.out
    assert "feature_matrix.parquet" in captured.out
    assert "inference_bundle.joblib" in captured.out
