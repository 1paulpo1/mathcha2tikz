"""
Bézier Analysis Module: Bézier curve operations
- Curve evaluation
- Derivative calculations
- Length and curvature
- Control point analysis
"""

import math
from typing import List, Tuple, Optional
from utils.geometry.base_geometry import distance

# Gaussian quadrature constants
GAUSS_NODES = [0.046910077, 0.230765345, 0.5, 0.769234655, 0.953089923]
GAUSS_WEIGHTS = [0.1184634425, 0.2393143352, 0.2844444444, 0.2393143352, 0.1184634425]

# Curve evaluation
def bezier_point_at_t(t: float, points: List[Tuple[float, float]]) -> Tuple[float, float]:
    n = len(points) - 1
    x, y = 0.0, 0.0
    for i, (px, py) in enumerate(points):
        coeff = math.comb(n, i) * (1-t)**(n-i) * t**i
        x += coeff * px
        y += coeff * py
    return (x, y)

# Derivative calculations
def bezier_derivative(t: float, points: List[Tuple[float, float]]) -> Tuple[float, float]:
    n = len(points) - 1
    if n == 0:
        return (0.0, 0.0)
    
    derivative = [0.0, 0.0]
    reduced_points = []
    for i in range(n):
        dx = points[i+1][0] - points[i][0]
        dy = points[i+1][1] - points[i][1]
        reduced_points.append((dx, dy))
    
    for i, (dx, dy) in enumerate(reduced_points):
        coeff = math.comb(n-1, i) * (1-t)**(n-1-i) * t**i
        derivative[0] += n * coeff * dx
        derivative[1] += n * coeff * dy
    
    return (derivative[0], derivative[1])

def bezier_velocity(t: float, points: List[Tuple[float, float]]) -> float:
    dx, dy = bezier_derivative(t, points)
    return math.sqrt(dx*dx + dy*dy)

# Curve properties
def bezier_length(points: List[Tuple[float, float]], steps: int = 50) -> float:
    if len(points) < 2:
        return 0.0
    if len(points) == 2:
        return distance(points[0], points[1])
    
    length = 0.0
    for step in range(steps):
        t = step / steps
        length += bezier_velocity(t, points)

    # Refine with fixed Gaussian nodes (5-point Gauss–Legendre on [0, 1])
    length += sum(
        weight * bezier_velocity(node, points)
        for weight, node in zip(GAUSS_WEIGHTS, GAUSS_NODES)
    )
    return length


def nearest_segment_midpoint(segments: List[List[Tuple[float, float]]], point: Tuple[float, float]) -> Tuple[Optional[int], float, float]:
    """Return the index and local t of the segment whose midpoint is closest to the given point.

    TODO: enhance by evaluating multiple t samples for more accurate placement.
    """
    best: Tuple[Optional[int], float, float] = (None, float('inf'), 0.5)
    for idx, segment in enumerate(segments):
        if len(segment) != 4:
            continue
        mid = bezier_point_at_t(0.5, segment)
        distance = math.hypot(point[0] - mid[0], point[1] - mid[1])
        if distance < best[1]:
            best = (idx, distance, 0.5)
    return best

def bezier_curvature(t: float, points: List[Tuple[float, float]]) -> float:
    if len(points) < 3:
        return 0.0
    
    # First derivative
    dx, dy = bezier_derivative(t, points)
    
    # Second derivative using finite differences
    dt = 0.001
    t1 = max(0, t - dt)
    t2 = min(1, t + dt)
    dx1, dy1 = bezier_derivative(t1, points)
    dx2, dy2 = bezier_derivative(t2, points)
    ddx = (dx2 - dx1) / (2 * dt)
    ddy = (dy2 - dy1) / (2 * dt)
    
    numerator = abs(dx * ddy - dy * ddx)
    denominator = (dx*dx + dy*dy)**1.5
    
    return numerator / denominator if denominator > 1e-10 else 0.0

# Control point analysis
def find_curve_extrema(points: List[Tuple[float, float]]) -> List[float]:
    if len(points) != 4:
        return []
    
    extrema = []
    # X extrema
    ax = 3*(points[1][0] - points[0][0])
    bx = 3*(points[2][0] - 2*points[1][0] + points[0][0])
    cx = points[3][0] - 3*points[2][0] + 3*points[1][0] - points[0][0]
    
    # Y extrema
    ay = 3*(points[1][1] - points[0][1])
    by = 3*(points[2][1] - 2*points[1][1] + points[0][1])
    cy = points[3][1] - 3*points[2][1] + 3*points[1][1] - points[0][1]
    
    for a, b, c in [(ax, bx, cx), (ay, by, cy)]:
        if abs(c) > 1e-10:
            discriminant = b*b - 4*a*c
            if discriminant >= 0:
                sqrt_d = math.sqrt(discriminant)
                t1 = (-b + sqrt_d) / (2*a)
                t2 = (-b - sqrt_d) / (2*a)
                for t in [t1, t2]:
                    if 0 <= t <= 1:
                        extrema.append(t)
        elif abs(b) > 1e-10:
            t = -a / b
            if 0 <= t <= 1:
                extrema.append(t)
    
    return sorted(set(extrema))

def is_curve_closed(points: List[Tuple[float, float]], tolerance: float = 1e-6) -> bool:
    return distance(points[0], points[-1]) < tolerance

def curve_direction(points: List[Tuple[float, float]]) -> str:
    if len(points) < 3:
        return 'unknown'
    
    area = 0
    for i in range(len(points)):
        j = (i+1) % len(points)
        area += points[i][0]*points[j][1] - points[j][0]*points[i][1]
    
    return 'clockwise' if area < 0 else 'counterclockwise' if area > 0 else 'unknown'