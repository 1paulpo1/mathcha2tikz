from __future__ import annotations

from typing import Callable, Iterable, List, Optional, Sequence, Tuple, TypedDict
import re

from utils.style_utils import STYLE_BLOCK_PATTERN, parse_style_blocks


DRAW_SPLIT_PATTERN = re.compile(r"(\\draw[^\\]*)")
SHIFT_TOKEN = 'shift'
ROTATE_TOKEN = 'rotate'
CYCLE_TOKEN = 'cycle'
CONTROL_TOKEN = 'controls'


class ParsedShape(TypedDict, total=False):
    main: Optional[str]
    arrows: List[str]
    styles: dict


def iter_draw_commands(raw_block: str) -> List[str]:
    """Split a raw block into individual \draw commands, preserving the prefix."""
    raw = raw_block or ''
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    draws: List[str] = []
    for line in lines:
        if '\\draw' not in line:
            continue
        # Split on \draw but keep it in tokens
        parts = line.split(r'\draw')
        for i, part in enumerate(parts):
            if i == 0 and not part.strip():
                continue
            part = part.strip()
            if part:
                draws.append(r'\draw' + part)
    return draws


def is_arrow_line(s: str) -> bool:
    s = s or ''
    # Only transform lines with explicit arrowhead affine transforms into aux lines.
    # Do NOT treat '-- cycle' as an arrow line; closed paths can be main commands (Ellipse, closed curves).
    return (SHIFT_TOKEN in s) or (ROTATE_TOKEN in s)


def extract_styles(line: str) -> dict:
    blocks = STYLE_BLOCK_PATTERN.findall(line or '')
    if not blocks:
        return {}
    return parse_style_blocks(blocks)


def choose_main_draw(
    draws: Sequence[str],
    *,
    require_bezier: Optional[bool] = None,
    require_closed: Optional[bool] = None,
    exclude_opacity_zero: bool = True,
) -> Optional[str]:
    """Pick the main draw command based on simple heuristics.

    - require_bezier: if True, must contain '.. controls .. and ..'
    - require_closed: if True, must contain '-- cycle'
    - exclude_opacity_zero: skip lines with 'draw opacity=0'
    """
    candidates: List[str] = []
    for s in draws:
        if exclude_opacity_zero and 'draw opacity=0' in s:
            continue
        if require_bezier is True and not ('..' in s and CONTROL_TOKEN in s and 'and' in s):
            continue
        if require_closed is True and '-- cycle' not in s:
            continue
        if require_bezier is False and ('..' in s and CONTROL_TOKEN in s and 'and' in s):
            continue
        candidates.append(s)
    if not candidates:
        return None
    # Prefer the longest (often the primary path)
    return max(candidates, key=len)


def parse_shape_common(
    raw_block: str,
    *,
    require_bezier: Optional[bool] = None,
    require_closed: Optional[bool] = None,
    exclude_opacity_zero: bool = True,
) -> Tuple[Optional[str], List[str], dict]:
    """Generic parse helper used by multiple parsers.

    Returns (main_command, arrow_commands, styles_dict)
    """
    draws = iter_draw_commands(raw_block)
    arrows = [d for d in draws if is_arrow_line(d)]
    body   = [d for d in draws if not is_arrow_line(d)]

    main = choose_main_draw(
        body,
        require_bezier=require_bezier,
        require_closed=require_closed,
        exclude_opacity_zero=exclude_opacity_zero,
    )

    styles = extract_styles(main) if main else {}
    return main, arrows, styles
