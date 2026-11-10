"""Offline tests"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from src.common import TARGET, load_config
from src.evaluate import evaluate
from src.prepare_data import parse_adult, prepare
from src.train import train


def create_raw_data(raw_dir: Path, n_train: int = 100, n_test: int = 40) -> None:
    raw_dir.mkdir(parents=True, exist_ok=True)

    def row(i: int, is_test: bool) -> str:
        income = ">50K" if i % 3 == 0 else "<=50K"
        if is_test:
            income += "."
        return ", ".join([
            str(18 + i % 50), "?" if i % 11 == 0 else "Private",
            str(100000 + 5 * i), "Bachelors" if i % 3 == 0 else "HS-grad",
            str(13 if i % 3 == 0 else 9),
            "Married-civ-spouse" if i % 2 else "Never-married",
            "?" if i % 9 == 0 else "Adm-clerical", "Not-in-family",
            "Other", "Male" if i % 2 else "Female", str(100 * (i % 5)),
            "0", str(20 + i % 40), "?" if i % 8 == 0 else "United-States",
            income,
        ])

    (raw_dir / "adult.data").write_text(
        "\n".join(row(i, False) for i in range(n_train)) + "\n", encoding="utf-8"
    )
    (raw_dir / "adult.test").write_text(
        "|1x3 Cross validator\n" +
        "\n".join(row(i, True) for i in range(n_test)) + "\n", encoding="utf-8"
    )


def test_parsing_and_split_are_deterministic(tmp_path: Path):
    raw_dir = tmp_path / "raw"
    create_raw_data(raw_dir)
    parsed = parse_adult(raw_dir / "adult.test", is_test=True)
    assert parsed.shape == (40, 15)
    assert parsed[TARGET].isin([0, 1]).all()
    assert pd.isna(parsed.iloc[0]["workclass"])
    assert pd.isna(parsed.iloc[0]["native_country"])

    result_a = prepare(raw_dir, tmp_path / "a", seed=42, val_size=0.2, download=False)
    result_b = prepare(raw_dir, tmp_path / "b", seed=42, val_size=0.2, download=False)
    assert result_a["counts"] == {"train": 80, "val": 20, "test": 40}
    assert result_a["split_sha256"] == result_b["split_sha256"]
    assert len(set(result_a["split_sha256"].values())) == 3


@pytest.mark.parametrize("config_name", ["baseline", "experiment"])
def test_full_workflow_offline(tmp_path: Path, config_name: str):
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    artifact_dir = tmp_path / "artifacts"
    create_raw_data(raw_dir)
    prepare(raw_dir, processed_dir, seed=42, val_size=0.2, download=False)

    config_path = Path(__file__).resolve().parents[1] / "configs" / f"{config_name}.yaml"
    run_dir = train(config_path, data_dir=processed_dir, artifacts_dir=artifact_dir)
    metrics = evaluate(config_path, data_dir=processed_dir, artifacts_dir=artifact_dir)
    assert (run_dir / "model.joblib").exists()
    assert (run_dir / "config.yaml").exists()
    assert (run_dir / "run_info.json").exists()
    assert (run_dir / "val_metrics.json").exists()
    assert (run_dir / "test_metrics.json").exists()
    assert metrics["n_rows"] == 40
    assert 0 <= metrics["roc_auc"] <= 1
    assert len(metrics["confusion_matrix"]) == 2
    assert sum(map(sum, metrics["confusion_matrix"])) == 40
    saved = json.loads((run_dir / "val_metrics.json").read_text())
    assert saved["split"] == "validation"
    assert 0 <= saved["f1"] <= 1


def test_bad_config_is_rejected(tmp_path: Path):
    path = tmp_path / "bad.yaml"
    path.write_text("experiment_name: ../oops\nmodel:\n  name: logistic_regression\n")
    with pytest.raises(ValueError, match="experiment_name"):
        load_config(path)


def test_unexpected_target_is_rejected(tmp_path: Path):
    path = tmp_path / "adult.data"
    path.write_text("1, Private, 10, HS-grad, 9, Never-married, Sales, Own-child, White, Male, 0, 0, 30, United-States, invalid\n")
    with pytest.raises(ValueError, match="Unexpected"):
        parse_adult(path, is_test=False)


def test_compare_validation_runs(tmp_path: Path):
    from src.compare import compare

    raw_dir, processed_dir, artifact_dir = (tmp_path / name for name in ("raw", "processed", "artifacts"))
    create_raw_data(raw_dir)
    prepare(raw_dir, processed_dir, seed=42, val_size=0.2, download=False)
    for name in ("baseline", "experiment"):
        path = Path(__file__).resolve().parents[1] / "configs" / f"{name}.yaml"
        train(path, data_dir=processed_dir, artifacts_dir=artifact_dir)
    results = compare(artifact_dir)
    assert len(results) == 2
    assert results[0]["roc_auc"] >= results[1]["roc_auc"]
