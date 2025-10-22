"""Ellipse Processor

Parses ellipse/circle raw block, fits conic, and prepares data for rendering.
Pipeline: EllipseParser -> ConicFitting -> EllipseRenderer
"""

from __future__ import annotations

import logging
import math
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from core.exceptions import ProcessingError, RenderingError
from core.shape_payload import ShapePayload
from utils.geometry.shared_arrow_logic import parse_points_from_draw
from .ellipse_parser import EllipseParser
from utils.geometry.conics.conic_fitting import main as fit_ellipse
from .ellipse_renderer import EllipseRenderer
from utils.processing.base_shape_processor import BaseShapeProcessor
from utils.shapes.types import Point, EllipsePayload


logger = logging.getLogger('modules.shapes.ellipse.ellipse_processor')


@dataclass
class EllipseInput:
    """Локальное описание входного payload для `EllipseProcessor`.

    Поля читаются через getattr и являются опциональными.
    """
    id: Optional[str] = None
    raw_block: Optional[str] = None
    raw_command: Optional[str] = None
    annotation: Optional[str] = None
    shape_type: Optional[str] = None

class EllipseProcessor(BaseShapeProcessor):
    def __init__(self, shape_instance: Optional[ShapePayload] = None) -> None:
        super().__init__(shape_instance, parser=EllipseParser(), renderer=EllipseRenderer())
        self.default_type = 'Ellipse'

    def _points_from_main(self, main_command: str) -> List[Point]:
        raw_points = parse_points_from_draw(main_command)
        deduped: List[Point] = []
        for point in raw_points:
            if not deduped:
                deduped.append(point)
                continue

            if all(math.hypot(point[0] - existing[0], point[1] - existing[1]) > 1e-6 for existing in deduped):
                deduped.append(point)

        return deduped

    def _validate_fit_output(
        self,
        fit_result: Dict[str, Any],
    ) -> Optional[Tuple[Point, float, float, float, bool]]:
        center_raw = fit_result.get('center')
        if not isinstance(center_raw, (list, tuple)) or len(center_raw) < 2:
            return None

        try:
            center = (float(center_raw[0]), float(center_raw[1]))
        except (TypeError, ValueError):
            return None

        try:
            major = float(fit_result.get('major_axis'))
            minor = float(fit_result.get('minor_axis'))
        except (TypeError, ValueError):
            return None

        if not all(math.isfinite(value) for value in (center[0], center[1], major, minor)):
            return None

        if major <= 0 or minor <= 0:
            return None

        rotation_raw = fit_result.get('rotation', 0.0)
        try:
            rotation = float(rotation_raw)
        except (TypeError, ValueError):
            rotation = 0.0

        if major < minor:
            major, minor = minor, major
            rotation = (rotation + 90.0) % 360

        ellipse_type = str(fit_result.get('type', 'ellipse')).lower()
        is_circle = ellipse_type == 'circle' or abs(major - minor) < 1e-6

        return center, major, minor, rotation, is_circle

    def process_arrows(self, main: str, arrow_cmds: List[str]) -> Dict[str, Any]:
        return {}

    def build_render_payload(self, main: str, styles: Dict[str, Any], extras: Dict[str, Any]) -> Dict[str, Any]:
        points = self._points_from_main(main)
        if len(points) < 4:
            logger.debug("Not enough points for ellipse fitting; returning raw block")
            return {'raw': extras.get('_raw_block', '')}

        try:
            fit_result = fit_ellipse(str(points))
        except Exception as exc:  # pragma: no cover
            logger.exception("Conic fitting failed")
            raise ProcessingError("Failed to fit ellipse") from exc

        if isinstance(fit_result, str):
            logger.debug("Ellipse fitting returned error: %s", fit_result)
            return {'raw': extras.get('_raw_block', '')}

        validated = self._validate_fit_output(fit_result)
        if not validated:
            logger.debug("Invalid fit result; returning raw block: %s", fit_result)
            return {'raw': extras.get('_raw_block', '')}

        center, major, minor, rotation, is_circle = validated

        processed: EllipsePayload = {
            'center': center,
            'major_axis': major,
            'minor_axis': minor,
            'rotation': rotation,
            'is_circle': is_circle,
        }
        if styles:
            processed['styles'] = styles  # type: ignore[assignment]
        return processed

    def post_process(self, payload: Dict[str, Any], extras: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        center = payload.get('center')
        if center is not None:
            result['center'] = center
        for key in ('major_axis', 'minor_axis', 'rotation', 'is_circle', 'id'):
            if key in payload:
                result[key] = payload[key]
        # Shape type telemetry (only if we have fit result)
        if 'is_circle' in payload:
            result['type'] = 'Circle' if payload.get('is_circle') else 'Ellipse'
        return result

