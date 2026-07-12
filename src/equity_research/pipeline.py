from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from equity_research.config import load_scheme_aliases


if __package__ in {None, ""}:
    # Allow running this file directly via `python src/equity_research/pipeline.py`.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from equity_research.config import (
    LOG_FILE,
    RAW_DIR,
    STANDARDIZED_DIR,
    SUPPORTED_EXTENSIONS,
    load_scheme_aliases,
)
from equity_research.consolidator import build_master_csv, write_standardized_output
from equity_research.logging_utils import append_log, build_log_entry
from equity_research.parsers.registry import get_parser


def normalize_amc_name(file_path: Path) -> str:
    """
    Infer the AMC name from the filename by searching for any known AMC
    from scheme_aliases.json.

    Examples:
        10818f38-bandhan-small-cap-fund-31-may-26.xlsx -> bandhan
        invesco-india-smallcap-fund_may_2026.xlsx -> invesco
        sbi_small_cap.xlsx -> sbi
    """

    normalized = re.sub(
        r"[^a-z0-9]+",
        "_",
        file_path.stem.strip().lower(),
    )

    known_amcs = sorted(load_scheme_aliases().keys(), key=len, reverse=True)

    for amc in known_amcs:
        if amc in normalized:
            return amc

    return normalized


def discover_month_folders(process_all: bool, month: str | None) -> list[Path]:
    available_months = sorted(path for path in RAW_DIR.iterdir() if path.is_dir())

    if process_all or month is None:
        if not available_months:
            raise FileNotFoundError(
                f"No month folders found in {RAW_DIR}. Add data under data/raw/YYYY-MM/ first."
            )
        return available_months

    if month is None:
        raise ValueError("Pass --month YYYY-MM or use --all-months.")
    target = RAW_DIR / month
    if not target.exists():
        raise FileNotFoundError(f"Raw month folder not found: {target}")
    return [target]


def process_file(file_path: Path, month_folder: str, scheme_aliases_map: dict[str, list[str]]) -> None:
    amc = normalize_amc_name(file_path)
    parser = get_parser(amc)
    aliases = scheme_aliases_map.get(amc, [])
    try:
        frame = parser.parse(
            file_path,
            amc=amc,
            month_folder=month_folder,
            scheme_aliases=aliases,
        )
        output_path = STANDARDIZED_DIR / month_folder / f"{amc}_small_cap.csv"
        write_standardized_output(frame, output_path)
        append_log(
            LOG_FILE,
            build_log_entry(
                month_folder=month_folder,
                amc=amc,
                source_file=file_path.name,
                status="success",
                parser_name=parser.parser_name,
                message=f"Wrote {len(frame)} normalized rows.",
            ),
        )
    except Exception as exc:  # noqa: BLE001
        append_log(
            LOG_FILE,
            build_log_entry(
                month_folder=month_folder,
                amc=amc,
                source_file=file_path.name,
                status="failed",
                parser_name=parser.parser_name,
                message=str(exc),
            ),
        )


def process_month_folder(month_path: Path, scheme_aliases_map: dict[str, list[str]]) -> None:
    files = sorted(
        file_path
        for file_path in month_path.iterdir()
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    for file_path in files:
        process_file(file_path, month_path.name, scheme_aliases_map)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Standardize Indian small cap mutual fund holdings into one master CSV."
    )
    parser.add_argument(
        "--month",
        help="Month folder to process in YYYY-MM format. Defaults to all available months.",
    )
    parser.add_argument(
        "--all-months",
        action="store_true",
        help="Process every month folder found in data/raw.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    scheme_aliases_map = load_scheme_aliases()
    month_folders = discover_month_folders(args.all_months, args.month)
    for month_path in month_folders:
        process_month_folder(month_path, scheme_aliases_map)
    build_master_csv()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
