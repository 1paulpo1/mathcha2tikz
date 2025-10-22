from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from utils.style_utils import (
    merge_style_str_with_dict,
    style_dict_to_str,
    format_number,
    apply_arrow_styles,
    append_style_token,
)
from utils.id_utils import build_id_header
from utils.arrows.normalize import normalize_arrows


class BaseRenderer:
    shape_label: str = ""

    def _fmt_num(self, value: Any) -> str:
        return format_number(value)

    def _format_coord(self, v: Any) -> str:
        try:
            if isinstance(v, float) and v.is_integer():
                return str(int(v))
            if isinstance(v, (int, float)):
                return str(v)
        except Exception:
            pass
        return str(v)

    def _format_point(self, p: Tuple[float, float]) -> str:
        x, y = p
        return f"({self._format_coord(x)}, {self._format_coord(y)})"

    def style_from_dict(self, styles: Dict[str, Any]) -> str:
        return style_dict_to_str(styles, self._fmt_num)

    def merge_styles(self, style_str: str, styles: Dict[str, Any]) -> str:
        return merge_style_str_with_dict(style_str, styles, self._fmt_num)

    def apply_arrows(self, style_str: str, arrows_info: Dict[str, Any]) -> str:
        normalized = normalize_arrows(arrows_info)
        return apply_arrow_styles(style_str, normalized)

    def append_style(self, style_str: str, token: str) -> str:
        return append_style_token(style_str, token)

    def id_header(self, shape_id: Optional[str], raw: str = "") -> str:
        label = self.shape_label or "Shape"
        return build_id_header(label, shape_id, raw)

    def id_header_with_label(self, label: str, shape_id: Optional[str], raw: str = "") -> str:
        return build_id_header(label, shape_id, raw)

    def passthrough(self, processed: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if 'raw' in processed:
            return {'tikz_code': processed['raw']}
        if 'tikz_code' in processed:
            return {'tikz_code': processed['tikz_code']}
        return None
