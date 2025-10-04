"""
Vector Analysis Module: Vector operations and transformations
- Vector arithmetic
- Vector properties
- Coordinate transformations
- Projections and reflections
"""

import math
import numpy as np
from typing import Tuple

from utils.geometry import point_path_operations

# Basic vector operations
def vector_add(v1: Tuple[float, float], v2: Tuple[float, float]) -> Tuple[float, float]:
    return (v1[0] + v2[0], v1[1] + v2[1])

def vector_subtract(v1: Tuple[float, float], v2: Tuple[float, float]) -> Tuple[float, float]:
    return (v1[0] - v2[0], v1[1] - v2[1])

def vector_scale(vec: Tuple[float, float], scalar: float) -> Tuple[float, float]:
    return (vec[0] * scalar, vec[1] * scalar)

def dot_product(v1: Tuple[float, float], v2: Tuple[float, float]) -> float:
    return v1[0]*v2[0] + v1[1]*v2[1]

def cross_product(v1: Tuple[float, float], v2: Tuple[float, float]) -> float:
    return v1[0]*v2[1] - v1[1]*v2[0]

def vector_length(vec: Tuple[float, float]) -> float:
    return math.sqrt(vec[0]**2 + vec[1]**2)

def normalize(vec: Tuple[float, float]) -> Tuple[float, float]:
    length = vector_length(vec)
    if length < 1e-10:
        return (0.0, 0.0)
    return (vec[0]/length, vec[1]/length)

# Vector properties
def vector_from_line(
    start: tuple, 
    end: tuple, 
    canvas_height: float
) -> tuple:
    """
    Calculate direction vector with coordinate conversion
    """
    start_std = point_path_operations.convert_coordinates(start, canvas_height)
    end_std = point_path_operations.convert_coordinates(end, canvas_height)
    return (end_std[0] - start_std[0], end_std[1] - start_std[1])

def vector_from_angle(angle_degrees: float) -> Tuple[float, float]:
    rad = math.radians(angle_degrees)
    return (math.cos(rad), math.sin(rad))

def angle_from_vector(vec: Tuple[float, float]) -> float:
    return math.degrees(math.atan2(vec[1], vec[0])) % 360

def angle_between_vectors(v1: Tuple[float, float], v2: Tuple[float, float]) -> float:
    cos_angle = dot_product(normalize(v1), normalize(v2))
    return math.degrees(math.acos(max(-1.0, min(1.0, cos_angle))))

def is_parallel(v1: Tuple[float, float], v2: Tuple[float, float], tol: float = 1e-6) -> bool:
    return abs(cross_product(v1, v2)) < tol

def is_perpendicular(v1: Tuple[float, float], v2: Tuple[float, float], tol: float = 1e-6) -> bool:
    return abs(dot_product(v1, v2)) < tol

# Transformations
def rotate_point(point: Tuple[float, float], center: Tuple[float, float], angle_deg: float) -> Tuple[float, float]:
    x, y = point[0]-center[0], point[1]-center[1]
    rad = math.radians(angle_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    return (
        x*cos_a - y*sin_a + center[0],
        x*sin_a + y*cos_a + center[1]
    )

def scale_point(point: Tuple[float, float], center: Tuple[float, float], scale_x: float, scale_y: float) -> Tuple[float, float]:
    return (
        center[0] + (point[0]-center[0])*scale_x,
        center[1] + (point[1]-center[1])*scale_y
    )

def reflect_point(point: Tuple[float, float], line_start: Tuple[float, float], line_end: Tuple[float, float]) -> Tuple[float, float]:
    dx, dy = vector_subtract(line_end, line_start)
    a = dx*dx + dy*dy
    if a < 1e-10:
        return point
    
    u = ((point[0]-line_start[0])*dx + (point[1]-line_start[1])*dy) / a
    projection = (line_start[0] + u*dx, line_start[1] + u*dy)
    return vector_scale(vector_subtract(projection, point), 2)

# Coordinate systems
def cartesian_to_polar(x: float, y: float) -> Tuple[float, float]:
    return (math.sqrt(x*x + y*y), math.degrees(math.atan2(y, x)))

def polar_to_cartesian(radius: float, angle_deg: float) -> Tuple[float, float]:
    rad = math.radians(angle_deg)
    return (radius * math.cos(rad), radius * math.sin(rad))

# Projections
def vector_projection(vec: Tuple[float, float], onto: Tuple[float, float]) -> Tuple[float, float]:
    onto_unit = normalize(onto)
    scalar = dot_product(vec, onto_unit)
    return vector_scale(onto_unit, scalar)