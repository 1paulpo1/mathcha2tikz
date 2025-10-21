"""Compatibility shim for style utilities inside the mathcha2tikz package.

Re-exports helpers from the top-level utils package so that
`from mathcha2tikz.utils.style_utils import ...` works in modules.
"""
from __future__ import annotations

# Re-export public helpers used by renderers/parsers
from utils.style_utils import (  # noqa: F401
    STYLE_BLOCK_PATTERN,
    apply_arrow_styles,
    append_style_token,
    format_number,
    merge_style_str_with_dict,
    parse_style_blocks,
    split_style_parts,
    style_dict_to_str,
)

__all__ = [
    "STYLE_BLOCK_PATTERN",
    "apply_arrow_styles",
    "append_style_token",
    "format_number",
    "merge_style_str_with_dict",
    "parse_style_blocks",
    "split_style_parts",
    "style_dict_to_str",
]
