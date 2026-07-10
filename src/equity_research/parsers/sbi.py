from __future__ import annotations

from pathlib import Path

import pandas as pd

from equity_research.normalization import normalize_holdings_frame
from equity_research.parsers.generic import GenericParser


class SBIParser(GenericParser):
    parser_name = "sbi"
    SHEET_NAME = "SSCF"
    DATA_START_ROW = 11  # 1-based Excel row number where the first holding begins.
    COLUMN_MAP = {
        "security_name": 2,   # Column C
        "isin": 3,            # Column D
        "industry": 4,        # Column E
        "quantity": 5,        # Column F
        "market_value": 6,    # Column G
        "percent_of_aum": 7,  # Column H
    }

    def parse(
        self,
        file_path: Path,
        *,
        amc: str,
        month_folder: str,
        scheme_aliases: list[str],
    ) -> pd.DataFrame:
        workbook = pd.read_excel(file_path, sheet_name=None, header=None)

        if self.SHEET_NAME not in workbook:
            return super().parse(
                file_path,
                amc=amc,
                month_folder=month_folder,
                scheme_aliases=scheme_aliases,
            )

        raw_frame = workbook[self.SHEET_NAME]
        data_start_index = self.DATA_START_ROW - 1
        security_series = raw_frame.iloc[data_start_index:, self.COLUMN_MAP["security_name"]].astype(str).str.strip()
        total_rows = security_series[security_series.str.lower() == "total"]
        data_end_index = int(total_rows.index[0]) if not total_rows.empty else len(raw_frame)

        frame = pd.DataFrame(
            {
                column_name: raw_frame.iloc[data_start_index:data_end_index, column_index]
                for column_name, column_index in self.COLUMN_MAP.items()
            }
        ).reset_index(drop=True)
        frame = frame.dropna(how="all")
        frame = frame[frame["isin"].notna()].copy()

        return normalize_holdings_frame(
            frame,
            amc=amc,
            month_folder=month_folder,
            source_file=file_path,
            parser_name=self.parser_name,
            default_scheme_name=scheme_aliases[0] if scheme_aliases else "SBI Smallcap Fund",
        )
