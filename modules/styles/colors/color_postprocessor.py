"""
Color PostProcessor

Processes colors in the final TikZ code after all shapes have been rendered.
This is more efficient than processing colors for each individual shape.

Architecture:
1. Parse the final TikZ code to find all RGB color specifications
2. Convert RGB colors to named colors using existing algorithms
3. Replace RGB specifications with named colors in the final code
4. Generate color definitions for used colors
"""

import re
from typing import Dict, Any, List, Optional, Tuple
import logging

from .utils.kdtree import ColorKDTree
from .utils.color_base import COLOR_DEFINITIONS
from .utils.color_utils import (
    RGB_PATTERN,
    COLOR_SPEC_PATTERN,
    FILL_COLOR_PATTERN,
    build_rgb_spec_int,
    normalize_rgb_255,
)

logger = logging.getLogger(__name__)


class ColorPostProcessor:
    """
    Post-processor for converting RGB colors to named colors in final TikZ code.
    
    This processor works on the complete TikZ code after all shapes have been rendered,
    making it more efficient than processing colors for each individual shape.
    """
    
    def __init__(self):
        """Initialize the color post-processor."""
        self.kdtree = ColorKDTree(COLOR_DEFINITIONS)
        self.processed_cache = {}  # Cache for processed colors
        self.used_colors = set()  # Track used colors for definitions
        
        # Use shared precompiled regex patterns
        self.rgb_pattern = RGB_PATTERN
        self.color_spec_pattern = COLOR_SPEC_PATTERN
        self.fill_color_pattern = FILL_COLOR_PATTERN
    
    def process(self, tikz_code: str) -> Dict[str, Any]:
        """
        Process colors in the final TikZ code.
        
        Args:
            tikz_code: Complete TikZ code to process
            
        Returns:
            Dictionary containing:
            {
                'processed_code': TikZ code with RGB colors replaced by named colors,
                'color_definitions': LaTeX color definitions for used colors,
                'conversion_stats': Statistics about color conversions,
                'used_colors': Set of used color names
            }
        """
        try:
            logger.debug("Starting color post-processing")
            
            # Find all RGB color specifications
            rgb_colors = self._find_rgb_colors(tikz_code)
            
            if not rgb_colors:
                logger.debug("No RGB colors found in TikZ code")
                return {
                    'processed_code': tikz_code,
                    'color_definitions': '',
                    'conversion_stats': {'total_colors': 0, 'converted_colors': 0},
                    'used_colors': set()
                }
            
            logger.debug(f"Found {len(rgb_colors)} RGB color specifications")
            
            # Convert RGB colors to named colors
            color_conversions = {}
            conversion_stats = {
                'total_colors': len(rgb_colors),
                'converted_colors': 0,
                'cache_hits': 0,
                'new_conversions': 0
            }
            
            for rgb_spec, rgb_tuple in rgb_colors.items():
                if rgb_spec in self.processed_cache:
                    # Use cached result
                    named_color = self.processed_cache[rgb_spec]
                    color_conversions[rgb_spec] = named_color
                    conversion_stats['cache_hits'] += 1
                else:
                    # Convert RGB to named color
                    named_color = self._convert_rgb_to_named(rgb_tuple)
                    color_conversions[rgb_spec] = named_color
                    self.processed_cache[rgb_spec] = named_color
                    conversion_stats['new_conversions'] += 1
                
                conversion_stats['converted_colors'] += 1
                self.used_colors.add(named_color)
            
            # Replace RGB colors in the code
            processed_code = self._replace_colors_in_code(tikz_code, color_conversions)
            
            # Generate color definitions
            color_definitions = self._generate_color_definitions()
            
            logger.debug(f"Color post-processing completed: {conversion_stats}")
            
            return {
                'processed_code': processed_code,
                'color_definitions': color_definitions,
                'conversion_stats': conversion_stats,
                'used_colors': self.used_colors.copy()
            }
            
        except Exception as e:
            logger.error(f"Error in color post-processing: {e}")
            return {
                'processed_code': tikz_code,  # Return original code on error
                'color_definitions': '',
                'conversion_stats': {'error': str(e)},
                'used_colors': set()
            }
    
    def _find_rgb_colors(self, tikz_code: str) -> Dict[str, Tuple[int, int, int]]:
        """
        Find all RGB color specifications in TikZ code.
        
        Args:
            tikz_code: TikZ code to search
            
        Returns:
            Dictionary mapping RGB specifications to RGB tuples
        """
        
        rgb_colors: Dict[str, Tuple[int, int, int]] = {}
        
        # Find color specifications
        color_matches = self.color_spec_pattern.findall(tikz_code)
        for match in color_matches:
            r, g, b = map(int, match)
            rgb_spec = build_rgb_spec_int(r, g, b)
            rgb_colors[rgb_spec] = (r, g, b)
            
            # Also add version with trailing space inside braces (common in TikZ output)
            rgb_spec_with_space = f"{{rgb, 255:red, {r}; green, {g}; blue, {b} }}"
            rgb_colors[rgb_spec_with_space] = (r, g, b)
        
        # Find fill color specifications
        fill_matches = self.fill_color_pattern.findall(tikz_code)
        for match in fill_matches:
            r, g, b = map(int, match)
            rgb_spec = build_rgb_spec_int(r, g, b)
            rgb_colors[rgb_spec] = (r, g, b)
        
        # Find standalone RGB specifications
        rgb_matches = self.rgb_pattern.findall(tikz_code)
        for match in rgb_matches:
            r, g, b = map(int, match)
            rgb_spec = build_rgb_spec_int(r, g, b)
            rgb_colors[rgb_spec] = (r, g, b)
        
        return rgb_colors
    
    def _convert_rgb_to_named(self, rgb_tuple: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to named color using K-D tree.
        
        Args:
            rgb_tuple: RGB values as (r, g, b) tuple
            
        Returns:
            Name of the closest color
        """
        try:
            # Normalize RGB values to 0-1 range
            normalized_rgb = normalize_rgb_255(rgb_tuple)
            
            # Find closest color using K-D tree
            closest_color = self.kdtree.find_nearest(normalized_rgb)
            
            return closest_color
            
        except Exception as e:
            logger.warning(f"Error converting RGB {rgb_tuple} to named color: {e}")
            return 'black'  # Fallback color
    
    def _replace_colors_in_code(self, tikz_code: str, color_conversions: Dict[str, str]) -> str:
        """
        Replace RGB color specifications with named colors in TikZ code.
        
        Args:
            tikz_code: Original TikZ code
            color_conversions: Dictionary mapping RGB specs to named colors
            
        Returns:
            TikZ code with RGB colors replaced
        """
        processed_code = tikz_code
        
        for rgb_spec, named_color in color_conversions.items():
            # Replace color specifications (with or without braces)
            processed_code = processed_code.replace(
                f"color={rgb_spec}",
                f"color = {named_color}"
            )
            processed_code = processed_code.replace(
                f"color={rgb_spec}",
                f"color = {named_color}"
            )
            
            # Replace fill color specifications (with or without braces)
            processed_code = processed_code.replace(
                f"fill={rgb_spec}",
                f"fill = {named_color}"
            )
            processed_code = processed_code.replace(
                f"fill={rgb_spec}",
                f"fill = {named_color}"
            )
            
            # Replace standalone RGB specifications
            processed_code = processed_code.replace(rgb_spec, named_color)
        
        return processed_code
    
    def _generate_color_definitions(self) -> str:
        """
        Generate LaTeX color definitions for used colors.
        
        Returns:
            LaTeX color definitions string
        """
        if not self.used_colors:
            return ""
        
        definitions = []
        for color_name in sorted(self.used_colors):
            if color_name in COLOR_DEFINITIONS:
                definitions.append(COLOR_DEFINITIONS[color_name])
        
        if not definitions:
            return ""
        
        return "% Color definitions\n" + "\n".join(definitions) + "\n\n"
    
    def get_used_colors(self) -> set:
        """Get the set of used colors."""
        return self.used_colors.copy()
    
    def clear_cache(self):
        """Clear the processed color cache."""
        self.processed_cache.clear()
        self.used_colors.clear()
