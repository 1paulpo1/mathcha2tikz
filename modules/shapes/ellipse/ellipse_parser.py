from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple

from utils.parsing.base_parser import BaseParser


from utils.shapes.styles import StyleDict

logger = logging.getLogger('modules.shapes.ellipse.ellipse_parser')


class EllipseParser(BaseParser):
    r"""Parser for Ellipse/Circle raw TikZ bezier blocks (closed with ``-- cycle``).

    Returns a tuple ``(main_command, extra_commands, styles_dict)`` where:

    - ``main_command`` — string ``\draw`` with bezier controls and ``-- cycle``
    - ``extra_commands`` — additional lines (usually empty)
    - ``styles_dict`` — extracted inline styles (color, draw opacity, dash pattern)
    """

    def __init__(self) -> None:
        super().__init__(require_bezier=True, require_closed=True, exclude_opacity_zero=False)

    def parse_shape(self, raw_block: str) -> Tuple[Optional[str], List[str], StyleDict]:
        main_command, arrow_commands, styles = super().parse_shape(raw_block)
        styles_dict: StyleDict = StyleDict()
        if styles:
            styles_dict.update(styles)  # type: ignore[arg-type]

        if main_command is None:
            logger.debug("No main ellipse command found in block")

        return main_command, arrow_commands, styles_dict

