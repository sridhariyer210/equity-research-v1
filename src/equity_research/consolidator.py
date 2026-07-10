from __future__ import annotations

from pathlib import Path

import pandas as pd

from equity_research.config import MASTER_FILE, STANDARD_COLUMNS, STANDARDIZED_DIR


def build_master_csv() -> pd.DataFrame:
    csv_files = sorted(STANDARDIZED_DIR.glob("*/*.csv"))
    if not csv_files:
        empty = pd.DataFrame(columns=STANDARD_COLUMNS)
        MASTER_FILE.parent.mkdir(parents=True, exist_ok=True)
        empty.to_csv(MASTER_FILE, index=False)
        return empty

    frames = [pd.read_csv(path) for path in csv_files]
    master = pd.concat(frames, ignore_index=True)[STANDARD_COLUMNS].drop_duplicates()
    MASTER_FILE.parent.mkdir(parents=True, exist_ok=True)
    master.to_csv(MASTER_FILE, index=False)
    return master


def write_standardized_output(frame: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False)
