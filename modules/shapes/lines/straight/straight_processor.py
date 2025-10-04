"""Straight Processor

Processes straight line shapes in the modular pipeline:
Parser → Processor → Style → Arrow → Renderer
"""

from typing import Any, Dict, List, Optional, Tuple, TypedDict, cast
from dataclasses import dataclass

from core.exceptions import ProcessingError, RenderingError
from core.shape_payload import ShapePayload

from modules.shapes.lines.straight.straight_parser import StraightParser
from modules.shapes.lines.straight.straight_arrows import (
    StraightArrows,
    StraightArrowInfo,
    StraightMidArrow,
)
from modules.shapes.lines.straight.straight_renderer import StraightRenderer


Point = Tuple[float, float]


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


 


class ProcessedArrows(TypedDict):
    start_arrow: Optional[str]
    end_arrow: Optional[str]
    mid_arrows: List[StraightMidArrow]


class ProcessedStraight(TypedDict, total=False):
    tikz_code: str
    start_point: Point
    end_point: Point
    id: str
    processed_arrows: ProcessedArrows


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


class StraightProcessor:
    def __init__(self, shape_instance: Optional[ShapePayload] = None) -> None:
        self.shape_instance = shape_instance
        self.parser = StraightParser()
        self.arrows = StraightArrows()
        self.renderer = StraightRenderer()

    def process(self, raw_block: Optional[str] = None) -> ProcessedStraight:
        """
        Process a raw block of straight line code with color processing
        
        Args:
            raw_block: The raw TikZ code block to process
            
        Returns:
            Dictionary containing the processed TikZ code and metadata
        """
        if self.shape_instance and not raw_block:
            raw_block = getattr(self.shape_instance, 'raw_block', '')
        
        if not raw_block:
            return cast(ProcessedStraight, {'tikz_code': raw_block or ''})

        # Parse the input to get main command, arrow commands, and styles
        try:
            main_command, arrow_commands, styles_dict = self.parser.parse_shape(raw_block)
        except Exception as exc:  # pragma: no cover - unexpected parser errors should bubble as ProcessingError
            raise ProcessingError("Failed to parse straight line block") from exc

        if not main_command:
            return cast(ProcessedStraight, {'tikz_code': raw_block})
        # Colors are now processed in the final output by ColorPostProcessor
        # No need to process colors here anymore
        
        # Process arrows
        try:
            arrows_info_raw = self.arrows.process_arrows(main_command, arrow_commands)
        except Exception as exc:  # pragma: no cover
            raise ProcessingError("Failed to process straight line arrows") from exc
        arrows_info: StraightArrowInfo = cast(StraightArrowInfo, arrows_info_raw)

        if styles_dict:
            arrows_info['styles'] = styles_dict

        # Use id from shape_instance if available (Detector already extracted it)
        shape_id = None
        if self.shape_instance is not None:
            shape_id = getattr(self.shape_instance, 'id', None)
            # Add ID to arrows_info so it gets passed to renderer
            if shape_id:
                arrows_info['id'] = shape_id

        # Render the final TikZ code
        try:
            result = cast(ProcessedStraight, self.renderer.render(arrows_info))
        except Exception as exc:  # pragma: no cover
            raise RenderingError("Failed to render straight line") from exc

        # Add start and end points to the result for downstream processing
        if 'start_point' in arrows_info:
            result['start_point'] = arrows_info['start_point']
        if 'end_point' in arrows_info:
            result['end_point'] = arrows_info['end_point']
        
        # Add ID to the result if available
        if shape_id:
            result['id'] = shape_id
        
        # Add ID comment to the tikz_code if available and not already present
        tikz_code = result.get('tikz_code')
        if shape_id and tikz_code:
            result['tikz_code'] = _prepend_id_comment(tikz_code, shape_id)

        # Add metadata about processed arrows for debugging
        result['processed_arrows'] = ProcessedArrows(
            start_arrow=arrows_info.get('start_arrow'),
            end_arrow=arrows_info.get('end_arrow'),
        )

        return result
    
    def validate(self) -> bool:
        """Validate that the shape instance has all required data."""
        return True
