from __future__ import annotations
import logging
from typing import List, Optional, Tuple

from utils.parsing.base_parser import BaseParser
from utils.shapes.styles import StyleDict


logger = logging.getLogger('modules.shapes.curve_parser')


class CurveParser(BaseParser):
    """Parser for Curve Lines raw TikZ blocks.

    Responsibilities:
    - Extract the main curve "\\draw" line that contains bezier controls (.. controls .. and ..)
    - Collect arrow-related commands (lines with shift/rotate/cycle) for later processing
    - Parse inline style attributes (currently: color, draw opacity)

    Returns a tuple: (main_line:str|None, arrow_commands:list[str], styles_dict:dict)
    Assumes input is a single shape block containing one primary curve path.
    """

    def __init__(self) -> None:
        # Preserve previous behavior: do not exclude opacity=0 here
        super().__init__(require_bezier=True, exclude_opacity_zero=False)

    def parse_shape(self, raw_block: str) -> Tuple[Optional[str], List[str], StyleDict]:
        main_line, arrow_commands, styles = super().parse_shape(raw_block)
        styles_dict: StyleDict = StyleDict()
        if styles:
            styles_dict.update(styles)  # type: ignore[arg-type]
        return main_line, arrow_commands, styles_dict

