"""
DashPatternPostProcessor

- Normalizes dash pattern formatting
- De-duplicates multiple dash pattern entries per style block
- Converts exact matches from DASH_PATTERNS into named TikZ dash styles (e.g., dashed, dotted)

This is intentionally conservative: only exact dictionary matches are converted.
Future work: fuzzy matching to closest known pattern.
"""
from __future__ import annotations

from typing import Dict, Any, List, Tuple
import re
from .utils.dash_utils import (
    DASH_PATTERNS,
    PAIR_RE,
    STYLE_BLOCK_RE,
    DASH_KV_RE,
    split_style_parts,
    normalize_pattern_content,
)


class DashPatternPostProcessor:
    def __init__(self) -> None:
        # Use shared precompiled regex and helpers
        self._pair_re = PAIR_RE
        self._style_block_re = STYLE_BLOCK_RE
        self._dash_kv_re = DASH_KV_RE

    def _split_style_parts(self, style_content: str) -> List[str]:
        """Deprecated: kept for backward compatibility, now delegates to utils."""
        return split_style_parts(style_content)

    def _normalize_pattern_content(self, content: str) -> Tuple[str, List[Tuple[float, float]]]:
        """Deprecated: kept for backward compatibility, now delegates to utils."""
        return normalize_pattern_content(content)

    def _dedupe_and_convert_in_style(self, style_content: str) -> Tuple[str, Dict[str, int]]:
        """Process one style content (inside [...]) and return new content and stats."""
        stats = {
            'duplicates_removed': 0,
            'normalized': 0,
            'converted_to_named': 0,
            'malformed_removed': 0,
        }

        # Gather all dash pattern occurrences
        matches = list(self._dash_kv_re.finditer(style_content))
        if not matches:
            return style_content, stats

        # Keep only the first occurrence; remove others
        if len(matches) > 1:
            # remove from the end to preserve indices
            for m in reversed(matches[1:]):
                style_content = style_content[:m.start()] + style_content[m.end():]
                stats['duplicates_removed'] += 1
            matches = matches[:1]

        # Normalize the remaining one
        m = matches[0]
        inner = m.group(1)
        normalized, pairs = normalize_pattern_content(inner)
        if not pairs:
            # remove malformed entirely
            style_content = style_content[:m.start()] + style_content[m.end():]
            stats['malformed_removed'] += 1
            return style_content, stats

        # Check exact dictionary conversion (only exact string match)
        # Note: DASH_PATTERNS keys expect the textual inside {...}
        mapped_name = DASH_PATTERNS.get(normalized)
        if mapped_name:
            # Remove the dash pattern kv and inject the named style token if not present
            before = style_content[:m.start()].rstrip()
            after = style_content[m.end():].lstrip()
            # Reconstruct without the dash pattern kv
            style_content = (before + (', ' if before and not before.endswith('[') else '') + after).strip(', ')

            # Split by commas (top-level), respecting nested braces
            parts = split_style_parts(style_content)
            # Avoid duplicate named tokens
            if mapped_name not in parts:
                parts.append(mapped_name)
            style_content = ', '.join(parts)
            stats['converted_to_named'] += 1
        else:
            # Replace the dash pattern value with normalized text
            repl = f"dash pattern={{{normalized}}}"
            style_content = style_content[:m.start()] + repl + style_content[m.end():]
            stats['normalized'] += 1

        return style_content, stats

    def process(self, tikz_code: str) -> Dict[str, Any]:
        if not tikz_code:
            return {'processed_code': tikz_code, 'conversion_stats': {}}

        total = {
            'style_blocks': 0,
            'duplicates_removed': 0,
            'normalized': 0,
            'converted_to_named': 0,
            'malformed_removed': 0,
        }

        def _process_block(m: re.Match) -> str:
            content = m.group('content')
            total['style_blocks'] += 1
            new_content, stats = self._dedupe_and_convert_in_style(content)
            for k in stats:
                total[k] += stats[k]
            return f"[{new_content}]"

        processed = self._style_block_re.sub(_process_block, tikz_code)
        return {'processed_code': processed, 'conversion_stats': total}
