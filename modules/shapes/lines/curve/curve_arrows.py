from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, TypedDict
import logging
import math

from utils.geometry.bezier_analysis import (
    bezier_point_at_t,
    bezier_derivative,
    bezier_length,
    nearest_segment_midpoint,
)
from utils.geometry.point_path_operations import (
    split_bezier_into_segments,
    determine_arrow_type,
)
from utils.geometry.shared_arrow_logic import (
    extract_arrow_anchor,
    extract_style_block,
    parse_points_from_draw,
    Point,
)
from utils.geometry.base_geometry import distance



logger = logging.getLogger('modules.shapes.lines.curve_arrows')

START_END_DISTANCE_THRESHOLD = 10.0
LENGTH_EPSILON = 1e-9


class MidArrow(TypedDict):
    position: float
    direction: str


class CurveArrowInfo(TypedDict, total=False):
    start_arrow: Optional[str]
    end_arrow: Optional[str]
    mid_arrows: List[MidArrow]
    style_str: str
    start_point: Point
    end_point: Point
    segments: List[List[Point]]
    is_closed: bool


class CurveArrows:
    """Arrow processing for Curve Lines.

    Produces an arrows_info dict compatible with StraightArrows, plus
    curve-specific fields (segments, is_closed).
    """

    def _parse_points_from_main(self, main_command: str) -> List[Point]:
        return parse_points_from_draw(main_command)

    def _extract_style_str(self, main_command: str) -> str:
        return extract_style_block(main_command)

    def _extract_arrow_anchor(self, cmd: str) -> Tuple[Optional[Point], Optional[float]]:
        anchor_info = extract_arrow_anchor(cmd)
        if anchor_info is None:
            return None, None
        return anchor_info.position, anchor_info.rotation

    def _total_curve_length(self, segments: List[List[Point]]) -> float:
        return sum(bezier_length(seg) for seg in segments if len(seg) == 4)

    def _nearest_segment_mid(self, segments: List[List[Point]], point: Point) -> Tuple[Optional[int], float, float]:
        return nearest_segment_midpoint(segments, point)

    def process_arrows(self, main_command: str, arrow_commands: List[str]) -> CurveArrowInfo:
        # Extract style and points
        style_str = self._extract_style_str(main_command)
        points = self._parse_points_from_main(main_command)
        segments = split_bezier_into_segments(points)
        is_closed = main_command.strip().endswith('-- cycle')

        if not segments:
            logger.debug("No segments extracted from main command: %s", main_command)
            return CurveArrowInfo()

        start_pt = segments[0][0]
        end_pt = segments[-1][-1]

        arrows_info: CurveArrowInfo = {
            'start_arrow': None,
            'end_arrow': None,
            'mid_arrows': [],  # list of {position, direction}
            'style_str': style_str,
            'start_point': start_pt,
            'end_point': end_pt,
            'segments': segments,
            'is_closed': is_closed,
        }

        total_len = self._total_curve_length(segments)
        if total_len <= LENGTH_EPSILON:
            logger.debug("Total curve length below epsilon (%.3e).", total_len)
            return arrows_info

        # Precompute segment lengths and cumulative lengths
        seg_lengths = [bezier_length(seg) for seg in segments]
        cum_lengths = [0.0]
        for L in seg_lengths:
            cum_lengths.append(cum_lengths[-1] + L)

        def global_t(seg_idx: int, t_local: float) -> float:
            s = cum_lengths[seg_idx]
            return (s + t_local * seg_lengths[seg_idx]) / total_len if seg_lengths[seg_idx] > 0 else s / total_len

        for cmd in arrow_commands:
            anchor, rotation = self._extract_arrow_anchor(cmd)
            if anchor is None:
                continue
            ax, ay = anchor

            dist_start = distance(anchor, start_pt)
            dist_end = distance(anchor, end_pt)

            # Thresholds similar to straight logic
            if dist_start < START_END_DISTANCE_THRESHOLD:
                tangent = bezier_derivative(0.0, segments[0])
                direction = determine_arrow_type(tangent, rotation or 0.0, is_end_arrow=False)
                arrows_info['start_arrow'] = direction
                continue
            if dist_end < START_END_DISTANCE_THRESHOLD:
                tangent = bezier_derivative(1.0, segments[-1])
                direction = determine_arrow_type(tangent, rotation or 0.0, is_end_arrow=True)
                arrows_info['end_arrow'] = direction
                continue

            # Mid arrow: choose nearest segment mid
            idx, _, t_local = self._nearest_segment_mid(segments, (ax, ay))
            if idx is None:
                logger.debug("Could not find suitable segment for mid-arrow anchor: %s", anchor)
                continue
            t_glob = global_t(idx, t_local)
            tangent = bezier_derivative(t_local, segments[idx])
            direction = determine_arrow_type(tangent, rotation or 0.0, is_end_arrow=True)
            arrows_info['mid_arrows'].append({'position': t_glob, 'direction': direction})

        arrows_info['mid_arrows'].sort(key=lambda x: x['position'])
        return arrows_info

