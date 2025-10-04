"""
Curve Processor

Parses curve raw block, processes arrows, and renders final TikZ code.
Pipeline: CurveParser -> CurveArrows -> CurveRenderer
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, TypedDict, cast
from dataclasses import dataclass

from core.exceptions import ProcessingError, RenderingError
from core.shape_payload import ShapePayload
from modules.shapes.lines.curve.curve_parser import CurveParser, CurveStyles
from modules.shapes.lines.curve.curve_renderer import CurveRenderer
from modules.shapes.lines.curve.curve_arrows import CurveArrows


Point = Tuple[float, float]


@dataclass
class CurveInput:
    """Локальное описание входного payload для `CurveProcessor`.

    Поля читаются через getattr и являются опциональными.
    """
    id: Optional[str] = None
    raw_block: Optional[str] = None
    raw_command: Optional[str] = None
    annotation: Optional[str] = None
    shape_type: Optional[str] = None


class MidArrow(TypedDict):
    position: float
    direction: str


logger = logging.getLogger('modules.shapes.lines.curve_processor')


class ArrowInfo(TypedDict, total=False):
    start_arrow: Optional[str]
    end_arrow: Optional[str]
    mid_arrows: List[MidArrow]
    style_str: str
    styles: CurveStyles
    start_point: Point
    end_point: Point
    segments: List[List[Point]]
    is_closed: bool
    id: str


class ProcessedArrows(TypedDict):
    start_arrow: Optional[str]
    end_arrow: Optional[str]
    mid_arrows: List[MidArrow]


class ProcessedCurve(TypedDict, total=False):
    tikz_code: str
    start_point: Point
    end_point: Point
    id: str
    processed_arrows: ProcessedArrows


class CurveProcessor:
    def __init__(self, shape_instance: Optional[ShapePayload] = None) -> None:
        self.shape_instance = shape_instance
        self.parser = CurveParser()
        self.arrows = CurveArrows()
        self.renderer = CurveRenderer()

    def process(self, raw_block: Optional[str] = None) -> ProcessedCurve:
        """
        Process a raw block of curve code (colors handled post-render by ColorPostProcessor).

        Args:
            raw_block: The raw TikZ code block to process

        Returns:
            Dictionary containing the processed TikZ code and metadata
        """
        if self.shape_instance and not raw_block:
            raw_block = getattr(self.shape_instance, 'raw_block', '')

        if not raw_block:
            return cast(ProcessedCurve, {'tikz_code': raw_block or ''})

        # Parse main command, arrow commands, and styles
        try:
            main_command, arrow_commands, styles_dict = self.parser.parse_shape(raw_block)
        except Exception as exc:  # pragma: no cover - unexpected parser errors
            logger.exception("Failed to parse curve block")
            raise ProcessingError("Failed to parse curve block") from exc
        if not main_command:
            logger.debug("No main curve command found; returning raw block")
            return cast(ProcessedCurve, {'tikz_code': raw_block})

        # Process arrows and collect curve specifics
        try:
            arrows_info_raw = self.arrows.process_arrows(main_command, arrow_commands)
        except Exception as exc:  # pragma: no cover
            logger.exception("Failed to process curve arrows")
            raise ProcessingError("Failed to process curve arrows") from exc
        arrows_info: ArrowInfo = cast(ArrowInfo, arrows_info_raw)

        if styles_dict:
            arrows_info['styles'] = styles_dict

        # Attach ID from shape_instance if available
        shape_id = None
        if self.shape_instance is not None:
            shape_id = getattr(self.shape_instance, 'id', None)
        if shape_id:
            arrows_info['id'] = shape_id

        # Render final TikZ
        try:
            result = cast(ProcessedCurve, self.renderer.render(arrows_info))
        except Exception as exc:  # pragma: no cover
            logger.exception("Failed to render curve")
            raise RenderingError("Failed to render curve") from exc

        # Provide metadata similar to StraightProcessor
        if 'start_point' in arrows_info:
            result['start_point'] = arrows_info['start_point']
        if 'end_point' in arrows_info:
            result['end_point'] = arrows_info['end_point']
        if shape_id:
            result['id'] = shape_id
        result['processed_arrows'] = ProcessedArrows(
            start_arrow=arrows_info.get('start_arrow'),
            end_arrow=arrows_info.get('end_arrow'),
            mid_arrows=arrows_info.get('mid_arrows', []),
        )

        return result

    def validate(self) -> bool:
        return True

