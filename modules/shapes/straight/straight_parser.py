from typing import List, Optional, Tuple

from utils.parsing.base_parser import BaseParser
from utils.shapes.styles import StyleDict


ParsedStraight = Tuple[Optional[str], List[str], StyleDict]


class StraightParser(BaseParser):
    """Parser for Straight Lines raw TikZ blocks.

    Responsibilities:
    - Extract the main straight `\\draw` line command (without shift/rotate/controls)
    - Collect arrow-related commands (lines with shift/cycle) for later processing
    - Parse inline style attributes (currently: color, draw opacity)

    Returns a tuple: (main_line:str|None, arrow_commands:list[str], styles_dict:dict)
    Assumes input is a single shape block containing one primary straight segment.
    """
    def __init__(self) -> None:
        def main_filter(s: str) -> bool:
            return ("--" in s) and ("shift" not in s) and ("rotate" not in s) and ("controls" not in s)

        super().__init__(require_bezier=False, require_closed=False, exclude_opacity_zero=False, main_filter=main_filter)

    def parse_shape(self, raw_block: str) -> ParsedStraight:
        return super().parse_shape(raw_block)