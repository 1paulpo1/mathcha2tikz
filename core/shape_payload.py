"""
Common shape typing contracts used across the pipeline.

- ShapePayload: Protocol describing the minimal attributes a shape record
  should expose when passed from Detector to Processor/Renderer.

This is intentionally light-weight and matches what Detector currently
produces (SimpleNamespace) while allowing dict-like records to be used.
"""
from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable


@runtime_checkable
class ShapePayload(Protocol):
    """Minimal contract for shape records flowing through the pipeline.

    Attributes are optional: processors use getattr() to read them.
    """

    # Identifier and type
    id: Optional[str]
    shape_type: Optional[str]

    # Raw textual content
    annotation: Optional[str]
    raw_block: Optional[str]
    raw_command: Optional[str]

    # Optional raw sub-parts produced by Parser/Detector
    raw_shape_data: Optional[str]
    raw_arrows_data: Optional[str]
