"""Top-level package exports for mathcha2tikz."""

from core.converter import Converter, convert
from core.exceptions import (
    ConfigurationError,
    DetectionError,
    ParserError,
    ProcessingError,
    RenderingError,
)

from .CLI import main
from .__version__ import __version__

# Backward compatibility for older imports
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
