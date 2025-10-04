import re
from typing import List, Dict, Any, Optional, Tuple


DRAW_PREFIX = r"\draw"
MAIN_LINE_TOKEN = "--"
SHIFT_TOKEN = "shift"
ROTATE_TOKEN = "rotate"
CONTROLS_TOKEN = "controls"
CYCLE_TOKEN = "cycle"

STYLE_BLOCK_PATTERN = re.compile(r"\[([^\]]+)\]")
COLOR_PATTERN = re.compile(r"color\s*=\s*(\{[^}]+\}|[^,\]]+)")
OPACITY_PATTERN = re.compile(r"draw\s+opacity\s*=\s*([\d.]+)")
DASH_PATTERN = re.compile(r"dash\s*pattern\s*=\s*\{[^}]+\}")


ParsedStraight = Tuple[Optional[str], List[str], Dict[str, Any]]


def _is_main_line(line: str) -> bool:
    return (
        MAIN_LINE_TOKEN in line
        and SHIFT_TOKEN not in line
        and ROTATE_TOKEN not in line
        and CONTROLS_TOKEN not in line
    )


def _parse_style_block(style_str: str, styles_dict: Dict[str, Any]) -> None:
    color_match = COLOR_PATTERN.search(style_str)
    if color_match:
        styles_dict['color'] = color_match.group(1)

    opacity_match = OPACITY_PATTERN.search(style_str)
    if opacity_match:
        try:
            styles_dict['opacity'] = float(opacity_match.group(1))
        except ValueError:
            pass

    dash_match = DASH_PATTERN.search(style_str)
    if dash_match:
        styles_dict['dash pattern'] = dash_match.group(0).split('=', 1)[1].strip()

class StraightParser:
    """Parser for Straight Lines raw TikZ blocks.

    Responsibilities:
    - Extract the main straight `\\draw` line command (without shift/rotate/controls)
    - Collect arrow-related commands (lines with shift/cycle) for later processing
    - Parse inline style attributes (currently: color, draw opacity)

    Returns a tuple: (main_line:str|None, arrow_commands:list[str], styles_dict:dict)
    Assumes input is a single shape block containing one primary straight segment.
    """
    def parse_shape(self, raw_block: str) -> ParsedStraight:
        """
        Извлекает данные линии, стрелок и стилей из raw-block
        
        Returns:
            tuple: (main_line, arrow_commands, styles_dict)
        """
        lines = raw_block.strip().split('\n')
        
        # Основная команда линии (первая команда с простой линией)
        main_line: Optional[str] = None
        arrow_commands: List[str] = []
        styles_dict: Dict[str, Any] = {}
        
        for raw_line in lines:
            line = raw_line.strip()
            if not line or line.startswith('%'):
                continue

            if not line.startswith(DRAW_PREFIX):
                continue

            if _is_main_line(line):
                if main_line is None:
                    main_line = line
                    for style_str in STYLE_BLOCK_PATTERN.findall(line):
                        _parse_style_block(style_str, styles_dict)
                continue

            if SHIFT_TOKEN in line or CYCLE_TOKEN in line:
                arrow_commands.append(line)

        return main_line, arrow_commands, styles_dict