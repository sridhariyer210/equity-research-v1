from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


@dataclass
class ProcessingLogEntry:
    timestamp: str
    month_folder: str
    amc: str
    source_file: str
    status: str
    parser_name: str
    message: str


def build_log_entry(
    month_folder: str,
    amc: str,
    source_file: str,
    status: str,
    parser_name: str,
    message: str,
) -> ProcessingLogEntry:
    return ProcessingLogEntry(
        timestamp=datetime.now(timezone.utc).isoformat(),
        month_folder=month_folder,
        amc=amc,
        source_file=source_file,
        status=status,
        parser_name=parser_name,
        message=message,
    )


def append_log(log_path: Path, entry: ProcessingLogEntry) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame([asdict(entry)])
    if log_path.exists():
        frame.to_csv(log_path, mode="a", header=False, index=False)
    else:
        frame.to_csv(log_path, index=False)

