from __future__ import annotations

from typing import Callable, List, Optional, Sequence, Tuple, Dict

from .parser_utils import (
    iter_draw_commands,
    is_arrow_line,
    choose_main_draw,
    extract_styles,
)


class BaseParser:
    """Common parser scaffold for shape parsers.

    Configure selection heuristics via constructor arguments.
    """

    def __init__(
        self,
        *,
        require_bezier: Optional[bool] = None,
        require_closed: Optional[bool] = None,
        exclude_opacity_zero: bool = True,
        main_filter: Optional[Callable[[str], bool]] = None,
    ) -> None:
        self.require_bezier = require_bezier
        self.require_closed = require_closed
        self.exclude_opacity_zero = exclude_opacity_zero
        self.main_filter = main_filter

    def parse_shape(self, raw_block: str) -> Tuple[Optional[str], List[str], Dict]:
        raw = raw_block or ""
        draws = iter_draw_commands(raw)
        arrow_cmds = [d for d in draws if is_arrow_line(d)]
        body = [d for d in draws if not is_arrow_line(d)]

        if self.main_filter is not None:
            body = [d for d in body if self.main_filter(d)]

        main = choose_main_draw(
            body,
            require_bezier=self.require_bezier,
            require_closed=self.require_closed,
            exclude_opacity_zero=self.exclude_opacity_zero,
        )
        styles = extract_styles(main) if main else {}
        return main, arrow_cmds, styles
