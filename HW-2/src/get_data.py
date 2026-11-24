"""DVC get_data stage: fetch original UCI Adult files with SHA256 verification."""
from __future__ import annotations

from src.common import RAW_DIR, file_sha256
from src.prepare_data import SOURCES, download_if_needed


def main() -> None:
    download_if_needed(RAW_DIR)
    for filename in SOURCES:
        path = RAW_DIR / filename
        print(f"{path}: sha256={file_sha256(path)}")
    print("get_data finished: raw dataset is ready for DVC.")


if __name__ == "__main__":
    main()
