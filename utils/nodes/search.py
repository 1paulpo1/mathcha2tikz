from __future__ import annotations

from typing import List, Tuple

from utils.shapes.types import Point
from utils.geometry.base_geometry import distance


def nearest_point(points: List[Point], q: Point) -> Tuple[int, float]:
    """Return (index, distance) of the closest point to q via brute force using geometry.distance."""
    if not points:
        return -1, float('inf')
    best_idx = 0
    best_d = distance(points[0], q)
    for i in range(1, len(points)):
        d = distance(points[i], q)
        if d < best_d:
            best_d = d
            best_idx = i
    return best_idx, best_d


def nearest_many(points: List[Point], queries: List[Point]) -> List[Tuple[int, float]]:
    return [nearest_point(points, q) for q in queries]
