"""
Regex pattern caching system for performance optimization.

Caches compiled regex patterns to avoid recompilation overhead.
"""

import logging
import re
from typing import Dict, Pattern, Optional
from functools import lru_cache

# Add a logger for regex errors
regex_logger = logging.getLogger("regex_debug")
regex_logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
regex_logger.addHandler(handler)

import re as _re

def safe_compile(pattern: str, flags: int = 0) -> re.Pattern:
    """Safely compile a regex pattern with error handling."""
    try:
        return re.compile(pattern, flags)
    except re.error as e:
        # If compilation fails, return a pattern that matches nothing
        return re.compile(r'(?!)', flags)

def safe_sub(pattern: re.Pattern, repl: str, string: str, count: int = 0, flags: int = 0) -> str:
    """Safely perform regex substitution with error handling."""
    try:
        return pattern.sub(repl, string, count, flags)
    except re.error as e:
        # If substitution fails, return original string
        return string

class RegexCache:
    """Caches compiled regex patterns for better performance."""
    
    def __init__(self):
        self._cache: Dict[str, Pattern] = {}
    
    def compile(self, pattern: str, flags: int = 0) -> Pattern:
        """
        Compile a regex pattern, using cache if available.
        
        Args:
            pattern: The regex pattern string
            flags: Regex flags (re.IGNORECASE, etc.)
            
        Returns:
            Compiled regex pattern
        """
        cache_key = f"{pattern}:{flags}"
        
        if cache_key not in self._cache:
            self._cache[cache_key] = safe_compile(pattern, flags)
            # Lazy import to avoid circular dependency
            try:
                from utils import performance_monitor
                performance_monitor.record_cache_miss()
            except ImportError:
                pass  # Performance monitoring not available
        else:
            # Lazy import to avoid circular dependency
            try:
                from utils import performance_monitor
                performance_monitor.record_cache_hit()
            except ImportError:
                pass  # Performance monitoring not available
        
        return self._cache[cache_key]
    
    def clear(self):
        """Clear the regex cache."""
        self._cache.clear()
    
    def get_cache_size(self) -> int:
        """Get the number of cached patterns."""
        return len(self._cache)


# Global regex cache instance
regex_cache = RegexCache()


def compile_pattern(pattern: str, flags: int = 0) -> Pattern:
    """
    Compile a regex pattern using the global cache.
    
    Args:
        pattern: The regex pattern string
        flags: Regex flags
        
    Returns:
        Compiled regex pattern
    """
    return regex_cache.compile(pattern, flags)


# Common patterns used throughout the application
class CommonPatterns:
    """Common regex patterns used in the application."""
    
    # TikZ environment patterns
    TIKZ_START = safe_compile(r'\\begin\{tikzpicture\}.*?\n', _re.DOTALL)
    TIKZ_END = safe_compile(r'\\end\{tikzpicture\}', _re.DOTALL)
    COMMENT_LINE = safe_compile(r'%uncomment if require:.*\n')
    EMPTY_LINES = safe_compile(r'\n\s*\n')
    
    # Color patterns
    RGB_COLOR = safe_compile(
        r'(=\s*)({rgb\s*,\s*255\s*:\s*red\s*,\s*(\d+)\s*;\s*green\s*,\s*(\d+)\s*;\s*blue\s*,\s*(\d+)\s*})',
        _re.IGNORECASE
    )
    COLOR_DEFINITION = safe_compile(r'rgb}{([\d.]+), ([\d.]+), ([\d.]+)}')
    
    # Style patterns
    OPACITY_PATTERN = safe_compile(r'(?:draw|fill) opacity\s*=\s*1(,)?\s*')
    STYLE_GROUPS = safe_compile(r'(\[[^]]*\])(?:\s*(\[[^]]*\])\s*)+')
    DASH_PATTERN = safe_compile(r'dash pattern\s*=\s*\{[^}]+\}', _re.IGNORECASE)
    
    # Coordinate patterns
    COORD_CLEAN_PATTERNS = [
        (safe_compile(r'\(\s*'), '('),
        (safe_compile(r'\s*\)'), ')'),
        (safe_compile(r'\s*,\s*'), ', '),
        (safe_compile(r',\s*\]'), ']'),
    ]
    
    # Arrow patterns
    ARROW_PATTERN = safe_compile(
        r'shift\s*=\s*{\([\d\., -]+\)}.*?rotate\s*=\s*[\d.-]+',
        _re.DOTALL
    )
    
    # Line patterns
    STRAIGHT_LINES = safe_compile(r'%Straight Lines \[id:.+\]')
    CURVE_LINES = safe_compile(r'%Curve Lines\s*\[id:.+\]')
    
    # Shape patterns
    ELLIPSE_CIRCLE = safe_compile(r'%Shape: (Ellipse|Circle)')
    ARC_SHAPE = safe_compile(r'%Shape: Arc')
    
    # General patterns
    DRAW_COMMAND = safe_compile(r'\\draw\s*(\[.*?\])?\s*(.*)')
    MULTIPLE_SPACES = safe_compile(r'\s+')
    TRAILING_COMMA = safe_compile(r',\s*]')
    EMPTY_BRACKETS = safe_compile(r'^\s*\\draw\[\s*\]')
    FRACTIONAL_ZEROS = safe_compile(r'(\d+)\.0+(?=\D)')
    DOUBLE_COMMAS = safe_compile(r',\s*,')
    BACKSLASH_EQUALS = safe_compile(r"\\\s*=\s*")
    LEADING_COMMA = safe_compile(r"\[\s*,\s*")
    DUPLICATE_STYLES = safe_compile(r"\b([\w-]+)\b(?:[ ,]+\1\b)+") 