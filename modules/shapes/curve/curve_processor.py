"""
Curve Processor

Parses curve raw block, processes arrows, and renders final TikZ code.
Pipeline: CurveParser -> CurveArrows -> CurveRenderer
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from core.exceptions import ProcessingError, RenderingError
from core.shape_payload import ShapePayload
from modules.shapes.curve.curve_parser import CurveParser
from modules.shapes.curve.curve_renderer import CurveRenderer
from modules.shapes.curve.curve_arrows import CurveArrows
from utils.processing.base_shape_processor import BaseShapeProcessor
from utils.shapes.types import Point


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

logger = logging.getLogger('modules.shapes.curve_processor')


class CurveProcessor(BaseShapeProcessor):
    def __init__(self, shape_instance: Optional[ShapePayload] = None) -> None:
        super().__init__(shape_instance, parser=CurveParser(), renderer=CurveRenderer())
        self.arrows = CurveArrows()
        self.default_type = 'CurveLine'

    def process_arrows(self, main: str, arrow_cmds: List[str]) -> Dict[str, Any]:
        # Reuse existing arrow logic to produce segments, start/end/mid arrows, etc.
        return self.arrows.process_arrows(main, arrow_cmds)

    def build_render_payload(self, main: str, styles: Dict[str, Any], extras: Dict[str, Any]) -> Dict[str, Any]:
        # 'extras' already contains: style_str, start/end points, segments, is_closed, arrow markers
        payload: Dict[str, Any] = dict(extras)
        if styles:
            payload['styles'] = styles
        return payload

    def post_process(self, payload: Dict[str, Any], extras: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        # Attach metadata similar to previous implementation
        start_pt = extras.get('start_point')
        end_pt = extras.get('end_point')
        if start_pt is not None:
            result['start_point'] = start_pt
        if end_pt is not None:
            result['end_point'] = end_pt
        result['processed_arrows'] = {
            'start_arrow': extras.get('start_arrow'),
            'end_arrow': extras.get('end_arrow'),
            'mid_arrows': extras.get('mid_arrows', []),
        }
        return result

