from typing import Any, Dict, List, Optional, Tuple, TypedDict, cast
from dataclasses import dataclass
import math
import logging

from core.exceptions import ProcessingError
from core.shape_payload import ShapePayload
from utils.geometry.shared_arrow_logic import (
    Point,
    parse_points_from_draw,
    extract_arrow_anchor,
)
from .arc_parser import ArcParser, ArcStyles
from .arc_renderer import ArcRenderer
from .arc_arrows import process_arc_arrows, ArcArrowData, ArcArrowResult

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


class ArcProcessedData(TypedDict, total=False):
    center: Point
    major_axis: float
    minor_axis: float
    rotation: float
    start_angle: float
    end_angle: float
    styles: ArcStyles
    arrows: ArcArrowResult
    id: str
    type: str


class ArcProcessor:
    def __init__(self, shape_instance: Optional[ShapePayload] = None) -> None:
        self.shape_instance = shape_instance
        self.parser = ArcParser()
        self.renderer = ArcRenderer()

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

    def process(self, raw_block: Optional[str] = None) -> ArcProcessedData:
        if self.shape_instance and not raw_block:
            raw_block = getattr(self.shape_instance, 'raw_block', '') or getattr(self.shape_instance, 'raw_command', '')

        if not raw_block:
            return cast(ArcProcessedData, {'tikz_code': raw_block or ''})

        try:
            main_command, arrow_commands, styles_dict = self.parser.parse_shape(raw_block)
        except Exception as exc:  # pragma: no cover
            logger.exception("ArcParser failed")
            raise ProcessingError("Failed to parse arc block") from exc

        if not main_command:
            logger.debug("ArcProcessor: no main command, returning passthrough")
            return cast(ArcProcessedData, {'tikz_code': raw_block})

        points = self._points_from_main(main_command)
        if len(points) < 4:
            logger.debug("ArcProcessor: insufficient points (%d), passthrough", len(points))
            return cast(ArcProcessedData, {'tikz_code': raw_block})

        try:
            segments = split_bezier_into_segments(points)
        except Exception as exc:  # pragma: no cover
            logger.exception("Failed to split bezier segments")
            raise ProcessingError("Failed to split arc segments") from exc

        ellipse_points = get_ellipse_points_from_bezier(segments)
        if len(ellipse_points) < 5:
            logger.debug("ArcProcessor: <5 ellipse points (%d), passthrough", len(ellipse_points))
            return cast(ArcProcessedData, {'tikz_code': raw_block})

        try:
            coeffs = compute_conic_coefficients(ellipse_points)
        except Exception as exc:  # pragma: no cover
            logger.exception("Failed to compute conic coefficients")
            raise ProcessingError("Failed to compute arc conic coefficients") from exc

        if not coeffs:
            logger.debug("ArcProcessor: conic coefficient failure, passthrough")
            return cast(ArcProcessedData, {'tikz_code': raw_block})

        try:
            params = compute_ellipse_params(*coeffs)
        except Exception as exc:  # pragma: no cover
            logger.exception("Failed to compute ellipse params")
            raise ProcessingError("Failed to compute ellipse parameters") from exc

        if not params:
            logger.debug("ArcProcessor: ellipse params missing, passthrough")
            return cast(ArcProcessedData, {'tikz_code': raw_block})

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

        arrows = self._build_arrow_payload(segments, arrow_commands)

        processed: ArcProcessedData = {
            'center': (cx, cy),
            'major_axis': major,
            'minor_axis': minor,
            'rotation': rotation_out,
            'start_angle': start_norm,
            'end_angle': end_norm,
            'styles': styles_dict,
            'arrows': arrows,
            'type': 'Arc',
        }

        if self.shape_instance is not None:
            shape_id = getattr(self.shape_instance, 'id', None)
            if shape_id:
                processed['id'] = shape_id

        return processed

    def validate(self) -> bool:
        return True