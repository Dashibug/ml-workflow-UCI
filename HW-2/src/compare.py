"""Compare validation scores and show which experiment to evaluate on UCI test."""
from __future__ import annotations

import argparse
from pathlib import Path

from src.common import ARTIFACTS_DIR, read_json


def compare(artifacts_dir: Path = ARTIFACTS_DIR) -> list[dict]:
    paths = sorted(artifacts_dir.glob("*/val_metrics.json"))
    if not paths:
        raise FileNotFoundError("No validation metrics. Train one or more models first.")
    results = [read_json(path) for path in paths]
    results.sort(key=lambda row: row["roc_auc"], reverse=True)
    print(f"{'EXPERIMENT':40s} {'ROC-AUC':>9s} {'F1':>9s} {'ACCURACY':>9s}")
    print("-" * 72)
    for row in results:
        print(f"{row['experiment_name']:40s} {row['roc_auc']:9.4f} {row['f1']:9.4f} {row['accuracy']:9.4f}")
    print(f"\nBest by validation ROC-AUC: {results[0]['experiment_name']}")
    print("Evaluate that model only on the official test after final selection.")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts-dir", type=Path, default=ARTIFACTS_DIR)
    args = parser.parse_args()
    compare(args.artifacts_dir)


if __name__ == "__main__":
    main()
