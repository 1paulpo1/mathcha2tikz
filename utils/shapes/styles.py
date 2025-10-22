from __future__ import annotations

from typing import TypedDict

# Unified style dictionary used by shape parsers to describe extracted inline styles
# such as color, draw opacity, and dash pattern.
StyleDict = TypedDict(
    'StyleDict',
    {
        'color': str,
        'opacity': float,
        'dash pattern': str,
    },
    total=False,
)
