"""Compatibility wrapper for the `mathcha2tikz` package."""

from .mathcha2tikz import (
    ConfigurationError,
    Converter,
    DetectionError,
    ParserError,
    Pipeline,
    ProcessingError,
    RenderingError,
    __version__,
    convert,
    main,
)

__all__ = [
    "ConfigurationError",
    "Converter",
    "DetectionError",
    "ParserError",
    "Pipeline",
    "ProcessingError",
    "RenderingError",
    "__version__",
    "convert",
    "main",
]
