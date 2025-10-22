from __future__ import annotations

from typing import Any, Dict, List, Optional
import re

from utils.shapes.types import Point
from utils.nodes.types import Anchor
from utils.geometry.base_geometry import distance


def _is_point(p: Any) -> bool:
    try:
        return (
            isinstance(p, (list, tuple))
            and len(p) >= 2
            and isinstance(p[0], (int, float))
            and isinstance(p[1], (int, float))
        )
    except Exception:
        return False


def _add_anchor(
    anchors: List[Anchor],
    point: Point,
    render_index: int,
    kind: str,
    shape_type: str,
    shape_id: Optional[str],
) -> None:
    anchors.append(
        Anchor(
            point=(float(point[0]), float(point[1])),
            render_index=int(render_index),
            kind=str(kind),
            shape_type=str(shape_type),
            shape_id=str(shape_id) if shape_id is not None else None,
        )
    )


def collect_anchors(processed_shapes: List[Dict[str, Any]]) -> List[Anchor]:
    """Collect anchor points P from processed shape payloads.

    Expected shape fields:
      - 'start_point': tuple[float,float]
      - 'end_point': tuple[float,float]
      - 'center': tuple[float,float]
    Other fields are ignored for now.
    """
    anchors: List[Anchor] = []

    for idx, item in enumerate(processed_shapes or []):
        if not isinstance(item, dict):
            # Non-dict shapes are not considered for anchors in this pass
            continue

        s_type = str(item.get('type') or item.get('normalized_type') or 'unknown')
        s_id: Optional[str] = item.get('id') if isinstance(item.get('id'), str) else None

        if 'start_point' in item and _is_point(item['start_point']):
            _add_anchor(anchors, item['start_point'], idx, 'start', s_type, s_id)
        if 'end_point' in item and _is_point(item['end_point']):
            _add_anchor(anchors, item['end_point'], idx, 'end', s_type, s_id)
        if 'center' in item and _is_point(item['center']):
            _add_anchor(anchors, item['center'], idx, 'center', s_type, s_id)

    return anchors


def anchors_to_points(anchors: List[Anchor]) -> List[Point]:
    return [a['point'] for a in anchors]


# --- Post-conversion anchors collection ---

COORD_RE = re.compile(
    r"\(\s*\{?\s*([-+]?\d+(?:\.\d+)?)\s*\}?\s*,\s*\{?\s*([-+]?\d+(?:\.\d+)?)\s*\}?\s*\)"
)


def _is_close(p: Point, q: Point, eps: float = 1e-6) -> bool:
    return distance(p, q) <= eps


def collect_anchors_from_tikz_parts(
    tikz_parts: List[str],
    nodes: List[Dict[str, Any]] | None = None,
    start_index: int = 0,
) -> List[Anchor]:
    """Collect anchors P by scanning final TikZ lines for (x, y) coordinates.

    - Excludes any coordinates that coincide with node 'at' points within epsilon.
    - Uses the line's index in tikz_parts as 'render_index' for insertion.
    """
    nodes = nodes or []
    node_points: List[Point] = []
    for n in nodes:
        at = n.get('at')
        if _is_point(at):
            node_points.append((float(at[0]), float(at[1])))

    anchors: List[Anchor] = []
    for idx in range(max(0, start_index), len(tikz_parts)):
        line = tikz_parts[idx] or ''
        for m in COORD_RE.finditer(line):
            px = float(m.group(1))
            py = float(m.group(2))
            p: Point = (px, py)
            # Skip if matches any node point
            if any(_is_close(p, np) for np in node_points):
                continue
            anchors.append(
                Anchor(
                    point=p,
                    render_index=idx,
                    kind='other',
                    shape_type='unknown',
                    shape_id=None,
                )
            )
    return anchors
