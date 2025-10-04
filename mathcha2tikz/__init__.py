"""Top-level package exports for mathcha2tikz."""

from core.converter import Converter, convert
from core.exceptions import (
    ConfigurationError,
    DetectionError,
    ParserError,
    ProcessingError,
    RenderingError,
)

from .cli import main

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
]

__version__ = "0.1.0"
