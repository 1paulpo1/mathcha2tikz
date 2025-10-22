"""Straight Processor

Processes straight line shapes in the modular pipeline:
Parser → Processor → Style → Arrow → Renderer
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from core.exceptions import ProcessingError, RenderingError
from core.shape_payload import ShapePayload

from modules.shapes.straight.straight_parser import StraightParser
from modules.shapes.straight.straight_arrows import (
    StraightArrows,
)
from modules.shapes.straight.straight_renderer import StraightRenderer
from utils.processing.base_shape_processor import BaseShapeProcessor


@dataclass
class StraightInput:
    """Локальное описание входного payload для `StraightProcessor`.

    Поля читаются через getattr и являются опциональными.
    """
    id: Optional[str] = None
    raw_block: Optional[str] = None
    raw_command: Optional[str] = None
    annotation: Optional[str] = None
    shape_type: Optional[str] = None


 


def _prepend_id_comment(tikz_code: str, shape_id: str) -> str:
    """Ensure the TikZ code starts with the straight-line ID comment."""
    if not tikz_code:
        return tikz_code

    stripped = tikz_code.lstrip()
    if stripped.startswith('%Straight Lines [id:'):
        return tikz_code

    # Remove leading blank lines before adding the header to keep output compact.
    body = stripped.lstrip('\n')
    return f"%Straight Lines [id:{shape_id}]\n{body}"


class StraightProcessor(BaseShapeProcessor):
    def __init__(self, shape_instance: Optional[ShapePayload] = None) -> None:
        super().__init__(shape_instance, parser=StraightParser(), renderer=StraightRenderer())
        self.arrows = StraightArrows()
        self.default_type = 'StraightLine'

    def process_arrows(self, main: str, arrow_cmds: List[str]) -> Dict[str, Any]:
        return self.arrows.process_arrows(main, arrow_cmds)

    def build_render_payload(self, main: str, styles: Dict[str, Any], extras: Dict[str, Any]) -> Dict[str, Any]:
        payload: Dict[str, Any] = dict(extras)
        if styles:
            payload['styles'] = styles
        return payload

    def post_process(self, payload: Dict[str, Any], extras: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        # Add start/end points
        if 'start_point' in extras:
            result['start_point'] = extras['start_point']
        if 'end_point' in extras:
            result['end_point'] = extras['end_point']

        # Add ID to the result if available
        shape_id = None
        if self.shape_instance is not None:
            shape_id = getattr(self.shape_instance, 'id', None)
            if shape_id:
                result['id'] = shape_id

        # Ensure ID header is present (renderer already adds; this is a safe no-op if present)
        tikz_code = result.get('tikz_code')
        if shape_id and tikz_code:
            result['tikz_code'] = _prepend_id_comment(tikz_code, shape_id)

        # Attach processed arrows metadata
        result['processed_arrows'] = {
            'start_arrow': extras.get('start_arrow'),
            'end_arrow': extras.get('end_arrow'),
            'mid_arrows': extras.get('mid_arrows', []),
        }
        return result
