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

    - Skips arrowhead helper lines with 'shift={...}' to avoid non-structural points.
    - Excludes any coordinates that coincide with node 'at' points within epsilon.
    - Classifies line type to prefer anchors from 'circle' (dots) over 'path' over 'unknown'.
    - Deduplicates anchors by coordinate with preference order: circle > path > unknown.
    - Uses the line's index in tikz_parts as 'render_index' for insertion.
    """
    nodes = nodes or []
    node_points: List[Point] = []
    for n in nodes:
        at = n.get('at')
        if _is_point(at):
            node_points.append((float(at[0]), float(at[1])))

    def classify_line(s: str) -> str:
        st = s or ''
        if ' circle ' in st or st.strip().startswith('\\draw') and ' circle ' in st:
            return 'circle'
        if '--' in st or ' to ' in st:
            return 'path'
        return 'unknown'

    def type_score(t: str) -> int:
        return {'circle': 3, 'path': 2, 'unknown': 0}.get(t, 0)

    best_by_point: dict[tuple[float, float], Anchor] = {}

    for idx in range(max(0, start_index), len(tikz_parts)):
        line = tikz_parts[idx] or ''
        # Skip arrowhead/auxiliary lines
        if 'shift={' in line:
            continue
        ltype = classify_line(line)
        # Compute style weight once per line
        w = 0
        sline = line.replace(' ', '')
        if 'color=' in sline:
            w += 1
        if 'dashpattern' in sline or 'dashed' in sline:
            w += 1
        # line width
        m_lw = re.search(r"line\s*width\s*=\s*([0-9]+(?:\.[0-9]+)?)", line)
        if m_lw:
            try:
                lw = float(m_lw.group(1))
                if lw >= 1.0:
                    w += 1
            except Exception:
                pass
        for m in COORD_RE.finditer(line):
            px = float(m.group(1))
            py = float(m.group(2))
            p: Point = (px, py)
            # Skip if matches any node point
            if any(_is_close(p, np) for np in node_points):
                continue
            key = (round(px, 6), round(py, 6))
            cand = Anchor(
                point=p,
                render_index=idx,
                kind='other',
                shape_type=ltype,
                shape_id=None,
                style_weight=w,
            )
            if key not in best_by_point:
                best_by_point[key] = cand
            else:
                # Prefer higher type score; on tie, keep existing
                cur = best_by_point[key]
                if type_score(cand.get('shape_type', 'unknown')) > type_score(cur.get('shape_type', 'unknown')):
                    best_by_point[key] = cand

    return list(best_by_point.values())


# --- Path segmentation for placement ---

def extract_path_segments(tikz_parts: List[str]) -> Dict[int, List[tuple[Point, Point]]]:
    """Extract straight path segments for each draw line.

    Returns a mapping: render_index -> list of (start_point, end_point) tuples.
    Skips auxiliary arrowhead lines containing 'shift={...}'.
    """
    segments_by_line: Dict[int, List[tuple[Point, Point]]] = {}
    for idx, line in enumerate(tikz_parts):
        if not line:
            continue
        if 'shift={' in line:
            continue
        s = line.strip()
        if not s.startswith('\\draw'):
            continue
        if ('--' not in s) and (' to ' not in s):
            continue
        coords = []
        for m in COORD_RE.finditer(line):
            try:
                x = float(m.group(1)); y = float(m.group(2))
                coords.append((x, y))
            except Exception:
                continue
        if len(coords) < 2:
            continue
        segs: List[tuple[Point, Point]] = []
        for i in range(len(coords) - 1):
            segs.append((coords[i], coords[i+1]))
        if segs:
            segments_by_line[idx] = segs
    return segments_by_line
