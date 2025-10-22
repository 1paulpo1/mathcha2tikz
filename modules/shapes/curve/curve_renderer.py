from typing import Dict, Any, List, Tuple

from utils.rendering.base_renderer import BaseRenderer
from utils.rendering.path_builder import build_curve_path


class CurveRenderer(BaseRenderer):
    shape_label = "Curve Lines"

    def _format_coord(self, v: float) -> str:
        return f"{int(v) if isinstance(v, float) and v.is_integer() else v}"

    def _format_point(self, p: Tuple[float, float]) -> str:
        x, y = p
        return f"({self._format_coord(x)}, {self._format_coord(y)})"

    def render(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Render curve TikZ command from processed data.

        processed_data keys expected:
        - style_str, start_point, end_point, segments, is_closed, id (optional)
        - mid_arrows, start_arrow, end_arrow
        """
        passthrough = self.passthrough(processed_data)
        if passthrough:
            return passthrough

        style_str = processed_data.get('style_str', '')
        styles_dict = processed_data.get('styles') or {}
        if styles_dict:
            style_str = self.merge_styles(style_str, styles_dict)
        segments = processed_data.get('segments', [])
        is_closed = bool(processed_data.get('is_closed', False))

        # Inject arrows/decorations
        style_str = self.apply_arrows(style_str, processed_data)
        # Build path
        path_str = build_curve_path(segments, is_closed, self._format_point, multiline=True)

        # ID comment header
        id_line = ""
        if processed_data.get('id'):
            id_line = self.id_header(processed_data.get('id'), processed_data.get('raw', ''))

        cmd = f"{id_line}\\draw{style_str} {path_str};"
        return {'tikz_code': cmd}

