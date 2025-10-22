from typing import Dict, Any

from utils.rendering.base_renderer import BaseRenderer


class EllipseRenderer(BaseRenderer):
    """Render ellipse/circle TikZ command from processed data.

    Expected keys in processed data:
    - center: (cx, cy)
    - major_axis: float (semi-major axis)
    - minor_axis: float (semi-minor axis)
    - rotation: float (degrees)
    - is_circle: bool
    - styles: dict (e.g., {color: ..., opacity: ..., 'dash pattern': {...}})
    - id: optional shape id
    """

    def render(self, processed: Dict[str, Any]) -> Dict[str, Any]:
        passthrough = self.passthrough(processed)
        if passthrough:
            return passthrough
        center = processed.get('center') or (0, 0)
        cx, cy = center
        a = processed.get('major_axis')
        b = processed.get('minor_axis')
        rotation = float(processed.get('rotation', 0.0) or 0.0)
        is_circle = bool(processed.get('is_circle', False))
        styles_dict = processed.get('styles', {}) or {}

        # Build base style string
        style_str = self.style_from_dict(styles_dict)

        # Add rotate around for ellipses only if there is a significant rotation
        if not is_circle and abs(rotation) >= 0.5:
            rot_part = f"rotate around = {{{self._fmt_num(rotation)} : ({self._fmt_num(cx)}, {self._fmt_num(cy)})}}"
            style_str = self.append_style(style_str, rot_part)

        # ID comment header
        id_line = ''
        if processed.get('id'):
            shape_label = 'Circle' if is_circle else 'Ellipse'
            id_line = self.id_header_with_label(shape_label, processed.get('id'), processed.get('raw', ''))

        # Build command
        if is_circle:
            r = a if a is not None else b
            r = r or 0
            cmd = f"{id_line}\\draw{style_str} ({self._fmt_num(cx)}, {self._fmt_num(cy)}) circle ({self._fmt_num(r)});"
        else:
            cmd = (
                f"{id_line}\\draw{style_str} ({self._fmt_num(cx)}, {self._fmt_num(cy)}) "
                f"ellipse ({self._fmt_num(a)} and {self._fmt_num(b)});"
            )

        return {'tikz_code': cmd}

