from __future__ import annotations

from equity_research.parsers.generic import GenericParser


class AMCParser(GenericParser):
    """Base class for AMC-specific parsers."""


class SBIParser(AMCParser):
    parser_name = "sbi"


class HDFCParser(AMCParser):
    parser_name = "hdfc"


class NipponParser(AMCParser):
    parser_name = "nippon"


class AxisParser(AMCParser):
    parser_name = "axis"


class KotakParser(AMCParser):
    parser_name = "kotak"


class ICICIPrudentialParser(AMCParser):
    parser_name = "icici_prudential"


class QuantParser(AMCParser):
    parser_name = "quant"

    def post_process(self, frame):
        security_series = frame["security_name"].astype(str).str.lower()
        rest_mask = (
            security_series.str.contains("treasury bill", na=False)
            | security_series.str.contains("gilt fund", na=False)
            | security_series.str.contains("treps", na=False)
            | security_series.str.contains("net current assets", na=False)
        )
        frame.loc[rest_mask, "holding_category"] = "rest"
        return frame


class BandhanParser(AMCParser):
    parser_name = "bandhan"


class FranklinTempletonParser(AMCParser):
    parser_name = "franklin_templeton"


class AdityaBirlaSunLifeParser(AMCParser):
    parser_name = "aditya_birla_sun_life"


class CanaraRobecoParser(AMCParser):
    parser_name = "canara_robeco"


class TataParser(AMCParser):
    parser_name = "tata"


class UTIParser(AMCParser):
    parser_name = "uti"


class BankOfIndiaParser(AMCParser):
    parser_name = "bank_of_india"


class InvescoParser(AMCParser):
    parser_name = "invesco"


class HSBCParser(AMCParser):
    parser_name = "hsbc"


class ITIParser(AMCParser):
    parser_name = "iti"


class SundaramParser(AMCParser):
    parser_name = "sundaram"


class TrustParser(AMCParser):
    parser_name = "trust"
