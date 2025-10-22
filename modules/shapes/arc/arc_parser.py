import logging
from typing import List, Optional, Tuple

from utils.parsing.base_parser import BaseParser
from utils.shapes.styles import StyleDict

logger = logging.getLogger('modules.shapes.arc.parser')


class ArcParser(BaseParser):
    r"""Parser for Arc raw TikZ blocks.

    Returns (main_command, arrow_commands, styles_dict)
    - main_command: visible \draw line with bezier controls (exclude draw opacity=0)
    - arrow_commands: list of auxiliary \draw lines with [shift=(), rotate=...] for arrowheads
    - styles_dict: extracted inline styles (color, draw opacity, dash pattern)
    """

    def __init__(self) -> None:
        super().__init__(require_bezier=True, exclude_opacity_zero=True)

    def parse_shape(self, raw_block: str) -> Tuple[Optional[str], List[str], StyleDict]:
        main_command, arrow_commands, styles = super().parse_shape(raw_block)
        styles_dict: StyleDict = StyleDict()
        if styles:
            styles_dict.update(styles)  # type: ignore[arg-type]
        logger.debug(
            'ArcParser.parse_shape: result has_main=%s styles_keys=%s arrows=%d',
            bool(main_command),
            list(styles_dict.keys()),
            len(arrow_commands),
        )
        return main_command, arrow_commands, styles_dict