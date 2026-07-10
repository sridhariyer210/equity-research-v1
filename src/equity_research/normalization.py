from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from equity_research.config import STANDARD_COLUMNS


COLUMN_SYNONYMS = {
    "scheme_name": ["scheme", "scheme name", "fund name", "name of the scheme"],
    "security_name": [
        "security",
        "security name",
        "instrument",
        "name of instrument",
        "name of the instrument issuer",
        "name of security",
        "issuer name",
        "company name",
    ],
    "isin": ["isin", "isin code", "isin no", "security isin"],
    "industry": ["industry", "sector", "industry/sector", "rating / industry^", "rating industry"],
    "quantity": ["quantity", "qty", "shares", "no. of shares", "quantity held"],
    "market_value": [
        "market value",
        "market value rs. in lakhs",
        "market/fair value",
        "value",
        "value rs",
        "fair value",
    ],
    "percent_of_aum": [
        "% to nav",
        "% to aum",
        "% to net assets",
        "% of net assets",
        "% of aum",
        "percentage to nav",
        "percentage to aum",
        "net assets %",
    ],
}

EQUITY_HINTS = ("equity", "shares", "stock", "listed")
REST_HINTS = ("cash", "debt", "cblo", "treps", "repo", "futures", "option", "mf unit", "etf")
REST_ISIN = "0000"


def canonicalize_column_name(name: str) -> str:
    return re.sub(r"[^a-z0-9%]+", " ", str(name).strip().lower()).strip()


def rename_columns(frame: pd.DataFrame) -> pd.DataFrame:
    rename_map: dict[str, str] = {}
    canonical_aliases = {
        target: {canonicalize_column_name(alias) for alias in aliases} | {target}
        for target, aliases in COLUMN_SYNONYMS.items()
    }
    for column in frame.columns:
        canonical = canonicalize_column_name(column)
        for target, aliases in canonical_aliases.items():
            if canonical in aliases:
                rename_map[column] = target
                break
    return frame.rename(columns=rename_map)


def parse_month_folder(month_folder: str) -> tuple[int, int]:
    match = re.fullmatch(r"(\d{4})-(\d{1,2})", month_folder)
    if not match:
        raise ValueError(
            f"Month folder '{month_folder}' must use YYYY-MM format, for example 2024-01."
        )
    return int(match.group(1)), int(match.group(2))


def coerce_numeric(series: pd.Series) -> pd.Series:
    cleaned = (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.replace(r"\((.*?)\)", r"-\1", regex=True)
        .str.strip()
        .replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
    )
    return pd.to_numeric(cleaned, errors="coerce")


def infer_holding_category(row: pd.Series) -> str:
    combined = " ".join(str(row.get(field, "")).lower() for field in ["industry", "security_name"])
    if any(token in combined for token in EQUITY_HINTS):
        return "equity"
    if any(token in combined for token in REST_HINTS):
        return "rest"
    if pd.notna(row.get("isin")) and str(row.get("isin")).strip():
        return "equity"
    return "rest"


def build_rest_row(normalized: pd.DataFrame) -> pd.DataFrame:
    if normalized.empty:
        return normalized.iloc[0:0].copy()

    percent_total = normalized["percent_of_aum"].fillna(0).sum()
    remaining_percent = round(max(0.0, 100.0 - float(percent_total)), 2)
    if remaining_percent == 0:
        return normalized.iloc[0:0].copy()

    first_row = normalized.iloc[0]
    rest_row = {
        "year": first_row["year"],
        "month": first_row["month"],
        "amc": first_row["amc"],
        "scheme_name": first_row["scheme_name"],
        "security_name": "REST",
        "isin": REST_ISIN,
        "industry": "REST",
        "quantity": pd.NA,
        "market_value": pd.NA,
        "percent_of_aum": remaining_percent,
        "holding_category": "rest",
        "source_file": first_row["source_file"],
        "parser_name": first_row["parser_name"],
    }
    return pd.DataFrame([rest_row], columns=STANDARD_COLUMNS)


def normalize_holdings_frame(
    frame: pd.DataFrame,
    *,
    amc: str,
    month_folder: str,
    source_file: Path,
    parser_name: str,
    default_scheme_name: str | None = None,
) -> pd.DataFrame:
    year, month = parse_month_folder(month_folder)
    normalized = rename_columns(frame).copy()

    if "scheme_name" not in normalized.columns:
        normalized["scheme_name"] = default_scheme_name

    for required in ["security_name", "scheme_name"]:
        if required not in normalized.columns:
            raise ValueError(f"Required column '{required}' is missing after normalization.")

    normalized["isin"] = normalized.get("isin", pd.Series(index=normalized.index, dtype="object"))
    normalized["industry"] = normalized.get(
        "industry", pd.Series(index=normalized.index, dtype="object")
    )
    normalized["quantity"] = coerce_numeric(
        normalized.get("quantity", pd.Series(index=normalized.index, dtype="object"))
    )
    normalized["market_value"] = coerce_numeric(
        normalized.get("market_value", pd.Series(index=normalized.index, dtype="object"))
    )
    normalized["percent_of_aum"] = coerce_numeric(
        normalized.get("percent_of_aum", pd.Series(index=normalized.index, dtype="object"))
    )

    normalized["security_name"] = normalized["security_name"].astype(str).str.strip()
    normalized["scheme_name"] = normalized["scheme_name"].astype(str).str.strip()
    normalized = normalized[normalized["security_name"].ne("")]
    normalized = normalized[normalized["scheme_name"].ne("")]

    normalized["year"] = year
    normalized["month"] = month
    normalized["amc"] = amc
    normalized["holding_category"] = normalized.apply(infer_holding_category, axis=1)
    normalized["source_file"] = source_file.name
    normalized["parser_name"] = parser_name

    for column in STANDARD_COLUMNS:
        if column not in normalized.columns:
            normalized[column] = pd.NA

    normalized = normalized[STANDARD_COLUMNS].drop_duplicates()
    normalized = pd.concat([normalized, build_rest_row(normalized)], ignore_index=True)
    return normalized.reset_index(drop=True)
