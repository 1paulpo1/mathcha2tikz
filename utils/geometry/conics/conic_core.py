"""
Conic Core: Unified conic operations
- Simplified interface for conic fitting
- Uses base geometry and path utilities
"""

from typing import Tuple
from ..base_geometry import (
    parse_coordinates_from_string as parse_input,
    compute_conic_coefficients,
    compute_ellipse_params,
    compute_ellipse_type
)
from ..point_path_operations import (
    sample_bezier_points,
    normalize_arc_angles
)

def compute_parametric_angle(point: Tuple[float, float], center: Tuple[float, float], 
                           major: float, minor: float, rotation_rad: float) -> float:
    """
    Compute the parametric angle for a point on an ellipse.
    
    Args:
        point: Point on the ellipse
        center: Center of the ellipse
        major: Major axis length
        minor: Minor axis length
        rotation_rad: Rotation angle in radians
        
    Returns:
        Parametric angle in radians
    """
    import math
    
    # Translate point to origin
    x, y = point[0] - center[0], point[1] - center[1]
    
    # Rotate point to align with ellipse axes
    cos_r, sin_r = math.cos(-rotation_rad), math.sin(-rotation_rad)
    x_rot = x * cos_r - y * sin_r
    y_rot = x * sin_r + y * cos_r
    
    # Compute parametric angle
    if abs(x_rot) < 1e-10:
        return math.pi/2 if y_rot > 0 else 3*math.pi/2
    
    angle = math.atan2(y_rot * major, x_rot * minor)
    return angle