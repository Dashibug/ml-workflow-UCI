"""Evaluate a trained experiment on the untouched UCI test split."""
from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd

from src.common import ARTIFACTS_DIR, PROCESSED_DIR, file_sha256, load_config, write_json
from src.metrics import calculate_metrics
from src.modeling import split_xy


def evaluate(config_path: Path, *, data_dir: Path = PROCESSED_DIR,
             artifacts_dir: Path = ARTIFACTS_DIR) -> dict:
    config = load_config(config_path)
    run_dir = artifacts_dir / config["experiment_name"]
    model_path = run_dir / "model.joblib"
    test_path = data_dir / "test.csv"
    if not model_path.is_file():
        raise FileNotFoundError(f"Missing {model_path}: train this experiment first")
    if not test_path.is_file():
        raise FileNotFoundError(f"Missing {test_path}: prepare data first")
    model = joblib.load(model_path)
    test_df = pd.read_csv(test_path)
    x_test, y_test = split_xy(test_df)
    metrics = calculate_metrics(model, x_test, y_test)
    metrics.update({
        "experiment_name": config["experiment_name"],
        "model_name": config["model"]["name"],
        "split": "official_test",
        "test_sha256": file_sha256(test_path),
    })
    write_json(metrics, run_dir / "test_metrics.json")
    print(f"Test {config['experiment_name']} — ROC-AUC={metrics['roc_auc']:.4f}, F1={metrics['f1']:.4f}")
    print(f"Saved {run_dir / 'test_metrics.json'}")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--data-dir", type=Path, default=PROCESSED_DIR)
    parser.add_argument("--artifacts-dir", type=Path, default=ARTIFACTS_DIR)
    args = parser.parse_args()
    evaluate(args.config, data_dir=args.data_dir, artifacts_dir=args.artifacts_dir)


if __name__ == "__main__":
    main()
