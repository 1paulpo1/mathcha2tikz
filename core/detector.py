from __future__ import annotations

from typing import Dict, Any, List, Optional
import logging
import re
from types import SimpleNamespace

from core.parser import ShapeBlock


logger = logging.getLogger(__name__)


_CANONICAL_ALIASES: Dict[str, List[str]] = {
    # Important: canonical keys must match names registered in Processor/Renderer registries
    'StraightLine': [
        'straight lines', 'straight line', 'straight_lines', 'straight_line', 'straightline', 'line', 'lines'
    ],
    'CurveLine': [
        'curve lines', 'curve line', 'curve_lines', 'curve_line', 'curveline', 'curve'
    ],
    'Arc': ['arc', 'elliptical arc'],
    'Ellipse': ['ellipse', 'ellipseshape'],
    'Circle': ['circle'],
    'Text Node': ['text node', 'text', 'node'],
}


def _normalize(value: str) -> str:
    return re.sub(r"[\s\-]+", "_", value.strip().lower()) if value else ""


_ALIAS_LOOKUP: Dict[str, str] = {}
for canonical, aliases in _CANONICAL_ALIASES.items():
    _ALIAS_LOOKUP[_normalize(canonical)] = canonical
    for alias in aliases:
        _ALIAS_LOOKUP[_normalize(alias)] = canonical


class Detector:
    """Simple detector that normalizes parser output into canonical shape records."""

    def __init__(self, shape_block: Optional[ShapeBlock] = None) -> None:
        self.shape_block = shape_block

    def detect(self, shape_block: Optional[ShapeBlock] = None) -> List[SimpleNamespace]:
        block = shape_block or self.shape_block
        if block is None:
            return []

        canonical_type = self._resolve_shape_type(block)
        payload: Dict[str, Any] = {
            'id': block.shape_id,
            'shape_type': canonical_type,
            'raw_block': block.raw_block,
            'annotation': block.annotation,
        }
        if block.raw_shape_data:
            payload['raw_shape_data'] = block.raw_shape_data
        if block.raw_arrows_data:
            payload['raw_arrows_data'] = block.raw_arrows_data

        return [SimpleNamespace(**payload)]

    def _resolve_shape_type(self, shape_block: ShapeBlock) -> str:
        candidates: List[str] = []

        if getattr(shape_block, 'shape_type', None):
            candidates.append(shape_block.shape_type)

        annotation_line = shape_block.annotation or ''
        if annotation_line:
            cleaned = annotation_line.lstrip('%').strip()
            if cleaned:
                before_id = cleaned.split('[', 1)[0].strip()
                if before_id:
                    candidates.append(before_id)
                if ':' in before_id:
                    after_colon = before_id.split(':', 1)[1].strip()
                    if after_colon:
                        candidates.append(after_colon)

            match = re.search(r'%\s*(?:Shape:)?\s*([^\[\n]+)', annotation_line, re.IGNORECASE)
            if match:
                candidates.append(match.group(1))

        for candidate in candidates:
            normalized = _normalize(candidate)
            if normalized:
                resolved = _ALIAS_LOOKUP.get(normalized)
                if resolved:
                    logger.debug("Resolved shape type '%s' -> '%s'", candidate, resolved)
                    return resolved

        logger.debug("Defaulting shape type to 'unknown' for annotation: %s", annotation_line)
        return 'unknown'


# Backwards-compatible alias
ShapeDetector = Detector