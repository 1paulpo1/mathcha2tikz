from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import math
import logging

from core.exceptions import ProcessingError
from core.shape_payload import ShapePayload
from utils.geometry.shared_arrow_logic import (
    parse_points_from_draw,
    extract_arrow_anchor,
)
from .arc_parser import ArcParser
from .arc_renderer import ArcRenderer
from .arc_arrows import process_arc_arrows, ArcArrowData, ArcArrowResult
from utils.processing.base_shape_processor import BaseShapeProcessor
from utils.shapes.types import Point, ArcPayload

from utils.geometry.point_path_operations import (
    split_bezier_into_segments,
    get_ellipse_points_from_bezier,
    normalize_arc_angles,
)
from utils.geometry.base_geometry import (
    compute_conic_coefficients,
    compute_ellipse_params,
)
from utils.geometry.conics.conic_core import compute_parametric_angle


logger = logging.getLogger('modules.shapes.arc.processor')


@dataclass
class ArcInput:
    """Локальное описание входного payload для `ArcProcessor`.

    Поля читаются через getattr и являются опциональными.
    """
    id: Optional[str] = None
    raw_block: Optional[str] = None
    raw_command: Optional[str] = None
    annotation: Optional[str] = None
    shape_type: Optional[str] = None


class ArcProcessor(BaseShapeProcessor):
    def __init__(self, shape_instance: Optional[ShapePayload] = None) -> None:
        super().__init__(shape_instance, parser=ArcParser(), renderer=ArcRenderer())
        # Defer rendering to GlobalRenderer via type='Arc'
        self.use_inline_renderer = False

    def _points_from_main(self, main_command: str) -> List[Point]:
        return parse_points_from_draw(main_command)

    def _build_arrow_payload(
        self,
        segments: List[List[Point]],
        arrow_commands: List[str],
    ) -> ArcArrowResult:
        # Build arrow_info by parsing auxiliary arrow commands
        arrow_info: Dict[str, Dict[str, float]] = {}

        try:
            if segments:
                start_pt = segments[0][0]
                end_pt = segments[-1][-1]
            else:
                start_pt = end_pt = (0.0, 0.0)

            for cmd in arrow_commands or []:
                anchor = extract_arrow_anchor(cmd)
                if not anchor:
                    continue
                ax, ay = anchor.position
                # Choose closest endpoint
                ds = (start_pt[0] - ax) ** 2 + (start_pt[1] - ay) ** 2
                de = (end_pt[0] - ax) ** 2 + (end_pt[1] - ay) ** 2
                if ds <= de:
                    # Assign to start if not set yet
                    if 'start' not in arrow_info:
                        arrow_info['start'] = {'rotation': float(anchor.rotation)}
                else:
                    if 'end' not in arrow_info:
                        arrow_info['end'] = {'rotation': float(anchor.rotation)}
        except Exception:
            # Fail-safe: no arrows
            arrow_info = {}

        data: ArcArrowData = {
            'segments': tuple(tuple(seg) for seg in segments),
            'arrow_info': arrow_info,  # may be empty
        }
        return process_arc_arrows(data)

    def process_arrows(self, main: str, arrow_cmds: List[str]) -> Dict[str, Any]:
        points = self._points_from_main(main)
        if len(points) < 4:
            return {}
        segments = split_bezier_into_segments(points)
        arrows = self._build_arrow_payload(segments, arrow_cmds)
        return {'arrows': arrows}

    def build_render_payload(self, main: str, styles: Dict[str, Any], extras: Dict[str, Any]) -> Dict[str, Any]:
        raw_block = extras.get('_raw_block', '')
        arrow_cmds = extras.get('_arrow_cmds', [])
        points = self._points_from_main(main)
        if len(points) < 4:
            logger.debug("ArcProcessor: insufficient points (%d), passthrough", len(points))
            return {'tikz_code': raw_block}

        try:
            segments = split_bezier_into_segments(points)
        except Exception as exc:  # pragma: no cover
            logger.exception("Failed to split bezier segments")
            raise ProcessingError("Failed to split arc segments") from exc

        ellipse_points = get_ellipse_points_from_bezier(segments)
        if len(ellipse_points) < 5:
            logger.debug("ArcProcessor: <5 ellipse points (%d), passthrough", len(ellipse_points))
            return {'tikz_code': raw_block}

        try:
            coeffs = compute_conic_coefficients(ellipse_points)
        except Exception as exc:  # pragma: no cover
            logger.exception("Failed to compute conic coefficients")
            raise ProcessingError("Failed to compute arc conic coefficients") from exc

        if not coeffs:
            logger.debug("ArcProcessor: conic coefficient failure, passthrough")
            return {'tikz_code': raw_block}

        try:
            params = compute_ellipse_params(*coeffs)
        except Exception as exc:  # pragma: no cover
            logger.exception("Failed to compute ellipse params")
            raise ProcessingError("Failed to compute ellipse parameters") from exc

        if not params:
            logger.debug("ArcProcessor: ellipse params missing, passthrough")
            return {'tikz_code': raw_block}

        cx, cy, major, minor, rotation_deg = params
        rotation_rad = math.radians(rotation_deg)

        start_point = points[0]
        end_point = points[-1]
        try:
            start_angle_deg = math.degrees(compute_parametric_angle(start_point, (cx, cy), major, minor, rotation_rad))
            end_angle_deg = math.degrees(compute_parametric_angle(end_point, (cx, cy), major, minor, rotation_rad))
        except Exception as exc:  # pragma: no cover
            logger.exception("Failed to compute parametric angles")
            raise ProcessingError("Failed to compute arc angles") from exc

        start_norm, end_norm, rotation_out = normalize_arc_angles(start_angle_deg, end_angle_deg, rotation_deg)

        arrows = extras.get('arrows')
        if not arrows:
            arrows = self._build_arrow_payload(segments, arrow_cmds)

        processed: ArcPayload = {
            'center': (cx, cy),
            'major_axis': major,
            'minor_axis': minor,
            'rotation': rotation_out,
            'start_angle': start_norm,
            'end_angle': end_norm,
            'styles': styles,
            'arrows': arrows,
            'type': 'Arc',
        }

        return processed