from __future__ import annotations

import logging
import re
from typing import List

logger = logging.getLogger('modules.nodes.node_parser')


NODE_PATTERN = re.compile(
    r"\\node(?P<prefix>.*?)at\s*\(\s*(?P<x>[-+]?\d+(?:\.\d+)?)\s*,\s*(?P<y>[-+]?\d+(?:\.\d+)?)\s*\)\s*\{(?P<content>.*?)\}\s*;",
    re.DOTALL,
)

ID_PATTERN = re.compile(r"\((?P<id>[^)]+)\)")

# Standalone draw-node lines: \draw (x,y) node [options] {content};
# This matches only when 'node' follows immediately after the first coordinate pair,
# thus avoiding path-internal nodes like: \draw ... -- (x,y) node ...
DRAW_NODE_PATTERN = re.compile(
    r"^\s*\\draw\s*\(\s*(?P<x>[-+]?\d+(?:\.\d+)?)\s*,\s*(?P<y>[-+]?\d+(?:\.\d+)?)\s*\)\s*node(?:\s*\[[^\]]*\])*\s*\{(?P<content>.*?)\}\s*;\s*$",
    re.DOTALL | re.MULTILINE,
)


class NodeParser:
    """Extract TikZ node commands from a raw block.

    Supported forms (order of id/options is flexible as long as they appear before 'at'):
      \node (id) [options] at (x, y) {content};
      \node [options] (id) at (x, y) {content};
      \node at (x, y) {content};
    """

    def parse_nodes(self, raw_block: str) -> List[dict]:
        text = raw_block or ''
        nodes: List[dict] = []
        seen = set()
        for m in NODE_PATTERN.finditer(text):
            prefix = m.group('prefix') or ''
            x = float(m.group('x'))
            y = float(m.group('y'))
            content = (m.group('content') or '').strip()
            raw = m.group(0)

            # id: first (...) in prefix
            node_id = None
            id_match = ID_PATTERN.search(prefix)
            if id_match:
                node_id = id_match.group('id').strip()

            node = {
                'id': node_id,
                'at': (x, y),  # type: ignore[assignment]
                'content': content,
                'raw': raw,
                'source': 'node_cmd',
            }
            key = (x, y, content)
            if key not in seen:
                seen.add(key)
                nodes.append(node)

        # Parse standalone draw-based node lines (Text Node)
        for m in DRAW_NODE_PATTERN.finditer(text):
            x = float(m.group('x'))
            y = float(m.group('y'))
            content = (m.group('content') or '').strip()
            raw = m.group(0)

            key = (x, y, content)
            if key in seen:
                continue
            seen.add(key)

            nodes.append(
                {
                    'id': None,
                    'at': (x, y),  # type: ignore[assignment]
                    'content': content,
                    'raw': raw,
                    'source': 'draw_inline',
                }
            )
        logger.debug("NodeParser: found %d nodes", len(nodes))
        return nodes
