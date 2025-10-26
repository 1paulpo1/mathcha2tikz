from __future__ import annotations

from typing import List, Dict, Any

from utils.nodes.types import Anchor, NodePlacement
from utils.nodes.anchors import anchors_to_points
from utils.nodes.search import nearest_point
from utils.nodes.positioning import angle_to_position
from utils.geometry.vector_analysis import angle_from_vector
from utils.geometry.base_geometry import distance
from utils.geometry.point_path_operations import project_point_on_segment
from utils.shapes.types import Point


class NodePlacer:
    """Compute placements for nodes relative to nearest anchor P.

    Produces insertion snippets of the form:
        node[<position>] {<content>}
    without explicit coordinates, intended to be inserted just before the
    terminating semicolon of the draw command that produced the anchor point.
    """

    def place_nodes(
        self,
        nodes: List[Dict[str, Any]],
        anchors: List[Anchor],
        max_distance: float | None = None,
        allowed_types: tuple[str, ...] | None = None,
        segments_by_line: Dict[int, List[tuple[Point, Point]]] | None = None,
    ) -> List[NodePlacement]:
        if not nodes or not anchors:
            return []

        points: List[Point] = anchors_to_points(anchors)
        # Restrict anchors to allowed types (default: only 'path')
        type_order = allowed_types or ('path',)
        allowed_idx: List[int] = [i for i, anc in enumerate(anchors) if str(anc.get('shape_type', 'unknown')) in type_order]
        # Build mapping from render_index -> indices of anchors in that line (for fallback angle)
        anchors_by_line: Dict[int, List[int]] = {}
        for i in allowed_idx:
            ri = int(anchors[i].get('render_index', -1))
            if ri < 0:
                continue
            anchors_by_line.setdefault(ri, []).append(i)
        placements: List[NodePlacement] = []

        for n_idx, node in enumerate(nodes):
            at = node.get('at')
            content = node.get('content', '')
            if not at or not isinstance(at, (list, tuple)) or len(at) < 2:
                continue

            # Segment-based nearest search across allowed path lines
            qpt = (float(at[0]), float(at[1]))
            best_line = -1
            best_seg = (-1, -1)
            best_d = float('inf')
            best_foot: Point | None = None
            best_pos_on_path = 0.0

            if segments_by_line:
                for ri, segs in segments_by_line.items():
                    if ri not in anchors_by_line:
                        # restrict to allowed types only
                        continue
                    # compute total length once
                    seg_lengths = [distance(a, b) for (a, b) in segs]
                    total_len = sum(seg_lengths) or 1.0
                    cum_len = 0.0
                    for si, (a, b) in enumerate(segs):
                        t = project_point_on_segment(qpt, a, b)
                        foot = (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
                        d = distance(qpt, foot)
                        if d < best_d:
                            best_d = d
                            best_line = ri
                            best_seg = (ri, si)
                            best_foot = foot
                            best_pos_on_path = (cum_len + t * seg_lengths[si]) / total_len
                    # update cum_len at end of loop iteration
                        # done inside loop increment below
                        
                        # next segment cum_len
                    # rebuild cum_len loop to accumulate lengths
                    # (we need separate loop to compute pos correctly)
                # re-evaluate to compute pos accurately for chosen line
                if best_line >= 0:
                    segs = segments_by_line.get(best_line, [])
                    seg_lengths = [distance(a, b) for (a, b) in segs]
                    total_len = sum(seg_lengths) or 1.0
                    cum_len = 0.0
                    for si, (a, b) in enumerate(segs):
                        t = project_point_on_segment(qpt, a, b)
                        foot = (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
                        d = distance(qpt, foot)
                        if si == (best_seg[1]):
                            best_pos_on_path = (cum_len + t * seg_lengths[si]) / total_len
                            best_foot = foot
                            break
                        cum_len += seg_lengths[si]

            # Fallback to anchor points if no segments available
            if best_line < 0:
                # Nearest anchor among allowed indices
                allowed_points = [anchors[i]['point'] for i in allowed_idx]
                rel_idx, best_d = nearest_point(allowed_points, qpt)
                if rel_idx < 0:
                    continue
                a_idx = allowed_idx[rel_idx]
                best_line = int(anchors[a_idx].get('render_index', -1))
                best_foot = anchors[a_idx]['point']
                best_pos_on_path = 1.0  # end by default

            if max_distance is not None and best_d > max_distance:
                continue

            # Compute direction from foot to node for placement keyword
            fx, fy = best_foot if best_foot is not None else qpt
            dx = qpt[0] - fx
            dy = qpt[1] - fy
            if dx == 0.0 and dy == 0.0:
                dx, dy = 1.0, 0.0

            angle = angle_from_vector((dx, -dy))
            position = angle_to_position(angle)
            attrs = []
            if best_pos_on_path < 1.0 - 1e-6:
                attrs.append(f"pos={best_pos_on_path:.2f}")
            attrs.append(position)
            attr_str = ", ".join(attrs)
            snippet = f"node[{attr_str}] {{{content}}}"

            placements.append(
                NodePlacement(
                    node_index=n_idx,
                    anchor_index=-1,
                    render_index=int(best_line),
                    position=position,
                    angle=angle,
                    distance=best_d,
                    snippet=snippet,
                )
            )

        return placements
