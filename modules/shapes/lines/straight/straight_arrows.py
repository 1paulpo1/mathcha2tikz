from typing import Dict, Any, List, Optional, TypedDict
import math

from utils.geometry.point_path_operations import determine_arrow_type, project_point_on_segment
from utils.geometry.base_geometry import distance
from utils.geometry.shared_arrow_logic import (
    extract_arrow_anchor,
    extract_style_block,
    parse_points_from_draw,
    ArrowDirection,
    Point,
)


ANCHOR_DISTANCE_THRESHOLD = 10.0
ANCHOR_START_EPSILON = 0.05
ANCHOR_END_EPSILON = 0.95


class StraightMidArrow(TypedDict):
    position: float
    direction: ArrowDirection


class StraightArrowInfo(TypedDict, total=False):
    start_arrow: Optional[ArrowDirection]
    end_arrow: Optional[ArrowDirection]
    mid_arrows: List[StraightMidArrow]
    style_str: str
    start_point: Point
    end_point: Point


class StraightArrows:
    def __init__(self):
        pass

    def process_arrows(self, main_command: str, arrow_commands: List[str]) -> StraightArrowInfo:
        main = main_command.rstrip(';').strip()
        style_str = extract_style_block(main) or None
        points = parse_points_from_draw(main)

        if len(points) < 2:
            return {}

        start_pt = points[0]
        end_pt = points[-1]
        path_vec = (end_pt[0] - start_pt[0], end_pt[1] - start_pt[1])
        path_len = math.hypot(path_vec[0], path_vec[1])

        if path_len <= 1e-9:
            return {}

        arrows_info: StraightArrowInfo = {
            'start_arrow': None,
            'end_arrow': None,
            'mid_arrows': [],
            'start_point': start_pt,
            'end_point': end_pt,
        }

        if style_str:
            arrows_info['style_str'] = style_str

        for cmd in arrow_commands:
            anchor_info = extract_arrow_anchor(cmd)
            if anchor_info is None:
                continue
            ax, ay = anchor_info.position

            dist_start = distance((ax, ay), start_pt)
            dist_end = distance((ax, ay), end_pt)

            t = project_point_on_segment((ax, ay), start_pt, end_pt)

            tangent = path_vec  # constant along straight line
            rotation = anchor_info.rotation or 0.0

            if dist_start < ANCHOR_DISTANCE_THRESHOLD or t <= ANCHOR_START_EPSILON:
                direction = determine_arrow_type(tangent, rotation, is_end_arrow=False)
                arrows_info['start_arrow'] = direction
                continue

            if dist_end < ANCHOR_DISTANCE_THRESHOLD or t >= ANCHOR_END_EPSILON:
                direction = determine_arrow_type(tangent, rotation, is_end_arrow=True)
                arrows_info['end_arrow'] = direction
                continue

            direction = determine_arrow_type(tangent, rotation, is_end_arrow=True)
            arrows_info['mid_arrows'].append({'position': t, 'direction': direction})

        arrows_info['mid_arrows'].sort(key=lambda x: x['position'])
        return arrows_info