from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
STANDARDIZED_DIR = DATA_DIR / "standardized"
MASTER_DIR = DATA_DIR / "master"
LOG_DIR = DATA_DIR / "logs"
CONFIG_DIR = PROJECT_ROOT / "config"

MASTER_FILE = MASTER_DIR / "small_cap_holdings_master.csv"
LOG_FILE = LOG_DIR / "processing_log.csv"

SUPPORTED_EXTENSIONS = {".csv", ".xls", ".xlsx"}

STANDARD_COLUMNS = [
    "year",
    "month",
    "amc",
    "scheme_name",
    "security_name",
    "isin",
    "industry",
    "quantity",
    "market_value",
    "percent_of_aum",
    "holding_category",
    "source_file",
    "parser_name",
]


def load_scheme_aliases() -> dict[str, list[str]]:
    config_path = CONFIG_DIR / "scheme_aliases.json"
    with config_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)

