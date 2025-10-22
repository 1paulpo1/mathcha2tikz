from __future__ import annotations

from typing import Callable, List, Tuple

Point = Tuple[float, float]


def build_line_coords(start: Point, end: Point, fmt_point: Callable[[Point], str]) -> str:
    """Return a TikZ line path between two points using provided formatter.

    Example: "(x1, y1) -- (x2, y2)"
    """
    return f"{fmt_point(start)} -- {fmt_point(end)}"


def build_curve_path(
    segments: List[List[Point]],
    is_closed: bool,
    fmt_point: Callable[[Point], str],
    multiline: bool = True,
) -> str:
    """Build a TikZ bezier path from cubic segments.

    Each segment is [P0, C1, C2, P3]. The first segment starts with P0,
    subsequent segments append ".. controls C1 and C2 .. P3".
    """
    if not segments:
        return ""

    parts: List[str] = []
    for i, seg in enumerate(segments):
        if len(seg) != 4:
            continue
        p0, c1, c2, p3 = seg
        p0s, c1s, c2s, p3s = (
            fmt_point(p0),
            fmt_point(c1),
            fmt_point(c2),
            fmt_point(p3),
        )
        if i == 0:
            parts.append(f"{p0s} .. controls {c1s} and {c2s} .. {p3s}")
        else:
            parts.append(f".. controls {c1s} and {c2s} .. {p3s}")

    if is_closed:
        parts.append("-- cycle")

    if multiline and len(parts) > 1:
        return "\n    ".join(parts)
    return " ".join(parts)
