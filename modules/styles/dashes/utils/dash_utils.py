"""
Dash utilities shared by dashes modules.

Contains:
- DASH_PATTERNS dictionary with known pattern -> named style mappings
- Precompiled regex patterns used across modules
- Helper functions for splitting style blocks and normalizing dash content
"""
from __future__ import annotations

from typing import Dict, List, Tuple
import re

# Comprehensive dictionary of dash patterns found in Mathcha output
DASH_PATTERNS: Dict[str, str] = {
    # Standard dashed patterns
    'on 4.5pt off 4.5pt': 'dashed',
    'on 4.5pt off 4.5pt on 4.5pt off 4.5pt': 'dashed',  # Duplicate pattern

    # Dotted patterns
    'on 0.84pt off 2.51pt': 'dotted',
    'on 0.84pt off 2.51pt on 0.84pt off 2.51pt': 'dotted',  # Duplicate pattern

    # Fine dotted patterns (for arrowheads and small elements)
    'on 0.08pt off 2.29pt': 'densely dotted',

    # Arrowhead-specific patterns
    'on 3.49pt off 4.5pt': 'densely dashed',

    # Additional patterns that might appear
    'on 2pt off 2pt': 'densely dashed',
    'on 1pt off 1pt': 'densely dotted',
    'on 6pt off 6pt': 'loosely dashed',
    'on 1pt off 3pt': 'densely dotted',
}

# Regex for dash pattern key/value inside a style block (pairs: on <num>pt off <num>pt)
PAIR_RE = re.compile(r"\bon\s+([\d.]+)\s*pt\s+off\s+([\d.]+)\s*pt\b", re.IGNORECASE)
# Find style blocks [ ... ]
STYLE_BLOCK_RE = re.compile(r"\[(?P<content>[^\]]*)\]")
# Regex to find dash pattern key-value pairs
DASH_KV_RE = re.compile(r"dash\s+pattern\s*=\s*\{([^}]*)\}", re.IGNORECASE)


def split_style_parts(style_content: str) -> List[str]:
    """
    Split style content by commas, respecting nested braces.
    Preserves newlines within nested structures like decoration={...}.
    """
    parts: List[str] = []
    current: List[str] = []
    brace_depth = 0

    for char in style_content:
        if char == '{':
            brace_depth += 1
            current.append(char)
        elif char == '}':
            brace_depth -= 1
            current.append(char)
        elif char == ',' and brace_depth == 0:
            # Top-level comma - split here
            part = ''.join(current).strip()
            if part:
                parts.append(part)
            current = []
        else:
            current.append(char)

    # Add the last part
    part = ''.join(current).strip()
    if part:
        parts.append(part)

    return parts


def normalize_pattern_content(content: str) -> Tuple[str, List[Tuple[float, float]]]:
    """Normalize inside {...} and return normalized string and parsed pairs."""
    norm_pairs: List[str] = []
    parsed: List[Tuple[float, float]] = []
    for m in PAIR_RE.finditer(content):
        on = m.group(1)
        off = m.group(2)
        try:
            on_f = float(on)
            off_f = float(off)
            parsed.append((on_f, off_f))
        except ValueError:
            # Skip unparsable pair
            continue
        # normalized with single spaces and lowercase keywords
        norm_pairs.append(f"on {on_f:g}pt off {off_f:g}pt")
    normalized = " ".join(norm_pairs)
    return normalized, parsed
