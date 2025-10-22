from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from core.processor import BaseProcessor as CoreBaseProcessor
from core.exceptions import ProcessingError, RenderingError

logger = logging.getLogger(__name__)


class BaseShapeProcessor(CoreBaseProcessor):
    """Shared scaffold for shape processors.

    Subclasses should set parser, renderer and override hooks:
      - process_arrows(main, arrow_cmds) -> Dict
      - build_render_payload(main, styles, extras) -> Dict
      - post_process(payload, extras, result) -> Dict (optional)

    use_inline_renderer controls whether to render immediately (True)
    or return a normalized payload for GlobalRenderer (False), e.g. Arc.
    """

    def __init__(self, shape_instance=None, parser=None, renderer=None) -> None:
        super().__init__(shape_instance)
        self.parser = parser
        self.renderer = renderer
        self.use_inline_renderer: bool = True
        # Default logical type for inline-rendered shapes (e.g., 'StraightLine', 'CurveLine', 'Ellipse').
        # Subclasses should set this; Arc keeps inline rendering off and sets explicit type in payload.
        self.default_type: Optional[str] = None

    # ---------- Core pipeline ----------
    def process(self, raw_block: Optional[str] = None) -> Dict[str, Any]:
        raw = self.get_raw_block(raw_block)
        if not raw:
            return self.passthrough(raw)

        try:
            main, arrow_cmds, styles = self.parse(raw)
        except Exception as exc:  # pragma: no cover
            logger.exception("Parser failure")
            raise ProcessingError(f"Parser failure: {exc}") from exc

        if not main:
            return self.passthrough(raw)

        try:
            extras = dict(self.process_arrows(main, arrow_cmds) or {})
            # Provide original raw block to hooks for robust passthrough fallbacks.
            extras.setdefault('_raw_block', raw)
            extras.setdefault('_arrow_cmds', arrow_cmds)
            payload = self.build_render_payload(main, styles or {}, extras)
            self.attach_id(payload)
            result = self.render_or_prepare(payload)
            # Set default inline type before subclass post-processing (subclass may override)
            if self.use_inline_renderer and isinstance(result, dict) and self.default_type:
                result.setdefault('type', self.default_type)
            result = self.post_process(payload, extras, result)
            # Ensure type is present if subclass didn't override
            if self.use_inline_renderer and isinstance(result, dict) and self.default_type:
                result.setdefault('type', self.default_type)
            return result
        except (ProcessingError, RenderingError):
            raise
        except Exception as exc:  # pragma: no cover
            logger.exception("Processor failure")
            raise ProcessingError(f"Processor failure: {exc}") from exc

    # ---------- Utilities ----------
    def get_raw_block(self, raw_block: Optional[str]) -> str:
        if raw_block:
            return raw_block
        if self.shape_instance is not None:
            return (
                getattr(self.shape_instance, 'raw_block', '')
                or getattr(self.shape_instance, 'raw_command', '')
                or ''
            )
        return ''

    def passthrough(self, raw: str) -> Dict[str, Any]:
        return {'tikz_code': raw or ''}

    def attach_id(self, payload: Dict[str, Any]) -> None:
        if self.shape_instance is not None:
            sid = getattr(self.shape_instance, 'id', None)
            if sid:
                payload['id'] = sid

    def parse(self, raw: str):
        if not self.parser:
            return None, [], {}
        return self.parser.parse_shape(raw)

    # ---------- Hooks for subclasses ----------
    def process_arrows(self, main: str, arrow_cmds: List[str]) -> Dict[str, Any]:
        return {}

    def build_render_payload(self, main: str, styles: Dict[str, Any], extras: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def render_or_prepare(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if self.use_inline_renderer:
            if not self.renderer:
                raise RenderingError("Renderer not configured")
            rendered = self.renderer.render(payload)
            return rendered if isinstance(rendered, dict) else {'tikz_code': str(rendered)}
        return payload

    def post_process(self, payload: Dict[str, Any], extras: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        return result

    def validate(self) -> bool:
        return True
