"""
Conic Fitting: Fit ellipses/circles to point data
"""

from .conic_core import parse_input, compute_conic_coefficients, compute_ellipse_params, compute_ellipse_type
from ..point_path_operations import sample_bezier_points

def main(input_str):
    points = parse_input(input_str)
    ellipse_points = sample_bezier_points(points, min_points=5)
    
    if len(ellipse_points) < 5:
        return "Not enough points"
    
    coeffs = compute_conic_coefficients(ellipse_points)
    if not coeffs:
        return "Degenerate system"
    
    params = compute_ellipse_params(*coeffs)
    if not params:
        return "Invalid parameters"
    
    x0, y0, major, minor, rotation = params
    ellipse_type = compute_ellipse_type(major, minor)
    
    return {
        "center": (round(x0, 2), round(y0, 2)),
        "major_axis": round(major, 2),
        "minor_axis": round(minor, 2),
        "rotation": 0.0 if ellipse_type == "circle" else round(rotation, 2),
        "type": ellipse_type
    }