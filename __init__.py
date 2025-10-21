"""Top-level package API for mathcha2tikz (single-root layout).

Exports:
- Converter/convert from core.converter
- Exception types from core.exceptions
- CLI main from CLI.main
- __version__ from __version__
"""

from __future__ import annotations

from .core.converter import Converter, convert
from .core.exceptions import (
    ConfigurationError,
    DetectionError,
    ParserError,
    ProcessingError,
    RenderingError,
)
from .CLI import main
from .__version__ import __version__

# Backward compatibility
Pipeline = Converter

__all__ = [
    "Converter",
    "Pipeline",
    "convert",
    "main",
    "ParserError",
    "DetectionError",
    "ProcessingError",
    "RenderingError",
    "ConfigurationError",
    "__version__",
]
