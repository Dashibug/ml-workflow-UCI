"""DVC prepare_data stage: read tracked YAML params and create split CSV files."""
from __future__ import annotations

from pathlib import Path

import yaml

from src.common import PROCESSED_DIR, RAW_DIR
from src.prepare_data import prepare

CONFIG = Path(__file__).resolve().parents[1] / "configs" / "data.yaml"


def main() -> None:
    with CONFIG.open("r", encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    if not isinstance(config, dict) or "seed" not in config or "val_size" not in config:
        raise ValueError(f"Expected seed and val_size in {CONFIG}")

    seed = int(config["seed"])
    val_size = float(config["val_size"])
    info = prepare(RAW_DIR, PROCESSED_DIR, seed=seed, val_size=val_size, download=False)
    print(
        f"prepare_data finished: seed={seed}; val_size={val_size}; "
        f"counts={info['counts']}"
    )


if __name__ == "__main__":
    main()
