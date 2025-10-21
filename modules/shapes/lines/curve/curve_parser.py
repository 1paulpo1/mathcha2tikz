from __future__ import annotations

import logging
from typing import List, Optional, Tuple, TypedDict

from mathcha2tikz.utils.style_utils import (
    STYLE_BLOCK_PATTERN,
    parse_style_blocks,
)


logger = logging.getLogger('modules.shapes.lines.curve_parser')

DRAW_PREFIX = '\draw'
CONTROL_TOKEN = 'controls'
AND_TOKEN = 'and'
SHIFT_TOKEN = 'shift'
ROTATE_TOKEN = 'rotate'
CYCLE_TOKEN = 'cycle'

CurveStyles = TypedDict('CurveStyles', {
    'color': str,
    'opacity': float,
    'dash pattern': str,
}, total=False)


class CurveParser:
    """Parser for Curve Lines raw TikZ blocks.

    Responsibilities:
    - Extract the main curve "\\draw" line that contains bezier controls (.. controls .. and ..)
    - Collect arrow-related commands (lines with shift/rotate) for later processing
    - Parse inline style attributes (currently: color, draw opacity)

    Returns a tuple: (main_line:str|None, arrow_commands:list[str], styles_dict:dict)
    Assumes input is a single shape block containing one primary curve path.
    """

    def parse_shape(self, raw_block: str) -> Tuple[Optional[str], List[str], CurveStyles]:
        lines = raw_block.strip().split('\n')

        main_line: Optional[str] = None
        arrow_commands: List[str] = []
        styles_dict: CurveStyles = CurveStyles()

        for raw_line in lines:
            line = raw_line.strip()
            if not line or line.startswith('%'):
                continue

            if not line.startswith(DRAW_PREFIX):
                continue

            # Identify main curve command: must contain bezier controls
            if (
                '..' in line
                and CONTROL_TOKEN in line
                and AND_TOKEN in line
                and SHIFT_TOKEN not in line
                and ROTATE_TOKEN not in line
            ):
                if main_line is None:
                    main_line = line
                    # Extract styles ONLY from main curve command
                    style_blocks = STYLE_BLOCK_PATTERN.findall(line)
                    parsed_styles = parse_style_blocks(style_blocks)
                    styles_dict.update(parsed_styles)  # type: ignore[arg-type]
                    logger.debug("Main curve command identified: %s", line)
            # Arrow heads or auxiliary draws
            elif (
                SHIFT_TOKEN in line
                or ROTATE_TOKEN in line
                or CYCLE_TOKEN in line
            ):
                arrow_commands.append(line)

        return main_line, arrow_commands, styles_dict

