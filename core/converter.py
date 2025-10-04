"""Conversion pipeline for Mathcha to TikZ."""

from __future__ import annotations

import logging
from typing import Dict, Any, Optional

from .exceptions import (
    ParserError,
    DetectionError,
    ProcessingError,
    RenderingError,
)
from .parser import Parser
from .detector import Detector
from .processor import Processor, ensure_builtin_processors_registered
from .renderer import Renderer, ensure_builtin_renderers_registered
from .postprocessing import PostProcessor

logger = logging.getLogger(__name__)


class Converter:
    """High-level pipeline that transforms Mathcha TikZ into optimized TikZ."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        ensure_builtin_processors_registered()
        ensure_builtin_renderers_registered()
        self.parser = Parser()
        self.detector = Detector()
        self.processor = Processor()
        self.renderer = Renderer()
        self.postprocessor = PostProcessor()

    def convert(self, input_str: str, mode: str = "classic") -> str:
        """Convert Mathcha TikZ input to processed output."""
        try:
            shape_blocks = self.parser.parse(input_str)
            if not shape_blocks:
                raise ParserError("No valid shape blocks found in input")

            detected_shapes = []
            for block in shape_blocks:
                try:
                    shapes = self.detector.detect(block)
                    detected_shapes.extend(shapes)
                except DetectionError:
                    logger.warning("Failed to detect shape in block: %s", block)

            if not detected_shapes:
                raise DetectionError("No valid shapes detected in input")

            processed_shapes = []
            for shape in detected_shapes:
                try:
                    processed = self.processor.process(shape)
                    if processed:
                        processed_shapes.append(processed)
                except ProcessingError as exc:
                    logger.warning("Failed to process shape %s: %s", shape, exc)

            if not processed_shapes:
                raise ProcessingError("No shapes were successfully processed")

            rendered_output = self.renderer.render(processed_shapes, mode=mode)
            if not rendered_output:
                raise RenderingError("Rendering produced empty output")

            postprocessed = self.postprocessor.process(rendered_output)
            return self.renderer.compose_output(
                postprocessed["color_definitions"],
                postprocessed["processed_body"],
                mode=mode,
            )

        except (ParserError, DetectionError, ProcessingError, RenderingError):
            raise
        except Exception as exc:
            raise ProcessingError(
                f"Unexpected error during conversion: {exc}"
            ) from exc


def convert(input_str: str, config: Optional[Dict[str, Any]] = None, mode: str = "classic") -> str:
    """Convenience wrapper around `Converter` for single-shot conversion."""
    converter = Converter(config)
    return converter.convert(input_str, mode=mode)


__all__ = ["Converter", "convert"]

