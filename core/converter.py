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

            # Prepare renderer configuration (including nodes list)
            renderer_cfg = dict(self.config.get('renderer_options') or {})
            try:
                from modules.nodes.node_parser import NodeParser
                nodes_list = NodeParser().parse_nodes(input_str)
            except Exception:
                nodes_list = []
            if nodes_list:
                # Default distance threshold (in TikZ units) to avoid far matches
                default_max_dist = renderer_cfg.get('nodes', {}).get('max_distance', 30.0) if isinstance(renderer_cfg.get('nodes', {}), dict) else 50.0
                renderer_cfg['nodes'] = {'enabled': True, 'list': nodes_list, 'max_distance': default_max_dist}
            else:
                renderer_cfg['nodes'] = {'enabled': False, 'list': []}

            # Configure renderer and render
            try:
                self.renderer.configure(renderer_cfg)
            except Exception:
                # Non-fatal; renderer will use defaults
                pass

            rendered_output = self.renderer.render(processed_shapes, mode=mode)
            if not rendered_output:
                raise RenderingError("Rendering produced empty output")

            postprocessed = self.postprocessor.process(rendered_output)

            # Optional nodes injection after postprocessing to avoid style/caption transforms
            processed_body = postprocessed.get("processed_body", "")
            color_defs = postprocessed.get("color_definitions", "")

            try:
                if nodes_list:
                    from utils.nodes.anchors import collect_anchors_from_tikz_parts
                    from modules.nodes.node_placer import NodePlacer

                    tikz_parts = processed_body.splitlines()
                    anchors = collect_anchors_from_tikz_parts(tikz_parts, nodes_list, start_index=0)

                    nodes_cfg = (renderer_cfg or {}).get('nodes', {}) if isinstance(renderer_cfg, dict) else {}
                    max_distance = nodes_cfg.get('max_distance') if isinstance(nodes_cfg, dict) else None
                    if not isinstance(max_distance, (int, float)):
                        max_distance = None

                    placements = NodePlacer().place_nodes(nodes_list, anchors, max_distance=max_distance)

                    def _inject_snippet(draw_code: str, snippet: str) -> str:
                        if not draw_code:
                            return draw_code
                        idx = draw_code.rfind(';')
                        if idx == -1:
                            return f"{draw_code} {snippet}"
                        return f"{draw_code[:idx]} {snippet}{draw_code[idx:]}"

                    for pl in placements:
                        try:
                            target_idx = int(pl.get('render_index', -1))
                            if 0 <= target_idx < len(tikz_parts):
                                tikz_parts[target_idx] = _inject_snippet(tikz_parts[target_idx], pl.get('snippet', ''))
                        except Exception:
                            continue

                    import re

                    # Prepare lookup of placed node indices
                    placed_node_idxs = {int(pl.get('node_index')) for pl in placements if 'node_index' in pl}

                    # Build coordinate-index lookups by source type
                    draw_inline_coords = []  # (idx, x, y)
                    node_cmd_coords = []     # (idx, x, y)
                    for idx, n in enumerate(nodes_list):
                        at = n.get('at')
                        if not at or not isinstance(at, (list, tuple)) or len(at) < 2:
                            continue
                        try:
                            x, y = float(at[0]), float(at[1])
                        except Exception:
                            continue
                        if n.get('source') == 'draw_inline':
                            draw_inline_coords.append((idx, x, y))
                        else:  # default treat as node_cmd
                            node_cmd_coords.append((idx, x, y))

                    # Regexes to match lines and extract the immediate node coordinates
                    COORD0 = r"\(\s*\{?\s*([-+]?\d+(?:\.\d+)?)\s*\}?\s*,\s*\{?\s*([-+]?\d+(?:\.\d+)?)\s*\}?\s*\)"
                    DRAW_NODE_LINE_RE = re.compile(rf"^\s*\\draw\s*{COORD0}\s*node\b", re.DOTALL)
                    NODE_AT_LINE_RE = re.compile(rf"^\s*\\node\b.*?at\s*{COORD0}", re.DOTALL)

                    def _is_comment_only(part: str) -> bool:
                        if not part:
                            return False
                        lines = [ln for ln in (part.splitlines() or []) if ln.strip()]
                        if not lines:
                            return False
                        return all(ln.strip().startswith('%') for ln in lines)

                    filtered_parts: list[str] = []
                    for i, part in enumerate(tikz_parts):
                        # Remove only if we can match to a placed node
                        stripped = (part or '').strip()
                        # Skip comments-only and empty
                        if not stripped or _is_comment_only(part):
                            filtered_parts.append(part)
                            continue

                        removed = False
                        m = DRAW_NODE_LINE_RE.match(stripped)
                        if m and ('--' not in stripped) and ('controls' not in stripped):
                            try:
                                x = float(m.group(1)); y = float(m.group(2))
                                for idx, xi, yi in draw_inline_coords:
                                    if abs(x - xi) < 1e-6 and abs(y - yi) < 1e-6 and idx in placed_node_idxs:
                                        # Optionally remove preceding comment-only
                                        if filtered_parts and _is_comment_only(filtered_parts[-1]):
                                            filtered_parts.pop()
                                        removed = True
                                        break
                            except Exception:
                                pass

                        if not removed:
                            m2 = NODE_AT_LINE_RE.match(stripped)
                            if m2:
                                try:
                                    x = float(m2.group(1)); y = float(m2.group(2))
                                    for idx, xi, yi in node_cmd_coords:
                                        if abs(x - xi) < 1e-6 and abs(y - yi) < 1e-6 and idx in placed_node_idxs:
                                            if filtered_parts and _is_comment_only(filtered_parts[-1]):
                                                filtered_parts.pop()
                                            removed = True
                                            break
                                except Exception:
                                    pass

                        if removed:
                            continue
                        filtered_parts.append(part)
                    processed_body = "\n".join(filtered_parts)
            except Exception as exc:
                logger.warning("Nodes injection failed: %s", exc)

            return self.renderer.compose_output(
                color_defs,
                processed_body,
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

