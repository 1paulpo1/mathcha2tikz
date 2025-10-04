import re
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class OpacityPostProcessor:
    """Post-processes TikZ code to normalize/remove draw opacity.

    Rules:
    - Keep draw opacity when value != 1
    - Remove draw opacity=1 from style
    - Clean up resulting empty style brackets [] and stray commas/spaces
    """

    DRAW_CMD_RE = re.compile(r"(\\draw\s*)(\[[^\]]*\])", re.MULTILINE)
    OPACITY_ITEM_RE = re.compile(r"(^|,)\s*draw\s+opacity\s*=\s*([0-9]*\.?[0-9]+)\s*(?=,|$)")

    def _clean_style(self, style: str) -> str:
        # Remove leading/trailing spaces and duplicate commas while preserving newlines
        style = re.sub(r"[ \t]+", " ", style)
        style = re.sub(r" \n", "\n", style)
        style = re.sub(r"\n ", "\n", style)
        style = re.sub(r",\s*,", ", ", style)
        style = style.strip()
        # Trim commas at ends
        style = re.sub(r"^,\s*", "", style)
        style = re.sub(r",\s*$", "", style)
        return style

    def process(self, tikz_code: str) -> Dict[str, object]:
        removed_equal_ones = 0
        kept_not_ones = 0
        modified_segments = 0

        def repl_draw(m: re.Match) -> str:
            nonlocal removed_equal_ones, kept_not_ones, modified_segments
            prefix = m.group(1)
            style_block = m.group(2)  # like [ ... ]
            inside = style_block[1:-1]

            # Find all opacity items
            items = list(self.OPACITY_ITEM_RE.finditer(inside))
            if not items:
                return m.group(0)

            modified = False
            cursor = 0
            rebuilt = []
            for im in items:
                # Append text up to the match
                rebuilt.append(inside[cursor:im.start()])
                value = float(im.group(2))
                if abs(value - 1.0) < 1e-9:
                    # drop this item entirely
                    removed_equal_ones += 1
                    modified = True
                    # ensure if there was a leading comma, keep nothing
                    # We'll clean stray commas later
                else:
                    # keep the matched substring
                    rebuilt.append(inside[im.start():im.end()])
                    kept_not_ones += 1
                cursor = im.end()
            rebuilt.append(inside[cursor:])
            new_inside = "".join(rebuilt)

            # Normalize commas/spaces
            new_inside = self._clean_style(new_inside)
            # Remove duplicate commas again after cleanup
            new_inside = re.sub(r",\s*,", ", ", new_inside)
            new_inside = self._clean_style(new_inside)

            if new_inside != inside:
                modified = True

            # Drop empty []
            if new_inside == "":
                modified_segments += 1 if modified else 0
                return prefix  # remove the [] entirely

            if modified:
                modified_segments += 1
                return f"{prefix}[{new_inside}]"
            return m.group(0)

        processed = self.DRAW_CMD_RE.sub(repl_draw, tikz_code)

        # Clean spaces left by removed []: e.g., "\\draw  (.." -> keep as is
        # Also remove leftover sequences like "[]" if any slipped through
        processed = processed.replace("[]", "")

        stats = {
            'removed_equal_ones': removed_equal_ones,
            'kept_not_ones': kept_not_ones,
            'modified_draw_segments': modified_segments,
        }
        logger.debug(f"Opacity post-processing completed: {stats}")
        return {
            'processed_code': processed,
            'conversion_stats': stats,
        }

