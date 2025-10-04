"""
Color utilities shared by color processing modules.

Provides precompiled regex patterns and helper functions for working
with Mathcha/TikZ color specifications.
"""
from __future__ import annotations

import re
from typing import Tuple

# Precompiled regex patterns
# Standalone RGB spec like: {rgb, 255:red, 118; green, 127; blue, 166}
RGB_PATTERN = re.compile(
    r"\{rgb\s*,\s*255\s*:\s*red\s*,\s*(\d+)\s*;\s*green\s*,\s*(\d+)\s*;\s*blue\s*,\s*(\d+)\s*\}",
    re.IGNORECASE,
)

# color=... style key with an RGB spec (with or without braces)
COLOR_SPEC_PATTERN = re.compile(
    r"color\s*=\s*(?:\{)?rgb\s*,\s*255\s*:\s*red\s*,\s*(\d+)\s*;\s*green\s*,\s*(\d+)\s*;\s*blue\s*,\s*(\d+)\s*(?:\})?",
    re.IGNORECASE,
)

# fill=... style key with an RGB spec
FILL_COLOR_PATTERN = re.compile(
    r"fill\s*=\s*\{rgb\s*,\s*255\s*:\s*red\s*,\s*(\d+)\s*;\s*green\s*,\s*(\d+)\s*;\s*blue\s*,\s*(\d+)\s*\}",
    re.IGNORECASE,
)


def build_rgb_spec_int(r: int, g: int, b: int) -> str:
    """Build a canonical RGB spec string used in replacements.

    Example: {rgb, 255:red, 118; green, 127; blue, 166}
    """
    return f"{{rgb, 255:red, {r}; green, {g}; blue, {b}}}"


def normalize_rgb_255(rgb_tuple: Tuple[int, int, int]) -> Tuple[float, float, float]:
    """Normalize 0..255 RGB components to 0..1 floats."""
    r, g, b = rgb_tuple
    return (r / 255.0, g / 255.0, b / 255.0)
