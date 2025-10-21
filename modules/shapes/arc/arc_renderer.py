from typing import Dict, Any

from utils.id_utils import build_id_header
from utils.style_utils import (
    apply_arrow_styles,
    append_style_token,
    format_number,
    style_dict_to_str,
)


class ArcRenderer:
    """Render elliptical arc TikZ command from processed data."""

    def _fmt_num(self, value: Any) -> str:
        return format_number(value)

    def _style_from_dict(self, styles: Dict[str, Any]) -> str:
        return style_dict_to_str(styles, self._fmt_num)

    def render(self, data: Dict[str, Any]) -> Dict[str, Any]:
        cx, cy = data.get('center', (0, 0))
        a = data.get('major_axis', 0)
        b = data.get('minor_axis', 0)
        start_ang = data.get('start_angle', 0)
        end_ang = data.get('end_angle', 0)
        rotation = float(data.get('rotation', 0.0) or 0.0)

        style_str = self._style_from_dict(data.get('styles', {}) or {})

        # Normalize arrows info keys to what apply_arrow_styles expects
        arrows = data.get('arrows', {}) or {}
        if arrows:
            normalized_arrows = {}
            # Support both {'start_arrow','end_arrow'} and {'start','end'}
            if 'start_arrow' in arrows or 'start' in arrows:
                normalized_arrows['start_arrow'] = arrows.get('start_arrow', arrows.get('start'))
            if 'end_arrow' in arrows or 'end' in arrows:
                normalized_arrows['end_arrow'] = arrows.get('end_arrow', arrows.get('end'))
            if 'mid_arrows' in arrows:
                normalized_arrows['mid_arrows'] = arrows.get('mid_arrows')
            style_str = apply_arrow_styles(style_str, normalized_arrows)
        else:
            style_str = apply_arrow_styles(style_str, {})

        if abs(rotation) >= 0.5:
            rot_part = f"rotate around = {{{self._fmt_num(rotation)} : ({self._fmt_num(cx)}, {self._fmt_num(cy)})}}"
            style_str = append_style_token(style_str, rot_part)

        id_line = ''
        if data.get('id'):
            id_line = build_id_header('Arc', data.get('id'), data.get('raw', ''))

        shift = (
            f"([shift = {{({self._fmt_num(cx)}, {self._fmt_num(cy)})}}] "
            f"{self._fmt_num(start_ang)} : {self._fmt_num(a)} and {self._fmt_num(b)})"
        )
        arc = (
            f"arc ({self._fmt_num(start_ang)} : {self._fmt_num(end_ang)} : "
            f"{self._fmt_num(a)} and {self._fmt_num(b)})"
        )
        cmd = f"{id_line}\\draw{style_str} {shift} {arc};"
        return {'tikz_code': cmd}
