"""
DEPRECATED: core.lexer

The lexer has been moved to `utils.lexer` and is considered Experimental.
This module remains as a compatibility shim and re-exports the public API.
"""

from utils.lexer import TikzLexer, TokenType, Token  # type: ignore

__all__ = ["TikzLexer", "TokenType", "Token"]
