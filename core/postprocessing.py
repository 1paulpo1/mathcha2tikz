"""Postprocessing of TikZ render result."""

from __future__ import annotations

import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class PostProcessor:
    """Encapsulates the chain of postprocessors for the final TikZ code."""

    def __init__(self) -> None:
        self._logger = logger

    def process(self, output: str) -> Dict[str, str]:
        """Apply postprocessors and return intermediate result."""
        try:
            color_definitions, processed_body = self._apply_color_postprocessor(output)
        except Exception as exc:  # noqa: BLE001 - return original output
            self._logger.warning(
                "Color post-processing failed, using original output: %s", exc
            )
            return {
                "color_definitions": "",
                "processed_body": output,
            }

        processed_body = self._apply_opacity_postprocessor(processed_body)
        processed_body = self._apply_dash_postprocessor(processed_body)

        self._logger.debug("Post-processing completed")
        return {
            "color_definitions": color_definitions,
            "processed_body": processed_body,
        }

    def _apply_color_postprocessor(self, output: str) -> Tuple[str, str]:
        from modules.styles.colors.color_postprocessor import ColorPostProcessor

        color_postprocessor = ColorPostProcessor()
        color_result = color_postprocessor.process(output)
        self._logger.debug(
            "Color post-processing completed: %s",
            color_result.get("conversion_stats"),
        )
        color_definitions = color_result.get("color_definitions", "")
        processed_body = color_result.get("processed_code", "")
        if not processed_body:
            raise ValueError("Color post-processor returned empty processed_code")
        return color_definitions, processed_body

    def _apply_opacity_postprocessor(self, processed_body: str) -> str:
        try:
            from modules.styles.fillings.opacity_postprocessor import OpacityPostProcessor  
        except Exception as exc:  # noqa: BLE001
            self._logger.warning(
                "Opacity post-processing unavailable, keeping color-processed output: %s",
                exc,
            )
            return processed_body

        try:
            opacity_post = OpacityPostProcessor()
            opacity_result = opacity_post.process(processed_body)
        except Exception as exc:  # noqa: BLE001
            self._logger.warning(
                "Opacity post-processing failed, keeping color-processed output: %s",
                exc,
            )
            return processed_body

        self._logger.debug(
            "Opacity post-processing completed: %s",
            opacity_result.get("conversion_stats"),
        )
        return opacity_result.get("processed_code", processed_body)

    def _apply_dash_postprocessor(self, processed_body: str) -> str:
        try:
            from modules.styles.dashes.dash_postprocessor import DashPatternPostProcessor
        except Exception as exc:  # noqa: BLE001
            self._logger.warning(
                "Dash post-processing unavailable, keeping previous output: %s",
                exc,
            )
            return processed_body

        try:
            dash_post = DashPatternPostProcessor()
            dash_result = dash_post.process(processed_body)
        except Exception as exc:  # noqa: BLE001
            self._logger.warning(
                "Dash post-processing failed, keeping opacity-processed output: %s",
                exc,
            )
            return processed_body

        self._logger.debug(
            "Dash post-processing completed: %s",
            dash_result.get("conversion_stats"),
        )
        return dash_result.get("processed_code", processed_body)

