from __future__ import annotations

from typing import List, Dict, Any

from utils.nodes.types import Anchor, NodePlacement
from utils.nodes.anchors import anchors_to_points
from utils.nodes.search import nearest_point
from utils.nodes.positioning import angle_to_position
from utils.geometry.vector_analysis import angle_from_vector
from utils.shapes.types import Point


class NodePlacer:
    """Compute placements for nodes relative to nearest anchor P.

    Produces insertion snippets of the form:
        node[<position>] {<content>}
    without explicit coordinates, intended to be inserted just before the
    terminating semicolon of the draw command that produced the anchor point.
    """

    def place_nodes(self, nodes: List[Dict[str, Any]], anchors: List[Anchor], max_distance: float | None = None) -> List[NodePlacement]:
        if not nodes or not anchors:
            return []

        points: List[Point] = anchors_to_points(anchors)
        placements: List[NodePlacement] = []

        for n_idx, node in enumerate(nodes):
            at = node.get('at')
            content = node.get('content', '')
            if not at or not isinstance(at, (list, tuple)) or len(at) < 2:
                continue

            # Find nearest anchor P
            a_idx, dist = nearest_point(points, (float(at[0]), float(at[1])))
            if a_idx < 0:
                continue

            anc = anchors[a_idx]
            px, py = anc['point']
            dx = float(at[0]) - float(px)
            dy = float(at[1]) - float(py)

            # Distance threshold: skip if too far
            if max_distance is not None and dist > max_distance:
                continue

            # If coincident, pick a tiny rightward vector to stabilize angle
            if dx == 0.0 and dy == 0.0:
                dx = 1.0
                dy = 0.0

            # Invert Y for screen coordinate system (yscale = -1)
            angle = angle_from_vector((dx, -dy))
            position = angle_to_position(angle)
            snippet = f"node[{position}] {{{content}}}"

            placements.append(
                NodePlacement(
                    node_index=n_idx,
                    anchor_index=a_idx,
                    render_index=int(anc['render_index']),
                    position=position,
                    angle=angle,
                    distance=dist,
                    snippet=snippet,
                )
            )

        return placements
