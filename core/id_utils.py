"""Utilities for building standardized ID comment headers for TikZ shapes."""

from __future__ import annotations

import re
from typing import Optional


def build_id_header(shape_type: str, shape_id: Optional[str], raw: str = "") -> str:
    """Build the standardized ID comment header.

    - shape_type: e.g. "Straight Lines", "Curve Lines"
    - shape_id: unique identifier to embed
    - raw: optional raw source to preserve trailing comment after ID if present
    """
    if not shape_id:
        return ""

    header = f"%{shape_type} [id:{shape_id}]\n"

    if raw:
        # Preserve any extra inline comment that followed the ID in original raw
        # Example to preserve: "%Straight Lines [id:123] % some note"
        pattern = rf"%{re.escape(shape_type)} \[id:[^\]]+\]\s*%\s*(.+)"
        m = re.search(pattern, raw)
        if m:
            header = header.rstrip("\n") + f" % {m.group(1).strip()}\n"

    return header
