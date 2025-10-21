"""Compatibility shim for legacy imports.

Some modules import `modules.shapes.lines.shared_arrow_logic`, but the
implementation lives in `utils.geometry.shared_arrow_logic`.
This shim re-exports the required symbols.
"""
from __future__ import annotations

from utils.geometry.shared_arrow_logic import (  # noqa: F401
    AnchorInfo,
    ArrowDirection,
    BoundaryArrows,
    Point,
    extract_arrow_anchor,
    extract_style_block,
    parse_points_from_draw,
)

__all__ = [
    "AnchorInfo",
    "ArrowDirection",
    "BoundaryArrows",
    "Point",
    "extract_arrow_anchor",
    "extract_style_block",
    "parse_points_from_draw",
]
