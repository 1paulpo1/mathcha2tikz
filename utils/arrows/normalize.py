from __future__ import annotations

from typing import Any, Dict, List

from .types import ArrowsInfo, MidArrow, ArrowDirection


def _normalize_direction(value: Any) -> ArrowDirection | None:
    if value in ('<', '>'):
        return value  # type: ignore[return-value]
    # Some processors might emit strings like 'left'/'right' or actual literals already
    if isinstance(value, str):
        v = value.strip().lower()
        if v in ('<', 'left', 'start'):
            return '<'  # type: ignore[return-value]
        if v in ('>', 'right', 'end'):
            return '>'  # type: ignore[return-value]
    return None


def normalize_arrows(obj: Dict[str, Any] | None) -> ArrowsInfo:
    """Convert shape-specific arrow payload into a standard ArrowsInfo.

    Accepted forms:
      - {'start_arrow': '<', 'end_arrow': '>'}
      - {'start': '<', 'end': '>'}
      - {'mid_arrows': [{'position': 0.3, 'direction': '>'}, ...]}
    Unknown fields are ignored.
    """
    result: ArrowsInfo = {}
    if not obj:
        return result

    start = obj.get('start_arrow', obj.get('start'))
    end = obj.get('end_arrow', obj.get('end'))
    start_dir = _normalize_direction(start)
    end_dir = _normalize_direction(end)
    if start_dir is not None:
        result['start_arrow'] = start_dir
    if end_dir is not None:
        result['end_arrow'] = end_dir

    mids_in: List[Dict[str, Any]] = obj.get('mid_arrows') or []
    mids_norm: List[MidArrow] = []
    for item in mids_in:
        try:
            pos = float(item.get('position', 0.0))
        except Exception:
            continue
        direction = _normalize_direction(item.get('direction'))
        if direction is None:
            continue
        mids_norm.append({'position': pos, 'direction': direction})
    if mids_norm:
        # Sort mid arrows by position for consistency
        mids_norm.sort(key=lambda x: x['position'])
        result['mid_arrows'] = mids_norm

    return result
