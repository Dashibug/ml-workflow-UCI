from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
TARGET = "income_gt_50k"

NUMERIC_COLUMNS = [
    "age", "fnlwgt", "education_num", "capital_gain", "capital_loss", "hours_per_week"
]
CATEGORICAL_COLUMNS = [
    "workclass", "education", "marital_status", "occupation", "relationship",
    "race", "sex", "native_country"
]
FEATURE_COLUMNS = NUMERIC_COLUMNS + CATEGORICAL_COLUMNS


def load_config(path: str | Path) -> dict:
    path = Path(path)
    with path.open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    if not isinstance(config, dict):
        raise ValueError(f"Config must be a YAML mapping: {path}")
    if not config.get("experiment_name") or not isinstance(config.get("model"), dict):
        raise ValueError("Config needs 'experiment_name' and 'model'")
    if not config["model"].get("name"):
        raise ValueError("Config needs 'model.name'")
    name = config["experiment_name"]
    if not isinstance(name, str) or not name.replace("_", "").replace("-", "").isalnum():
        raise ValueError("experiment_name must be letters/numbers/hyphens/underscores only")
    return config


def file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(payload: dict, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
