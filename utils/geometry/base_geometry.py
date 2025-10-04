"""
Base Geometry Module: Fundamental geometric operations
- Distance calculations
- Coordinate parsing and formatting
- Angle operations
- Conic section fitting
"""

import math
import re
import numpy as np
from typing import Tuple, List, Optional

# Distance calculations
def distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

# Coordinate handling
def parse_point(coord_str: str) -> Tuple[float, float]:
    coord_str = coord_str.strip().strip('()')
    parts = coord_str.split(',')
    try:
        return float(parts[0].strip()), float(parts[1].strip())
    except (ValueError, IndexError):
        return (0.0, 0.0)

def parse_coordinates_from_string(s: str) -> List[Tuple[float, float]]:
    pattern = r'\(([^,]+),([^)]+)\)'
    matches = re.findall(pattern, s)
    points = []
    for match in matches:
        try:
            points.append((float(match[0].strip()), float(match[1].strip())))
        except ValueError:
            continue
    return points

def round_coordinates(x: float, y: float, precision: int = 2) -> Tuple[float, float]:
    return (round(x, precision), round(y, precision))

def format_number(value: float, precision: int = 2) -> str:
    return f"{value:.{precision}f}"

# Angle operations
def normalize_angle(angle_degrees: float) -> float:
    normalized = angle_degrees % 360
    return normalized if normalized >= 0 else normalized + 360

def polar_to_parametric(θ_deg: float, a: float, b: float) -> float:
    θ = math.radians(θ_deg)
    if abs(math.cos(θ)) < 1e-10:
        return 90 if math.sin(θ) > 0 else 270
    φ = math.atan2(a * math.sin(θ), b * math.cos(θ))
    return normalize_angle(math.degrees(φ))

def parametric_to_polar(φ_deg: float, a: float, b: float) -> float:
    φ = math.radians(φ_deg)
    θ = math.atan2(b * math.sin(φ), a * math.cos(φ))
    return normalize_angle(math.degrees(θ))

# Conic fitting
def compute_conic_coefficients(points: List[Tuple[float, float]]) -> Optional[Tuple[float, float, float, float, float, float]]:
    if len(points) < 5:
        return None

    M = np.array([[y**2, x*y, x, y, 1] for x, y in points])
    b = -np.array([x**2 for x, y in points])
    
    try:
        s = np.linalg.lstsq(M, b, rcond=None)[0]
        return (1.0, float(s[0]), float(s[1]), float(s[2]), float(s[3]), float(s[4]))
    except np.linalg.LinAlgError:
        return None

def compute_ellipse_params(A: float, B: float, C: float, D: float, E: float, F: float) -> Optional[Tuple[float, float, float, float, float]]:
    discriminant = C**2 - 4*A*B
    if discriminant >= 1e-10:
        return None
    
    try:
        matrix = np.array([[2*A, C], [C, 2*B]])
        x0, y0 = np.linalg.solve(matrix, [-D, -E])
    except np.linalg.LinAlgError:
        return None
    
    F_prime = A*x0**2 + B*y0**2 + C*x0*y0 + D*x0 + E*y0 + F
    if F_prime >= 0:
        return None
    
    if abs(A - B) < 1e-5 and abs(C) < 1e-5:
        theta_rad = 0.0
    else:
        theta_rad = 0.5 * math.atan2(C, A - B)
    
    cos_t, sin_t = math.cos(theta_rad), math.sin(theta_rad)
    A_dash = A*cos_t**2 + C*cos_t*sin_t + B*sin_t**2
    B_dash = A*sin_t**2 - C*cos_t*sin_t + B*cos_t**2
    
    try:
        a = math.sqrt(-F_prime / A_dash)
        b = math.sqrt(-F_prime / B_dash)
    except ValueError:
        return None
    
    if a < b:
        a, b = b, a
        theta_rad += math.pi/2
    
    return (x0, y0, a, b, math.degrees(theta_rad))

def compute_ellipse_type(major: float, minor: float) -> str:
    return "circle" if abs(major - minor) < 1e-5 else "ellipse"