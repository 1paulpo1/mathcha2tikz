import logging
import re
from typing import List, Optional, Tuple, TypedDict


from modules.shapes.lines.style_utils import STYLE_BLOCK_PATTERN, parse_style_blocks

logger = logging.getLogger('modules.shapes.arc.parser')


ArcStyles = TypedDict(
    'ArcStyles',
    {
        'color': str,
        'opacity': float,
        'dash pattern': str,
    },
    total=False,
)


class ArcParser:
    r"""Parser for Arc raw TikZ blocks.

    Returns (main_command, arrow_commands, styles_dict)
    - main_command: visible \draw line with bezier controls (exclude draw opacity=0)
    - arrow_commands: list of auxiliary \draw lines with [shift=(), rotate=...] for arrowheads
    - styles_dict: extracted inline styles (color, draw opacity, dash pattern)
    """

    def parse_shape(self, raw_block: str) -> Tuple[Optional[str], List[str], ArcStyles]:
        raw_block = raw_block or ''
        logger.debug('ArcParser.parse_shape: start, raw length=%d', len(raw_block))
        lines = [ln.strip() for ln in raw_block.strip().split('\n') if ln.strip()]

        main_command = None
        arrow_commands: List[str] = []
        styles_dict: ArcStyles = ArcStyles()

        # Split multiple \draw commands on same line (Arc 4 case)
        all_draw_commands: List[str] = []
        for line in lines:
            # Split by \draw but keep \draw prefix
            parts = line.split(r'\draw')
            for i, part in enumerate(parts):
                if i == 0 and not part.strip():
                    continue  # Skip empty first part
                if part.strip():
                    cmd = r'\draw' + part.strip()
                    all_draw_commands.append(cmd)

        # Choose visible bezier draw (exclude draw opacity=0); prefer the longest with controls
        candidates: List[str] = []
        for s in all_draw_commands:
            if not s.startswith(r'\draw'):
                continue
            if 'shift={' in s or 'shift ={' in s:
                arrow_commands.append(s)
                continue
            if 'draw opacity=0' in s:
                continue
            if ('..' in s and 'controls' in s and 'and' in s):
                candidates.append(s)

        logger.debug(
            'ArcParser.parse_shape: candidates=%d arrow_commands=%d',
            len(candidates),
            len(arrow_commands),
        )
        if candidates:
            main_command = max(candidates, key=len)
            logger.debug('ArcParser.parse_shape: selected main bezier command length=%d', len(main_command))

            style_blocks = STYLE_BLOCK_PATTERN.findall(main_command)
            if style_blocks:
                parsed_styles = parse_style_blocks(style_blocks)
                styles_dict.update(parsed_styles)  # type: ignore[arg-type]

        logger.debug(
            'ArcParser.parse_shape: result has_main=%s styles_keys=%s arrows=%d',
            bool(main_command),
            list(styles_dict.keys()),
            len(arrow_commands),
        )
        return main_command, arrow_commands, styles_dict