from __future__ import annotations

import logging
from typing import Dict, Optional, Sequence, TypedDict

from utils.geometry.point_path_operations import (
    get_tangent_at_point,
    determine_arrow_type as determine_arrow_type_utils,
)
from modules.shapes.lines.shared_arrow_logic import Point, ArrowDirection


logger = logging.getLogger('modules.shapes.arc.arc_arrows')


Segments = Sequence[Sequence[Point]]


class ArrowEndpoint(TypedDict, total=False):
    rotation: float


class ArcArrowInfo(TypedDict, total=False):
    start: Optional[ArrowEndpoint]
    end: Optional[ArrowEndpoint]


class ArcArrowData(TypedDict):
    segments: Segments
    arrow_info: ArcArrowInfo


class ArcArrowResult(TypedDict, total=False):
    start: Optional[ArrowDirection]
    end: Optional[ArrowDirection]


def _compute_endpoint_arrow(
    segments: Segments,
    index: int,
    rotation: float,
    is_end_arrow: bool,
) -> Optional[ArrowDirection]:
    try:
        segment = segments[index]
    except IndexError:
        logger.debug("Arc arrow computation: segment index %d out of range", index)
        return None

    t = 1.0 if is_end_arrow else 0.0
    tangent = get_tangent_at_point(segment, t)
    if tangent == (0.0, 0.0):
        logger.debug("Arc arrow computation: zero tangent at index %d (t=%s)", index, t)
        return None

    return determine_arrow_type_utils(tangent, rotation or 0.0, is_end_arrow=is_end_arrow)  # type: ignore[return-value]


def process_arc_arrows(data: ArcArrowData) -> ArcArrowResult:
    segments = data.get('segments')
    arrow_info = data.get('arrow_info', {})

    result: ArcArrowResult = {'start': None, 'end': None}

    if not segments:
        logger.debug("Arc arrow processing: no segments supplied")
        return result

    if arrow_info.get('start'):
        rotation = arrow_info['start'].get('rotation', 0.0)
        result['start'] = _compute_endpoint_arrow(segments, 0, rotation, is_end_arrow=False)

    if arrow_info.get('end'):
        rotation = arrow_info['end'].get('rotation', 0.0)
        result['end'] = _compute_endpoint_arrow(segments, -1, rotation, is_end_arrow=True)

    return result