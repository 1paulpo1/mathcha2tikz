"""Ellipse Processor

Parses ellipse/circle raw block, fits conic, and prepares data for rendering.
Pipeline: EllipseParser -> ConicFitting -> EllipseRenderer
"""

from __future__ import annotations

import logging
import math
from typing import Any, Dict, List, Optional, Tuple, TypedDict, cast
from dataclasses import dataclass

from core.exceptions import ProcessingError, RenderingError
from core.shape_payload import ShapePayload
from modules.shapes.lines.shared_arrow_logic import parse_points_from_draw
from .ellipse_parser import EllipseParser, EllipseStyles
from utils.geometry.conics.conic_fitting import main as fit_ellipse
from .ellipse_renderer import EllipseRenderer


logger = logging.getLogger('modules.shapes.ellipse.ellipse_processor')


Point = Tuple[float, float]


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


class EllipseRenderInput(TypedDict, total=False):
    center: Point
    major_axis: float
    minor_axis: float
    rotation: float
    is_circle: bool
    styles: EllipseStyles
    id: str


class EllipseProcessResult(TypedDict, total=False):
    tikz_code: str
    center: Point
    major_axis: float
    minor_axis: float
    rotation: float
    is_circle: bool
    id: str


class EllipseProcessor:
    def __init__(self, shape_instance: Optional[ShapePayload] = None) -> None:
        self.shape_instance = shape_instance
        self.parser = EllipseParser()
        self.renderer = EllipseRenderer()

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

    def process(self, raw_block: Optional[str] = None) -> EllipseProcessResult:
        """Process a raw block of ellipse/circle code."""
        if self.shape_instance and not raw_block:
            raw_block = getattr(self.shape_instance, 'raw_block', '')

        if not raw_block:
            return cast(EllipseProcessResult, {'tikz_code': raw_block or ''})

        try:
            main_command, _extra_commands, styles_dict = self.parser.parse_shape(raw_block)
        except Exception as exc:  # pragma: no cover - unexpected parser errors
            logger.exception("Failed to parse ellipse block")
            raise ProcessingError("Failed to parse ellipse block") from exc

        if not main_command:
            logger.debug("No main ellipse command found; returning raw block")
            return cast(EllipseProcessResult, {'tikz_code': raw_block})

        points = self._points_from_main(main_command)
        if len(points) < 4:
            logger.debug("Not enough points for ellipse fitting; returning raw block")
            return cast(EllipseProcessResult, {'tikz_code': raw_block})

        try:
            fit_result = fit_ellipse(str(points))
        except Exception as exc:  # pragma: no cover
            logger.exception("Conic fitting failed")
            raise ProcessingError("Failed to fit ellipse") from exc

        if isinstance(fit_result, str):
            logger.debug("Ellipse fitting returned error: %s", fit_result)
            return cast(EllipseProcessResult, {'tikz_code': raw_block})

        validated = self._validate_fit_output(fit_result)
        if not validated:
            logger.debug("Invalid fit result; returning raw block: %s", fit_result)
            return cast(EllipseProcessResult, {'tikz_code': raw_block})

        center, major, minor, rotation, is_circle = validated

        processed: EllipseRenderInput = {
            'center': center,
            'major_axis': major,
            'minor_axis': minor,
            'rotation': rotation,
            'is_circle': is_circle,
        }

        if styles_dict:
            processed['styles'] = styles_dict

        if self.shape_instance is not None:
            shape_id = getattr(self.shape_instance, 'id', None)
            if shape_id:
                processed['id'] = shape_id

        try:
            rendered = cast(EllipseProcessResult, self.renderer.render(processed))
        except Exception as exc:  # pragma: no cover
            logger.exception("Failed to render ellipse")
            raise RenderingError("Failed to render ellipse") from exc

        result: EllipseProcessResult = dict(rendered)
        result['center'] = center
        result['major_axis'] = major
        result['minor_axis'] = minor
        result['rotation'] = rotation
        result['is_circle'] = processed['is_circle']
        if 'id' in processed:
            result['id'] = processed['id']

        return result

    def validate(self) -> bool:
        return True

