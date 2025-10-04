"""
Mathcha to TikZ Converter

This package converts Mathcha TikZ code to processed TikZ output.
"""

# Import core components
from .core.converter import convert, Converter

# Backward-compatible alias
Pipeline = Converter

# Import exceptions
from .core.exceptions import (
    ParserError,
    DetectionError,
    ProcessingError,
    RenderingError,
    ConfigurationError
)

# CLI entry point
from .mathcha2tikz.cli import main

# Import lexer components
from .core.lexer import TikzLexer, TokenType, Token

# Package version
__version__ = "0.1.0"
