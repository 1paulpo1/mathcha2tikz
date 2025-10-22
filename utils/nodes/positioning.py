from __future__ import annotations

import math
from typing import Tuple


def vector_angle_deg(dx: float, dy: float) -> float:
    """Return angle in degrees in [0, 360) where 0 is +X (right), 90 is +Y (up)."""
    return math.degrees(math.atan2(dy, dx)) % 360.0


# 8-way sectors with mid-angle thresholds (22.5° offsets)
SECTOR_EDGES = [22.5, 67.5, 112.5, 157.5, 202.5, 247.5, 292.5, 337.5]
SECTOR_LABELS = [
    'right',
    'above right',
    'above',
    'above left',
    'left',
    'below left',
    'below',
    'below right',
]

def angle_to_position(angle_deg: float) -> str:
    """Map an angle in degrees to a TikZ node position keyword."""
    a = angle_deg % 360.0
    if a < SECTOR_EDGES[0] or a >= SECTOR_EDGES[-1]:
        return SECTOR_LABELS[0]
    for i, edge in enumerate(SECTOR_EDGES):
        if a < edge:
            return SECTOR_LABELS[i]
    return SECTOR_LABELS[-1]
