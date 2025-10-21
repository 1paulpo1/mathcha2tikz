from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple, TypedDict

from mathcha2tikz.utils.style_utils import STYLE_BLOCK_PATTERN, parse_style_blocks


logger = logging.getLogger('modules.shapes.ellipse.ellipse_parser')


EllipseStyles = TypedDict(
    'EllipseStyles',
    {
        'color': str,
        'opacity': float,
        'dash pattern': str,
    },
    total=False,
)


class EllipseParser:
    r"""Parser for Ellipse/Circle raw TikZ bezier blocks (closed with ``-- cycle``).

    Returns a tuple ``(main_command, extra_commands, styles_dict)`` where:

    - ``main_command`` — string ``\draw`` with bezier controls and ``-- cycle``
    - ``extra_commands`` — additional lines (usually empty)
    - ``styles_dict`` — extracted inline styles (color, draw opacity, dash pattern)
    """

    def parse_shape(self, raw_block: str) -> Tuple[Optional[str], List[str], EllipseStyles]:
        lines = raw_block.strip().split('\n')

        main_command: Optional[str] = None
        extra_commands: List[str] = []
        styles_dict: EllipseStyles = EllipseStyles()

        for raw_line in lines:
            s = raw_line.strip()
            if not s or s.startswith('%'):
                continue

            if not s.startswith(r'\draw'):
                continue

            # Extract styles
            style_blocks = STYLE_BLOCK_PATTERN.findall(s)
            if style_blocks:
                parsed = parse_style_blocks(style_blocks)
                styles_dict.update(parsed)  # type: ignore[arg-type]

            # Identify main closed bezier command
            if ('..' in s and 'controls' in s and 'and' in s and '-- cycle' in s):
                if main_command is None:
                    main_command = s
            else:
                # Keep other draw lines if needed in future
                if s != main_command:
                    extra_commands.append(s)

        if main_command is None:
            logger.debug("No main ellipse command found in block")

        return main_command, extra_commands, styles_dict

