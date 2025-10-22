from typing import Dict, Any

from utils.rendering.base_renderer import BaseRenderer


class ArcRenderer(BaseRenderer):
    """Render elliptical arc TikZ command from processed data."""

    shape_label = "Arc"

    def render(self, data: Dict[str, Any]) -> Dict[str, Any]:
        cx, cy = data.get('center', (0, 0))
        a = data.get('major_axis', 0)
        b = data.get('minor_axis', 0)
        start_ang = data.get('start_angle', 0)
        end_ang = data.get('end_angle', 0)
        rotation = float(data.get('rotation', 0.0) or 0.0)

        style_str = self.style_from_dict(data.get('styles', {}) or {})
        arrows = data.get('arrows', {}) or {}
        style_str = self.apply_arrows(style_str, arrows)

        if abs(rotation) >= 0.5:
            rot_part = f"rotate around = {{{self._fmt_num(rotation)} : ({self._fmt_num(cx)}, {self._fmt_num(cy)})}}"
            style_str = self.append_style(style_str, rot_part)

        id_line = ''
        if data.get('id'):
            id_line = self.id_header(data.get('id'), data.get('raw', ''))

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
