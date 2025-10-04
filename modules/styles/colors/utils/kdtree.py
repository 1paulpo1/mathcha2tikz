"""
K-D Tree for Color Search

Provides efficient nearest neighbor search for color matching.
"""

import numpy as np
from typing import List, Tuple, Optional, Dict
from .color_base import COLOR_DEFINITIONS


class ColorKDTree:
    """
    K-D Tree implementation for efficient color search in RGB space.
    
    This provides O(log n) average case lookup time for finding
    the closest named color to a given RGB value.
    """
    
    def __init__(self, colors: Optional[Dict[str, str]] = None):
        """
        Initialize the K-D tree with color definitions.
        
        Args:
            colors: Dictionary of color names to RGB definitions
        """
        self.colors = colors or COLOR_DEFINITIONS
        self.root = None
        self._build_tree()
    
    def _extract_rgb(self, color_def: str) -> Optional[Tuple[float, float, float]]:
        """
        Extract RGB values from a color definition string.
        
        Args:
            color_def: Color definition string like "\\definecolor{Name}{rgb}{r, g, b}"
            
        Returns:
            RGB tuple or None if parsing fails
        """
        import re
        match = re.search(r'rgb}{([\d.]+), ([\d.]+), ([\d.]+)}', color_def)
        if match:
            return (
                float(match.group(1)),
                float(match.group(2)), 
                float(match.group(3))
            )
        return None
    
    def _build_tree(self):
        """Build the K-D tree from color definitions."""
        color_data = []
        
        for name, definition in self.colors.items():
            rgb = self._extract_rgb(definition)
            if rgb:
                color_data.append((name, rgb))
        
        if color_data:
            self.root = self._build_recursive(color_data, depth=0)
    
    def _build_recursive(self, points: List[Tuple[str, Tuple[float, float, float]]], 
                        depth: int) -> Optional['KDNode']:
        """
        Recursively build the K-D tree.
        
        Args:
            points: List of (name, rgb) tuples
            depth: Current depth in the tree
            
        Returns:
            Root node of the subtree
        """
        if not points:
            return None
        
        # Choose axis based on depth (0=R, 1=G, 2=B)
        axis = depth % 3
        
        # Sort points by the current axis
        points.sort(key=lambda x: x[1][axis])
        
        # Find median
        median_idx = len(points) // 2
        median_name, median_rgb = points[median_idx]
        
        # Create node
        node = KDNode(median_name, median_rgb)
        
        # Recursively build left and right subtrees
        left_points = points[:median_idx]
        right_points = points[median_idx + 1:]
        
        node.left = self._build_recursive(left_points, depth + 1)
        node.right = self._build_recursive(right_points, depth + 1)
        
        return node
    
    def find_nearest(self, target_rgb: Tuple[float, float, float]) -> Optional[str]:
        """
        Find the nearest color name to the target RGB value.
        
        Args:
            target_rgb: Target RGB values as (r, g, b) tuple
            
        Returns:
            Name of the closest color or None if tree is empty
        """
        if not self.root:
            return None
        
        best_distance = float('inf')
        best_name = None
        
        def search_recursive(node: Optional['KDNode'], depth: int):
            nonlocal best_distance, best_name
            
            if not node:
                return
            
            # Calculate distance to current node
            current_distance = self._rgb_distance(target_rgb, node.rgb)
            
            if current_distance < best_distance:
                best_distance = current_distance
                best_name = node.name
            
            # Choose axis
            axis = depth % 3
            
            # Determine which subtree to search first
            if target_rgb[axis] < node.rgb[axis]:
                first_subtree = node.left
                second_subtree = node.right
            else:
                first_subtree = node.right
                second_subtree = node.left
            
            # Search the closer subtree first
            search_recursive(first_subtree, depth + 1)
            
            # Check if we need to search the other subtree
            axis_distance = abs(target_rgb[axis] - node.rgb[axis])
            if axis_distance < best_distance:
                search_recursive(second_subtree, depth + 1)
        
        search_recursive(self.root, 0)
        return best_name
    
    def _rgb_distance(self, rgb1: Tuple[float, float, float], 
                     rgb2: Tuple[float, float, float]) -> float:
        """
        Calculate Euclidean distance between two RGB values.
        
        Args:
            rgb1: First RGB tuple
            rgb2: Second RGB tuple
            
        Returns:
            Euclidean distance
        """
        return np.linalg.norm(np.array(rgb1) - np.array(rgb2))


class KDNode:
    """Node in the K-D tree."""
    
    def __init__(self, name: str, rgb: Tuple[float, float, float]):
        """
        Initialize a K-D tree node.
        
        Args:
            name: Color name
            rgb: RGB values
        """
        self.name = name
        self.rgb = rgb
        self.left: Optional['KDNode'] = None
        self.right: Optional['KDNode'] = None 