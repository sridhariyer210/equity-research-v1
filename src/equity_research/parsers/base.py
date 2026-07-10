from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd


class BaseParser(ABC):
    parser_name = "base"

    @abstractmethod
    def parse(
        self,
        file_path: Path,
        *,
        amc: str,
        month_folder: str,
        scheme_aliases: list[str],
    ) -> pd.DataFrame:
        raise NotImplementedError
