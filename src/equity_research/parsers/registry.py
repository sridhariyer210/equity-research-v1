from __future__ import annotations

from equity_research.parsers.base import BaseParser
from equity_research.parsers.generic import GenericParser
from equity_research.parsers.hdfc import HDFCParser
from equity_research.parsers.nippon import NipponParser
from equity_research.parsers.sbi import SBIParser


PARSER_REGISTRY: dict[str, type[BaseParser]] = {
    "sbi": SBIParser,
    "hdfc": HDFCParser,
    "nippon": NipponParser,
}


def get_parser(amc: str) -> BaseParser:
    parser_cls = PARSER_REGISTRY.get(amc, GenericParser)
    return parser_cls()
