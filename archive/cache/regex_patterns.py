"""
Regex Pattern Manager

Centralizes common regex patterns and substitution operations
to reduce code duplication across the codebase.
"""

import re
from typing import Dict, List, Tuple, Callable, Any
from utils.maintenance.error_handling import error_handler


class RegexPatternManager:
    """
    Centralized manager for regex patterns and operations.
    """
    
    def __init__(self):
        """Initialize the regex pattern manager."""
        self.patterns = self._initialize_patterns()
        self.substitutions = self._initialize_substitutions()
    
    def _initialize_patterns(self) -> Dict[str, re.Pattern]:
        """Initialize common regex patterns."""
        return {
            # TikZ environment patterns
            'tikz_start': re.compile(r'\\begin\{tikzpicture\}.*?\n', re.DOTALL),
            'tikz_end': re.compile(r'\\end\{tikzpicture\}', re.DOTALL),
            'comment_line': re.compile(r'%uncomment if require:.*\n'),
            'empty_lines': re.compile(r'\n\s*\n'),
            
            # Color patterns
            'rgb_color': re.compile(
                r'(=\s*)({rgb\s*,\s*255\s*:\s*red\s*,\s*(\d+)\s*;\s*green\s*,\s*(\d+)\s*;\s*blue\s*,\s*(\d+)\s*})',
                re.IGNORECASE
            ),
            'color_definition': re.compile(r'rgb}{([\d.]+), ([\d.]+), ([\d.]+)}'),
            
            # Style patterns
            'opacity_pattern': re.compile(r'(?:draw|fill) opacity\s*=\s*1(,)?\s*'),
            'style_groups': re.compile(r'(\[[^]]*\])(?:\s*(\[[^]]*\])\s*)+'),
            'dash_pattern': re.compile(r'dash pattern\s*=\s*\{[^}]+\}', re.IGNORECASE),
            
            # Coordinate patterns
            'coord_clean': [
                (re.compile(r'\(\s*'), '('),
                (re.compile(r'\s*\)'), ')'),
                (re.compile(r'\s*,\s*'), ', '),
                (re.compile(r',\s*\]'), ']'),
            ],
            
            # Arrow patterns
            'arrow_pattern': re.compile(
                r'shift\s*=\s*{\([\d\., -]+\)}.*?rotate\s*=\s*[\d.-]+',
                re.DOTALL
            ),
            
            # Line patterns
            'straight_lines': re.compile(r'%Straight Lines \[id:.+\]'),
            'curve_lines': re.compile(r'%Curve Lines\s*\[id:.+\]'),
            
            # Shape patterns
            'ellipse_circle': re.compile(r'%Shape: (Ellipse|Circle)'),
            'arc_shape': re.compile(r'%Shape: Arc'),
            
            # General patterns
            'draw_command': re.compile(r'\\draw\s*(\[.*?\])?\s*(.*)'),
            'multiple_spaces': re.compile(r'\s+'),
            'trailing_comma': re.compile(r',\s*]'),
            'empty_brackets': re.compile(r'^\s*\\draw\[\s*\]'),
            'fractional_zeros': re.compile(r'(\d+)\.0+(?=\D)'),
            'double_commas': re.compile(r',\s*,'),
            'backslash_equals': re.compile(r"\\\s*=\s*"),
            
            # Arrow style patterns
            'arrow_indicators': [
                re.compile(r'->'),
                re.compile(r'<-'),
                re.compile(r'<->'),
                re.compile(r'->>'),
                re.compile(r'<<-'),
                re.compile(r'>>'),
                re.compile(r'<<')
            ],
            
            # Bracket cleaning patterns
            'bracket_cleanup': [
                (re.compile(r'\[\s*,\s*'), '['),
                (re.compile(r',\s*\]'), ']'),
                (re.compile(r'\[\s*,\s*\]'), '[]'),
                (re.compile(r'\[\s*([a-zA-Z]+)\s*\]'), r'[\1]'),
                (re.compile(r'\[\s*\]'), '[]'),
            ]
        }
    
    def _initialize_substitutions(self) -> Dict[str, List[Tuple[str, str]]]:
        """Initialize common substitution patterns."""
        return {
            'coordinate_cleaning': [
                (r'\(\s*', '('),
                (r'\s*\)', ')'),
                (r'\s*,\s*', ', '),
                (r',\s*\]', ']'),
            ],
            'bracket_cleaning': [
                (r'\[\s*,\s*', '['),
                (r',\s*\]', ']'),
                (r'\[\s*,\s*\]', '[]'),
                (r'\[\s*([a-zA-Z]+)\s*\]', r'[\1]'),
                (r'\[\s*\]', '[]'),
            ],
            'style_cleaning': [
                (r'(?:draw|fill) opacity\s*=\s*1(,)?\s*', ''),
                (r'\s+', ' '),
                (r',\s*,', ','),
            ]
        }
    
    def apply_substitutions(self, text: str, substitution_type: str) -> str:
        """
        Apply a set of substitutions to text.
        
        Args:
            text: Input text
            substitution_type: Type of substitutions to apply
            
        Returns:
            Text with substitutions applied
        """
        if substitution_type not in self.substitutions:
            return text
        
        result = text
        for pattern, replacement in self.substitutions[substitution_type]:
            result = error_handler.safe_regex_sub(
                pattern, replacement, result, 
                f"{substitution_type} substitution"
            )
        
        return result
    
    def clean_coordinates(self, text: str) -> str:
        """Clean coordinate formatting in text."""
        return self.apply_substitutions(text, 'coordinate_cleaning')
    
    def clean_brackets(self, text: str) -> str:
        """Clean bracket formatting in text."""
        return self.apply_substitutions(text, 'bracket_cleaning')
    
    def clean_styles(self, text: str) -> str:
        """Clean style formatting in text."""
        return self.apply_substitutions(text, 'style_cleaning')
    
    def remove_arrow_indicators(self, text: str) -> str:
        """Remove arrow indicators from text."""
        result = text
        for pattern in self.patterns['arrow_indicators']:
            result = error_handler.safe_regex_sub(
                pattern.pattern, '', result, 
                "arrow indicator removal"
            )
        return result
    
    def find_pattern(self, pattern_name: str, text: str) -> bool:
        """
        Check if a pattern is found in text.
        
        Args:
            pattern_name: Name of the pattern to check
            text: Text to search in
            
        Returns:
            True if pattern is found, False otherwise
        """
        if pattern_name not in self.patterns:
            return False
        
        pattern = self.patterns[pattern_name]
        if isinstance(pattern, list):
            # Handle list of patterns
            return any(p.search(text) for p, _ in pattern)
        else:
            return bool(pattern.search(text))
    
    def extract_matches(self, pattern_name: str, text: str) -> List[str]:
        """
        Extract matches for a pattern from text.
        
        Args:
            pattern_name: Name of the pattern to use
            text: Text to search in
            
        Returns:
            List of matches
        """
        if pattern_name not in self.patterns:
            return []
        
        pattern = self.patterns[pattern_name]
        if isinstance(pattern, list):
            # Handle list of patterns
            matches = []
            for p, _ in pattern:
                matches.extend(p.findall(text))
            return matches
        else:
            return pattern.findall(text)


# Global regex pattern manager instance
regex_patterns = RegexPatternManager() 