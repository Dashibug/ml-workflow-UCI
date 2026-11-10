"""загружаем и делим UCI Adult data"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

import pandas as pd
from sklearn.model_selection import train_test_split

from src.common import (
    CATEGORICAL_COLUMNS, DATA_DIR, NUMERIC_COLUMNS, PROCESSED_DIR, RAW_DIR,
    TARGET, file_sha256, write_json,
)

SOURCE_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/"
SOURCES = {
    "adult.data": "5b00264637dbfec36bdeaab5676b0b309ff9eb788d63554ca0a249491c86603d",
    "adult.test": "a2a9044bc167a35b2361efbabec64e89d69ce82d9790d2980119aac5fd7e9c05",
}
RAW_COLUMNS = [
    "age", "workclass", "fnlwgt", "education", "education_num", "marital_status",
    "occupation", "relationship", "race", "sex", "capital_gain", "capital_loss",
    "hours_per_week", "native_country", "income",
]


def download_if_needed(raw_dir: Path) -> None:
    raw_dir.mkdir(parents=True, exist_ok=True)
    for filename, expected_sha in SOURCES.items():
        path = raw_dir / filename
        if path.exists() and file_sha256(path) == expected_sha:
            print(f"Using verified cached {path}")
            continue
        if path.exists():
            raise ValueError(
                f"Checksum mismatch: {path}. Remove it and retry, or use "
                "--skip-download only if you intentionally supplied a different file."
            )
        url = SOURCE_URL + filename
        temp_path = path.with_name(path.name + ".tmp")
        print(f"Downloading {url}")
        try:
            request = Request(url, headers={"User-Agent": "ml-workflow-UCI/1.0 (course project)"})
            with urlopen(request, timeout=45) as response, temp_path.open("wb") as output:
                while chunk := response.read(1024 * 1024):
                    output.write(chunk)
            actual_sha = file_sha256(temp_path)
            if actual_sha != expected_sha:
                raise ValueError(f"Wrong SHA256 for {filename}: {actual_sha}")
            os.replace(temp_path, path)
        except (OSError, URLError, ValueError) as exc:
            temp_path.unlink(missing_ok=True)
            raise RuntimeError(
                f"Could not download {filename} from UCI: {exc}. "
                "Download adult.data and adult.test manually into data/raw/ "
                "and run with --skip-download."
            ) from exc


def parse_adult(path: Path, *, is_test: bool) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"Missing {path}. Run without --skip-download to fetch data.")
    frame = pd.read_csv(
        path,
        names=RAW_COLUMNS,
        header=None,
        skiprows=1 if is_test else 0,  
        skipinitialspace=True,
        na_values=["?", "", " ?"],
        keep_default_na=True,
    )
    if frame.empty:
        raise ValueError(f"No rows found in {path}")
    for column in CATEGORICAL_COLUMNS + ["income"]:
        frame[column] = frame[column].map(lambda x: x.strip() if isinstance(x, str) else x)
    labels = frame.pop("income").str.rstrip(".")
    unexpected = set(labels.dropna().unique()) - {"<=50K", ">50K"}
    if unexpected or labels.isna().any():
        raise ValueError(f"Unexpected/missing labels in {path}: {unexpected}")
    frame[TARGET] = labels.eq(">50K").astype(int)
    for column in NUMERIC_COLUMNS:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


def prepare(raw_dir: Path, output_dir: Path, *, seed: int, val_size: float, download: bool) -> dict:
    if not 0 < val_size < 1:
        raise ValueError("val_size must be between 0 and 1")
    if download:
        download_if_needed(raw_dir)
    raw_train = parse_adult(raw_dir / "adult.data", is_test=False)
    raw_test = parse_adult(raw_dir / "adult.test", is_test=True)
    train, val = train_test_split(
        raw_train, test_size=val_size, stratify=raw_train[TARGET],
        random_state=seed, shuffle=True,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    splits = {"train": train, "val": val, "test": raw_test}
    for name, frame in splits.items():
        frame.to_csv(output_dir / f"{name}.csv", index=False)
        print(f"{name:5s}: {len(frame):6,d} rows, positive_rate={frame[TARGET].mean():.4f}")
    metadata = {
        "source": "UCI Adult, https://doi.org/10.24432/C5XW20",
        "dataset_license": "CC BY 4.0",
        "seed": seed,
        "validation_fraction_of_original_training": val_size,
        "split_strategy": "stratified train/validation; untouched official UCI test",
        "raw_sha256": {name: file_sha256(raw_dir / name) for name in SOURCES},
        "split_sha256": {name: file_sha256(output_dir / f"{name}.csv") for name in splits},
        "counts": {name: len(frame) for name, frame in splits.items()},
        "positive_rates": {name: round(float(frame[TARGET].mean()), 6) for name, frame in splits.items()},
    }
    write_json(metadata, output_dir / "data_info.json")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR)
    parser.add_argument("--output-dir", type=Path, default=PROCESSED_DIR)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--val-size", type=float, default=0.2)
    parser.add_argument("--skip-download", action="store_true", help="Use local adult.data and adult.test")
    args = parser.parse_args()
    prepare(args.raw_dir, args.output_dir, seed=args.seed,
            val_size=args.val_size, download=not args.skip_download)
    print("Prepared splits and data_info.json successfully.")


if __name__ == "__main__":
    main()
