"""Compatibility shim for id utilities inside the mathcha2tikz package.

Re-exports build_id_header from the top-level utils package so that
`from mathcha2tikz.utils.id_utils import build_id_header` works.
"""

from __future__ import annotations

from utils.id_utils import build_id_header  # noqa: F401

__all__ = ["build_id_header"]
