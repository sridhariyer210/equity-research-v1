# equity-research-v1

Pipeline to standardize Indian mutual fund small cap holdings across AMCs and
combine them into a single master CSV.

## Folder layout

```text
data/
  raw/
    2024-01/
      sbi.xlsx
      hdfc.xlsx
      nippon.csv
  standardized/
    2024-01/
      sbi_small_cap.csv
      hdfc_small_cap.csv
  master/
    small_cap_holdings_master.csv
  logs/
    processing_log.csv
```

## Output schema

- `year`
- `month`
- `amc`
- `scheme_name`
- `security_name`
- `isin`
- `industry`
- `quantity`
- `market_value`
- `percent_of_aum`
- `holding_category`
- `source_file`
- `parser_name`

`holding_category` is simplified to:

- `equity`
- `rest`

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run

Process a single month:

```bash
python3 -m equity_research.pipeline --month 2024-01
```

Process every month folder inside `data/raw`:

```bash
python3 -m equity_research.pipeline --all-months
```

## How it works

1. Scans `data/raw/<month>/` for `.csv`, `.xls`, and `.xlsx` files.
2. Selects an AMC-specific parser when available, otherwise falls back to the
   generic parser.
3. Identifies the small cap scheme based on `config/scheme_aliases.json`.
4. Standardizes columns into the common schema.
5. Writes one standardized CSV per source file.
6. Builds `data/master/small_cap_holdings_master.csv`.
7. Logs successes and failures to `data/logs/processing_log.csv`.

## Important note

AMC files vary a lot. This project includes a generic parser plus parser hooks
for AMC-specific overrides. You should expect to add custom parsers over time as
you collect sample files from each AMC.
