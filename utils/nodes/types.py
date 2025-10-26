from __future__ import annotations

from typing import Optional, TypedDict, Literal

from utils.shapes.types import Point
from utils.shapes.styles import StyleDict


class ParsedNode(TypedDict, total=False):
    id: str
    at: Point
    content: str
    styles: StyleDict
    raw: str
    source: Literal['node_cmd', 'draw_inline']


class Anchor(TypedDict, total=False):
    point: Point
    render_index: int
    kind: Literal['start', 'end', 'center', 'mid', 'other']
    shape_type: str
    shape_id: Optional[str]
    style_weight: int


class NodePlacement(TypedDict, total=False):
    node_index: int
    anchor_index: int
    render_index: int
    position: str
    angle: float
    distance: float
    snippet: str
