"""Shared utilities for line-based renderers (straight, curve, etc.)."""


from typing import Any, Callable, Dict, List, Optional
import re


StyleFormatter = Callable[[Any], str]


def format_number(value: Any) -> str:
    """Format numeric values similarly to existing renderer helpers."""
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if abs(value - round(value)) < 1e-9:
            return str(int(round(value)))
        formatted = f"{value:.2f}"
        return formatted.rstrip('0').rstrip('.')
    return str(value)


def split_style_parts(style_content: str) -> List[str]:
    """Split a style string content into top-level comma-separated parts.

    Keeps brace nesting intact so that patterns like ``decoration={...}`` remain whole.
    """
    parts: List[str] = []
    current: List[str] = []
    brace_depth = 0

    for char in style_content:
        if char == '{':
            brace_depth += 1
            current.append(char)
        elif char == '}':
            brace_depth -= 1
            current.append(char)
        elif char == ',' and brace_depth == 0:
            part = ''.join(current).strip()
            if part:
                parts.append(part)
            current = []
        else:
            current.append(char)

    part = ''.join(current).strip()
    if part:
        parts.append(part)

    return parts


def merge_style_str_with_dict(
    style_str: Optional[str],
    styles: Dict[str, Any],
    fmt_num: StyleFormatter,
) -> str:
    """Merge a style string with additional style key/value pairs.

    - Preserves existing tokens (including arrow markers).
    - Avoids duplicating keys like ``dash pattern`` and ``draw opacity``.
    - Formats numeric values via ``fmt_num`` to keep renderer-specific precision.
    """
    if not styles:
        return style_str or ''

    content = ''
    if style_str:
        stripped = style_str.strip()
        content = stripped[1:-1] if stripped.startswith('[') and stripped.endswith(']') else stripped

    tokens = split_style_parts(content) if content else []

    present_keys = set()
    for token in tokens:
        if '=' in token:
            key, _ = token.split('=', 1)
            present_keys.add(key.strip())

    additions: List[str] = []
    for key, value in styles.items():
        if key == 'dash pattern':
            if 'dash pattern' not in present_keys:
                additions.append(f"dash pattern = {value}")
        elif key == 'opacity':
            if 'draw opacity' not in present_keys and 'opacity' not in present_keys:
                additions.append(f"draw opacity = {fmt_num(value)}")
        else:
            if key not in present_keys:
                additions.append(f"{key}={value}")

    merged = tokens + additions if additions else tokens
    return f"[{', '.join(merged)}]" if merged else ''


def style_dict_to_str(styles: Dict[str, Any], fmt_num: StyleFormatter = format_number) -> str:
    """Convert a style dictionary to a TikZ style string."""
    if not styles:
        return ''
    parts: List[str] = []
    for key, value in styles.items():
        if key == 'dash pattern':
            parts.append(f"dash pattern = {value}")
        elif key == 'opacity':
            parts.append(f"draw opacity = {fmt_num(value)}")
        else:
            parts.append(f"{key}={value}")
    return '[' + ', '.join(parts) + ']'


STYLE_BLOCK_PATTERN = re.compile(r'\[([^\]]+)\]')
COLOR_PATTERN = re.compile(r'color\s*=\s*(\{[^}]+\}|[^,\]]+)')
OPACITY_PATTERN = re.compile(r'draw\s+opacity\s*=\s*([\d.]+)')
DASH_PATTERN = re.compile(r'dash\s*pattern\s*=\s*\{[^}]+\}')
ARROW_MARKER_PATTERN = re.compile(r',?\s*[-<]?>')


def parse_style_blocks(style_blocks: List[str]) -> Dict[str, Any]:
    """Parse style tokens (color, opacity, dash pattern) from raw blocks."""
    styles: Dict[str, Any] = {}
    for style_str in style_blocks:
        color_match = COLOR_PATTERN.search(style_str)
        if color_match:
            styles['color'] = color_match.group(1)

        opacity_match = OPACITY_PATTERN.search(style_str)
        if opacity_match:
            try:
                styles['opacity'] = float(opacity_match.group(1))
            except ValueError:
                pass

        dash_match = DASH_PATTERN.search(style_str)
        if dash_match:
            styles['dash pattern'] = dash_match.group(0).split('=', 1)[1].strip()

    return styles


def apply_arrow_styles(style_str: str, arrows_info: Dict[str, Any]) -> str:
    """Apply start/end and mid-arrow decorations to a TikZ style string."""
    style_str = style_str or ''
    style_str = ARROW_MARKER_PATTERN.sub('', style_str)

    start_arrow = arrows_info.get('start_arrow')
    end_arrow = arrows_info.get('end_arrow')
    mid_arrows = arrows_info.get('mid_arrows') or []

    arrow_style = ''
    if start_arrow and end_arrow:
        arrow_style = f"{start_arrow}-{end_arrow}"
    elif start_arrow:
        arrow_style = f"{start_arrow}-"
    elif end_arrow:
        arrow_style = f"-{end_arrow}"

    if arrow_style:
        if style_str:
            if style_str.endswith(']'):
                style_str = style_str[:-1] + f', {arrow_style}]'
            else:
                style_str = f'[{style_str}, {arrow_style}]'
        else:
            style_str = f'[{arrow_style}]'

    if mid_arrows:
        sorted_mid = sorted(mid_arrows, key=lambda arrow: arrow.get('position', 0))
        marks = [
            f"mark = at position {arrow['position']:.2f} with {{\\arrow{{{arrow['direction']}}}}}"
            for arrow in sorted_mid
        ]
        if marks:
            marks_str = ",\n    ".join(marks)
            decoration = f"decoration = {{markings, {marks_str}}}, postaction = {{decorate}}"
            if style_str:
                if style_str.endswith(']'):
                    style_str = style_str[:-1] + f', {decoration}]'
                else:
                    style_str = f'[{style_str}, {decoration}]'
            else:
                style_str = f'[{decoration}]'

    return style_str


def append_style_token(style_str: str, token: str) -> str:
    """Append a single style token to an existing TikZ style string.

    Handles edge cases like empty strings and missing brackets.
    """
    token = token.strip()
    if not token:
        return style_str or ''

    style_str = style_str or ''
    if style_str:
        stripped = style_str.strip()
        if stripped.startswith('[') and stripped.endswith(']'):
            content = stripped[1:-1]
            content = f"{content}, {token}" if content else token
            return f"[{content}]"

        return f"[{stripped}, {token}]"

    return f"[{token}]"
