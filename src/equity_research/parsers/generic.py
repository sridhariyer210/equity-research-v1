from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from equity_research.normalization import normalize_holdings_frame
from equity_research.parsers.base import BaseParser


class GenericParser(BaseParser):
    parser_name = "generic"

    def parse(
        self,
        file_path: Path,
        *,
        amc: str,
        month_folder: str,
        scheme_aliases: list[str],
    ) -> pd.DataFrame:
        aliases_lower = [alias.lower() for alias in scheme_aliases]

        if file_path.suffix.lower() == ".csv":
            raw_frame = pd.read_csv(file_path)
            filtered = self._filter_small_cap_rows(raw_frame, aliases_lower)
            normalized = normalize_holdings_frame(
                filtered,
                amc=amc,
                month_folder=month_folder,
                source_file=file_path,
                parser_name=self.parser_name,
                default_scheme_name=scheme_aliases[0] if scheme_aliases else None,
            )
            return self.post_process(normalized)

        workbook = pd.read_excel(file_path, sheet_name=None, header=None)
        candidate_frames: list[pd.DataFrame] = []
        for sheet_name, frame in workbook.items():
            if self._sheet_matches(sheet_name, frame, aliases_lower):
                working = self._prepare_sheet_frame(frame)
                filtered = self._filter_small_cap_rows(working, aliases_lower)
                if not filtered.empty:
                    candidate_frames.append(filtered)

        if not candidate_frames:
            raise ValueError(
                "Generic parser could not identify a small cap holdings table. "
                "Add an AMC-specific parser for this format."
            )

        combined = pd.concat(candidate_frames, ignore_index=True)
        normalized = normalize_holdings_frame(
            combined,
            amc=amc,
            month_folder=month_folder,
            source_file=file_path,
            parser_name=self.parser_name,
            default_scheme_name=scheme_aliases[0] if scheme_aliases else None,
        )
        return self.post_process(normalized)

    def post_process(self, frame: pd.DataFrame) -> pd.DataFrame:
        return frame

    def _sheet_matches(
        self, sheet_name: str, frame: pd.DataFrame, scheme_aliases: list[str]
    ) -> bool:
        normalized_aliases = [self._normalize_text(alias) for alias in scheme_aliases]
        sheet_name_lower = self._normalize_text(sheet_name)
        if any(alias in sheet_name_lower for alias in normalized_aliases):
            return True
        sample_values = frame.head(25).fillna("").astype(str).to_numpy().ravel().tolist()
        sample_text = self._normalize_text(" ".join(sample_values))
        return any(alias in sample_text for alias in normalized_aliases)

    def _prepare_sheet_frame(self, frame: pd.DataFrame) -> pd.DataFrame:
        working = frame.dropna(axis=1, how="all").copy()

        header_row_index = self._find_header_row(working)
        if header_row_index is None:
            working.columns = [str(col) for col in working.columns]
            return working

        header_values = (
            working.iloc[header_row_index]
            .fillna("")
            .astype(str)
            .str.strip()
            .replace("", pd.NA)
            .ffill()
            .tolist()
        )
        prepared = working.iloc[header_row_index + 1 :].copy()
        prepared.columns = header_values
        prepared = prepared.dropna(how="all").reset_index(drop=True)
        prepared.columns = [str(col) for col in prepared.columns]
        prepared = self._trim_after_grand_total(prepared)
        return prepared
    
    def _trim_after_grand_total(self, frame: pd.DataFrame) -> pd.DataFrame:
    # Nothing to trim if the DataFrame is empty.
    if frame.empty:
        return frame

    # Iterate through each row looking for the end of the equity section.
    for index, row in frame.iterrows():

        # Normalize each cell for reliable comparisons.
        row_values = [
            self._normalize_text(value)
            for value in row.tolist()
            if pd.notna(value)
        ]

        # Stop when we reach the equity summary row.
        # Everything after this (Debt, T-Bills, TREPS, Cash, Notes, etc.)
        # will be represented by a single REST row.
        if "grandtotal" in row_values or "total" in row_values:
            return frame.iloc[:index].reset_index(drop=True)

    # If no summary row is found, return the original DataFrame.
    return frame


    if frame.empty:
        return frame

    for index, row in frame.iterrows():
        row_values = [
            self._normalize_text(value)
            for value in row.tolist()
            if pd.notna(value)
        ]

        if "grandtotal" in row_values or "total" in row_values:
            return frame.iloc[:index].reset_index(drop=True)

    return frame

    def _find_header_row(self, frame: pd.DataFrame) -> int | None:
        header_hints = {
            "name of the instrument issuer",
            "name of instrument",
            "name of security",
            "security name",
            "instrument",
            "isin",
            "quantity",
            "market value rs in lakhs",
            "market value",
            "to aum",
        }

        for index, row in frame.head(25).iterrows():
            row_text = {self._normalize_text(value) for value in row.fillna("").astype(str).tolist()}
            matches = sum(
                any(hint in cell for cell in row_text if cell)
                for hint in header_hints
            )
            if matches >= 3:
                return int(index)

        return None

    def _normalize_text(self, value: object) -> str:
        return re.sub(r"[^a-z0-9]+", "", str(value).strip().lower())

    def _filter_small_cap_rows(
        self, frame: pd.DataFrame, scheme_aliases: list[str]
    ) -> pd.DataFrame:
        if frame.empty:
            return frame

        lowered_columns = {str(column).strip().lower(): column for column in frame.columns}
        scheme_column = None
        for candidate in ["scheme_name", "scheme", "scheme name", "fund name", "name of the scheme"]:
            if candidate in lowered_columns:
                scheme_column = lowered_columns[candidate]
                break

        if scheme_column is None:
            return frame

        scheme_series = frame[scheme_column].astype(str).str.lower()
        mask = pd.Series(False, index=frame.index)
        for alias in scheme_aliases:
            mask = mask | scheme_series.str.contains(alias, na=False, regex=False)
        filtered = frame[mask].copy()
        return filtered if not filtered.empty else frame
