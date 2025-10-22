from __future__ import annotations

from typing import List, Optional, TypedDict, Literal

ArrowDirection = Literal['<', '>']


class MidArrow(TypedDict):
    position: float
    direction: ArrowDirection


class ArrowsInfo(TypedDict, total=False):
    start_arrow: Optional[ArrowDirection]
    end_arrow: Optional[ArrowDirection]
    mid_arrows: List[MidArrow]
