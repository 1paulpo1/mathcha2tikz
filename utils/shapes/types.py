from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, TypedDict, Literal, Union

from utils.arrows.types import ArrowsInfo, MidArrow, ArrowDirection


Point = Tuple[float, float]

ShapeKind = Literal[
    'StraightLine', 'Line',
    'CurveLine', 'Curve',
    'EllipseShape', 'Ellipse', 'Circle',
    'ArcShape', 'Arc', 'arc',
]


class InlineTikz(TypedDict, total=False):
    tikz_code: str


class BaseProcessedShape(TypedDict, total=False):
    type: str
    id: str
    normalized_type: str


class StraightPayload(BaseProcessedShape, total=False):
    style_str: str
    styles: Dict[str, Any]
    start_point: Point
    end_point: Point
    start_arrow: Optional[ArrowDirection]
    end_arrow: Optional[ArrowDirection]
    mid_arrows: List[MidArrow]


class CurvePayload(BaseProcessedShape, total=False):
    style_str: str
    styles: Dict[str, Any]
    start_point: Point
    end_point: Point
    segments: List[List[Point]]
    is_closed: bool
    start_arrow: Optional[ArrowDirection]
    end_arrow: Optional[ArrowDirection]
    mid_arrows: List[MidArrow]


class EllipsePayload(BaseProcessedShape, total=False):
    center: Point
    major_axis: float
    minor_axis: float
    rotation: float
    is_circle: bool
    styles: Dict[str, Any]


class ArcPayload(BaseProcessedShape, total=False):
    center: Point
    major_axis: float
    minor_axis: float
    rotation: float
    start_angle: float
    end_angle: float
    styles: Dict[str, Any]
    arrows: ArrowsInfo
    type: Literal['Arc', 'ArcShape', 'arc']


ProcessedShape = Union[
    InlineTikz,
    StraightPayload,
    CurvePayload,
    EllipsePayload,
    ArcPayload,
]
