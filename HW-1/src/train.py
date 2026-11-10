from __future__ import annotations

import argparse
import shutil
from importlib.metadata import version
from pathlib import Path

import joblib
import pandas as pd

from src.common import (
    ARTIFACTS_DIR, PROCESSED_DIR, file_sha256, load_config, read_json, write_json,
)
from src.metrics import calculate_metrics
from src.modeling import make_pipeline, split_xy


def train(config_path: Path, *, data_dir: Path = PROCESSED_DIR,
          artifacts_dir: Path = ARTIFACTS_DIR) -> Path:
    config = load_config(config_path)
    train_path, val_path = data_dir / "train.csv", data_dir / "val.csv"
    if not train_path.exists() or not val_path.exists():
        raise FileNotFoundError("Prepared data not found; run python -m src.prepare_data first")
    train_df, val_df = pd.read_csv(train_path), pd.read_csv(val_path)
    x_train, y_train = split_xy(train_df)
    x_val, y_val = split_xy(val_df)

    pipeline = make_pipeline(config)
    pipeline.fit(x_train, y_train)
    metrics = calculate_metrics(pipeline, x_val, y_val)
    metrics["split"] = "validation"
    metrics["experiment_name"] = config["experiment_name"]
    metrics["model_name"] = config["model"]["name"]
    metrics["random_state"] = config.get("random_state", 42)

    run_dir = artifacts_dir / config["experiment_name"]
    run_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, run_dir / "model.joblib")
    shutil.copyfile(config_path, run_dir / "config.yaml")
    write_json(metrics, run_dir / "val_metrics.json")
    write_json({
        "python_dependencies": {
            name: version(name) for name in
            ("numpy", "pandas", "scikit-learn", "scipy", "joblib", "PyYAML")
        },
        "input_sha256": {
            "train.csv": file_sha256(train_path),
            "val.csv": file_sha256(val_path),
        },
    }, run_dir / "run_info.json")
    print(f"Trained {config['experiment_name']} — val ROC-AUC={metrics['roc_auc']:.4f}, F1={metrics['f1']:.4f}")
    print(f"Saved model, metrics, config, run info to {run_dir}")
    return run_dir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--data-dir", type=Path, default=PROCESSED_DIR)
    parser.add_argument("--artifacts-dir", type=Path, default=ARTIFACTS_DIR)
    args = parser.parse_args()
    train(args.config, data_dir=args.data_dir, artifacts_dir=args.artifacts_dir)


if __name__ == "__main__":
    main()
