"""
Conic Arc: Convert Bézier paths to conic arcs
"""

import math
from .conic_core import parse_input, compute_conic_coefficients, compute_ellipse_params
from .conic_core import sample_bezier_points, normalize_arc_angles, compute_parametric_angle


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
    start_deg = math.degrees(compute_parametric_angle(
        points[0], (x0, y0), major, minor, math.radians(rotation))
    )
    end_deg = math.degrees(compute_parametric_angle(
        points[-1], (x0, y0), major, minor, math.radians(rotation))
    )
    
    start_norm, end_norm, rotation = normalize_arc_angles(start_deg, end_deg, rotation)
    
    # Format output
    if abs(rotation) < 1e-5:
        return f"\\draw ([shift={{({x0:.2f},{y0:.2f})}}] {start_norm:.2f}:{major:.2f} and {minor:.2f}) arc ({start_norm:.2f}:{end_norm:.2f}:{major:.2f} and {minor:.2f});"
    return f"\\draw[rotate around={{{rotation:.2f}:({x0:.2f},{y0:.2f})}}] ([shift={{({x0:.2f},{y0:.2f})}}] {start_norm:.2f}:{major:.2f} and {minor:.2f}) arc ({start_norm:.2f}:{end_norm:.2f}:{major:.2f} and {minor:.2f});"