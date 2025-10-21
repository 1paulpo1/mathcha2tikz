from typing import Dict, Any, List, Tuple

from utils.style_utils import (
    merge_style_str_with_dict,
    split_style_parts,
    format_number,
    style_dict_to_str,
    apply_arrow_styles,
)
from utils.id_utils import build_id_header

class CurveRenderer:
    def _fmt_num(self, value: float) -> str:
        return format_number(value)

    def _style_from_dict(self, styles: Dict[str, Any]) -> str:
        return style_dict_to_str(styles, self._fmt_num)

    def _format_coord(self, v: float) -> str:
        return f"{int(v) if isinstance(v, float) and v.is_integer() else v}"

    def _format_point(self, p: Tuple[float, float]) -> str:
        x, y = p
        return f"({self._format_coord(x)}, {self._format_coord(y)})"

    def _build_path(self, segments: List[List[Tuple[float, float]]], is_closed: bool) -> str:
        if not segments:
            return ''

        parts: List[str] = []
        for i, seg in enumerate(segments):
            if len(seg) != 4:
                continue
            p0, c1, c2, p3 = seg
            p0s, c1s, c2s, p3s = (
                self._format_point(p0),
                self._format_point(c1),
                self._format_point(c2),
                self._format_point(p3),
            )
            if i == 0:
                parts.append(f"{p0s} .. controls {c1s} and {c2s} .. {p3s}")
            else:
                parts.append(f".. controls {c1s} and {c2s} .. {p3s}")

        if is_closed:
            parts.append("-- cycle")

        # Multi-segment curves format with line breaks for readability
        return "\n    ".join(parts) if len(segments) > 1 else " ".join(parts)

    def render(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Render curve TikZ command from processed data.

        processed_data keys expected:
        - style_str, start_point, end_point, segments, is_closed, id (optional)
        - mid_arrows, start_arrow, end_arrow
        """
        if 'raw' in processed_data:
            return {'tikz_code': processed_data['raw']}
            return {'tikz_code': processed_data['tikz_code']}

        style_str = processed_data.get('style_str', '')
        styles_dict = processed_data.get('styles') or {}
        if styles_dict:
            style_str = merge_style_str_with_dict(style_str, styles_dict, self._fmt_num)
        segments = processed_data.get('segments', [])
        is_closed = bool(processed_data.get('is_closed', False))

        # Inject arrows/decorations
        style_str = apply_arrow_styles(style_str, processed_data)
        # Build path
        path_str = self._build_path(segments, is_closed)

        # ID comment header
        id_line = ""
        if processed_data.get('id'):
            id_line = build_id_header("Curve Lines", processed_data.get('id'), processed_data.get('raw', ''))

        cmd = f"{id_line}\\draw{style_str} {path_str};"
        return {'tikz_code': cmd}

