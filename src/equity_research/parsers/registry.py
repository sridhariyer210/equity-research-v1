from __future__ import annotations

from equity_research.parsers.base import BaseParser
from equity_research.parsers.amc import (
    AdityaBirlaSunLifeParser,
    AxisParser,
    BankOfIndiaParser,
    BandhanParser,
    CanaraRobecoParser,
    FranklinTempletonParser,
    HDFCParser,
    HSBCParser,
    ICICIPrudentialParser,
    ITIParser,
    InvescoParser,
    KotakParser,
    NipponParser,
    QuantParser,
    SBIParser,
    SundaramParser,
    TataParser,
    TrustParser,
    UTIParser,
)
from equity_research.parsers.generic import GenericParser


PARSER_REGISTRY: dict[str, type[BaseParser]] = {
    "aditya_birla_sun_life": AdityaBirlaSunLifeParser,
    "axis": AxisParser,
    "bank_of_india": BankOfIndiaParser,
    "bandhan": BandhanParser,
    "canara_robeco": CanaraRobecoParser,
    "franklin_templeton": FranklinTempletonParser,
    "hsbc": HSBCParser,
    "icici_prudential": ICICIPrudentialParser,
    "invesco": InvescoParser,
    "iti": ITIParser,
    "kotak": KotakParser,
    "quant": QuantParser,
    "sbi": SBIParser,
    "hdfc": HDFCParser,
    "nippon": NipponParser,
    "sundaram": SundaramParser,
    "tata": TataParser,
    "trust": TrustParser,
    "uti": UTIParser,
}


def get_parser(amc: str) -> BaseParser:
    parser_cls = PARSER_REGISTRY.get(amc, GenericParser)
    return parser_cls()
