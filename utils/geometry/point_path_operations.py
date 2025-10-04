"""
Path Utilities Module: Path manipulation and analysis
- Bézier path segmentation
- Point sampling
- Arc angle normalization
- Arrow type determination
"""

import math
from typing import List, Tuple, Optional
from .base_geometry import distance, normalize_angle
from .bezier_analysis import bezier_derivative

# Bézier path operations
def split_bezier_into_segments(points_list: List[Tuple[float, float]]) -> List[List[Tuple[float, float]]]:
    segments = []
    for i in range(0, len(points_list) - 1, 3):
        if i + 3 < len(points_list):
            segments.append(points_list[i:i+4])
    return segments


def project_point_on_segment(point: Tuple[float, float], start: Tuple[float, float], end: Tuple[float, float]) -> float:
    """Return normalized projection position t in [0,1] for a point on a segment."""
    vx, vy = end[0] - start[0], end[1] - start[1]
    seg_len_sq = vx * vx + vy * vy
    if seg_len_sq <= 1e-12:
        return 0.0
    px, py = point[0] - start[0], point[1] - start[1]
    t = (px * vx + py * vy) / seg_len_sq
    return max(0.0, min(1.0, t))

def get_ellipse_points_from_bezier(segments: List[List[Tuple[float, float]]]) -> List[Tuple[float, float]]:
    ellipse_points = []
    if not segments:
        return ellipse_points
    
    ellipse_points.append(segments[0][0])
    for segment in segments:
        if len(segment) < 4:
            continue
        P0, P1, P2, P3 = segment
        ellipse_points.append(P3)
        t = 0.5
        x = (1-t)**3*P0[0] + 3*(1-t)**2*t*P1[0] + 3*(1-t)*t**2*P2[0] + t**3*P3[0]
        y = (1-t)**3*P0[1] + 3*(1-t)**2*t*P1[1] + 3*(1-t)*t**2*P2[1] + t**3*P3[1]
        ellipse_points.append((x, y))
    return ellipse_points

def sample_bezier_points(points_list: List[Tuple[float, float]], min_points: int = 5) -> List[Tuple[float, float]]:
    segments = split_bezier_into_segments(points_list)
    points = get_ellipse_points_from_bezier(segments)
    
    if len(points) >= min_points:
        return points
    
    # Add more points if needed
    for segment in segments:
        if len(segment) < 4:
            continue
        t = 0.5
        x = sum(c * w for c, w in zip(
            [p[0] for p in segment],
            [(1-t)**3, 3*(1-t)**2*t, 3*(1-t)*t**2, t**3]
        ))
        y = sum(c * w for c, w in zip(
            [p[1] for p in segment],
            [(1-t)**3, 3*(1-t)**2*t, 3*(1-t)*t**2, t**3]
        ))
        points.append((x, y))
        if len(points) >= min_points:
            break
    return points

# Arc handling
def normalize_arc_angles(
    start_deg: float, 
    end_deg: float, 
    rotation_deg: float
) -> Tuple[float, float, float]:
    # Handle 180° rotation special case
    if abs(rotation_deg - 180) < 0.5 or abs(rotation_deg + 180) < 0.5:
        rotation_deg = 0.0
        start_deg -= 180
        end_deg -= 180
    
    # Normalize start angle
    start_norm = normalize_angle(start_deg)
    
    # Prefer negative angles when close to -180°
    if start_norm > 180 and start_norm < 360:
        start_norm -= 360
    
    # Ensure end angle is greater than start
    if end_deg < start_norm:
        end_deg += 360
    
    # Handle full circle case
    if abs(end_deg - start_norm - 360) < 0.1:
        end_deg = start_norm + 360
    
    return (start_norm, end_deg, rotation_deg)

# Arrow determination
def get_tangent_at_point(points: List[Tuple[float, float]], t: float) -> Tuple[float, float]:
    return bezier_derivative(t, points)

def get_normal_at_point(points: List[Tuple[float, float]], t: float) -> Tuple[float, float]:
    dx, dy = bezier_derivative(t, points)
    length = math.sqrt(dx*dx + dy*dy)
    return (-dy/length, dx/length) if length > 1e-10 else (0, 0)

def convert_coordinates(point: tuple, canvas_height: float) -> tuple:
    """
    Convert Mathcha coordinates (Y-down) to standard coordinates (Y-up)
    """
    x, y = point
    return (x, canvas_height - y)

def determine_arrow_type(
    tangent: Tuple[float, float], 
    rotation_deg: float,
    is_end_arrow: bool = False,
    tol: float = 15.0
) -> str:
    """
    Определение типа стрелки без преобразования координат
    
    Args:
        tangent: Касательный вектор (dx, dy) в системе Mathcha (Y-down)
        rotation_deg: Угол поворота стрелки из Mathcha
        is_end_arrow: Флаг, является ли стрелка конечной
        tol: Допустимое отклонение угла
        
    Returns:
        Символ TikZ для стрелки: '>' или '<'
    """
    dx, dy = tangent
    # Рассчет угла направления линии (Y-down)
    base_angle = math.degrees(math.atan2(dy, dx)) % 360
    
    # Определяем ожидаемый угол для стрелки
    if is_end_arrow:
        expected_angle = base_angle
    else:
        expected_angle = (base_angle + 180) % 360
    
    # Вычисляем минимальную разницу углов
    diff = abs(rotation_deg - expected_angle)
    min_diff = min(diff, 360 - diff)
    
    # Определяем тип стрелки
    if min_diff < tol:
        return '<' if is_end_arrow else '>'
    else:
        return '>' if is_end_arrow else '<'
        
def angle_difference(a: float, b: float) -> float:
    diff = abs(a - b)
    return min(diff, 360 - diff)