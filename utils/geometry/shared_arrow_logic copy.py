from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Optional, Literal, TypedDict
import logging
import re

# For now, reuse top-level geometry helpers until full namespacing is complete
from utils.geometry.point_path_operations import project_point_on_segment  # noqa: F401
from utils.geometry.base_geometry import distance  # noqa: F401

logger = logging.getLogger('mathcha2tikz.utils.geometry.shared_arrow_logic')

Point = Tuple[float, float]
Vector = Tuple[float, float]

ArrowDirection = Literal['<', '>']


class BoundaryArrows(TypedDict, total=False):
    start_arrow: Optional[ArrowDirection]
    end_arrow: Optional[ArrowDirection]


DRAW_STYLE_PATTERN = re.compile(r"\\draw\s*(\[[^\]]+\])?")
POINT_PATTERN = re.compile(r"\(([^)]+)\)")
SHIFT_PATTERN = re.compile(r"shift\s*=\s*\{\(([^)]+)\)\}")
ROTATE_PATTERN = re.compile(r"rotate\s*=\s*([\d.-]+)")


@dataclass
class AnchorInfo:
    position: Point
    rotation: float


def parse_points_from_draw(main_command: str) -> List[Point]:
    points: List[Point] = []
    for match in POINT_PATTERN.findall(main_command):
        parts = match.split(',')
        if len(parts) >= 2:
            try:
                points.append((float(parts[0].strip()), float(parts[1].strip())))
            except ValueError:
                logger.debug("Skipping point due to ValueError: %s", match)
                continue
    return points


def extract_style_block(main_command: str) -> str:
    match = DRAW_STYLE_PATTERN.match(main_command)
    return match.group(1) if match and match.group(1) else ''


def extract_arrow_anchor(command: str) -> Optional[AnchorInfo]:
    shift_match = SHIFT_PATTERN.search(command)
    rotate_match = ROTATE_PATTERN.search(command)
    if not shift_match:
        return None
    try:
        sx, sy = [float(v.strip()) for v in shift_match.group(1).split(',')[:2]]
    except Exception:
        logger.debug("Failed to parse shift anchor from command: %s", command, exc_info=True)
        return None
    rotation = float(rotate_match.group(1)) if rotate_match else 0.0
    return AnchorInfo((sx, sy), rotation)
