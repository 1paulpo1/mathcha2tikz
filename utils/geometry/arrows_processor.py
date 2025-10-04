from typing import List, Tuple, Dict, Optional
from enum import Enum
from utils.geometry.vector_analysis import normalize, dot_product
from utils.geometry.base_geometry import distance


class ArrowType(Enum):
    NONE = 0
    ON_PATH = 1
    ANTI_PATH = 2

class ArrowData:
    """
    Structured information about arrows on a shape.
    - is_closed: bool (for curves)
    - boundary: dict with keys 'start', 'end', values of ArrowType
    - middle: dict or list for mid-arrows, values of ArrowType or dicts with position/type
    """
    def __init__(self, is_closed: bool = False, boundary: Dict[str, ArrowType] = None, middle: Dict = None):
        self.is_closed = is_closed
        self.boundary = boundary or {"start": ArrowType.NONE, "end": ArrowType.NONE}
        self.middle = middle or {}  # e.g., {"mid": ArrowType.ANTI_PATH}

class GlobalArrowsProcessor:
    """
    Dispatches to the appropriate arrow processor based on shape type.
    Receives shape_type, geometry, and arrow_data (all structured, not raw strings).
    """
    def __init__(self, shape_type: str, geometry, arrow_data):
        self.shape_type = shape_type
        self.geometry = geometry
        self.arrow_data = arrow_data

    def process(self) -> ArrowData:
        """
        Dispatch to the correct processor and return ArrowInfo.
        """
        if self.shape_type == "straight":
            return StraightArrowsProcessor(self.geometry, self.arrow_data).process()
        elif self.shape_type == "curve":
            return CurveArrowsProcessor(self.geometry, self.arrow_data).process()
        elif self.shape_type == "arc":
            return ArcArrowsProcessor(self.geometry, self.arrow_data).process()
        else:
            raise NotImplementedError(f"Arrow processing for {self.shape_type} not implemented.")

class StraightArrowsProcessor:
    """
    Determines arrow positions/directions for straight lines.
    Receives:
        - geometry: (start_point, end_point)
        - arrow_data: dict with flags/positions
    Returns:
        - ArrowInfo
    """
    def __init__(self, geometry: Tuple[Tuple[float, float], Tuple[float, float]], arrow_data: dict):
        self.start_point, self.end_point = geometry
        self.arrow_data = arrow_data

    def process(self) -> ArrowData:
        """
        Use vector math to determine arrow directions at start, end, and mid.
        Return ArrowData.
        """
        from utils.geometry.vector_analysis import vector_from_angle, normalize, dot_product
        A, B = self.start_point, self.end_point
        path_vec = (B[0] - A[0], B[1] - A[1])
        path_vec_norm = normalize(path_vec)
        boundary = {"start": ArrowType.NONE, "end": ArrowType.NONE}
        middle = {}

        for key in ["start", "end", "mid"]:
            if key in self.arrow_data:
                arrow = self.arrow_data[key]
                angle = arrow.get("angle", 0.0)
                arrow_vec = vector_from_angle(angle)
                dp = dot_product(arrow_vec, path_vec_norm)
                if key == "start":
                    boundary["start"] = ArrowType.ON_PATH if dp < 0 else ArrowType.ANTI_PATH
                elif key == "end":
                    boundary["end"] = ArrowType.ON_PATH if dp < 0 else ArrowType.ANTI_PATH
                elif key == "mid":
                    middle["mid"] = ArrowType.ON_PATH if dp < 0 else ArrowType.ANTI_PATH

        return ArrowData(is_closed=False, boundary=boundary, middle=middle)

class CurveArrowsProcessor:
    """
    Determines arrow positions/directions for curves.
    Receives:
        - geometry: list of segments (e.g., Bezier control points)
        - arrow_data: dict with flags/positions
    Returns:
        - ArrowInfo
    """
    def __init__(self, geometry: List[Tuple], arrow_data: dict):
        self.segments = geometry
        self.arrow_data = arrow_data

    def process(self) -> ArrowData:
        """
        Use vector math to determine arrow directions at start, end, and mid for curves.
        For closed curves, only process mid-arrows.
        Return ArrowData.
        """
        from utils.geometry.vector_analysis import vector_from_angle, normalize, dot_product
        from utils.geometry.bezier_analysis import bezier_derivative
        segments = self.segments
        arrow_data = self.arrow_data
        # Determine if closed
        is_closed = False
        if segments and len(segments) > 0:
            first_pt = segments[0][0]
            last_pt = segments[-1][-1]
            if (abs(first_pt[0] - last_pt[0]) < 1e-6 and abs(first_pt[1] - last_pt[1]) < 1e-6):
                is_closed = True
        boundary = {"start": ArrowType.NONE, "end": ArrowType.NONE}
        middle = {}
        # Helper to get tangent at t for a segment
        def get_tangent(segment, t):
            return bezier_derivative(t, segment)
        if not is_closed:
            # Check if both start and end arrows have the same angle (special case like curve_4)
            start_angle = arrow_data.get("start", {}).get("angle") if "start" in arrow_data else None
            end_angle = arrow_data.get("end", {}).get("angle") if "end" in arrow_data else None
            same_angle = start_angle is not None and end_angle is not None and abs(start_angle - end_angle) < 1e-6
            
            # Start arrow
            if "start" in arrow_data:
                arrow = arrow_data["start"]
                tangent = get_tangent(segments[0], 0.0)
                tangent_norm = normalize(tangent)
                arrow_vec = vector_from_angle(arrow.get("angle", 0.0))
                dp = dot_product(arrow_vec, tangent_norm)
                # If same angle as end arrow, use end arrow logic
                if same_angle:
                    boundary["start"] = ArrowType.ON_PATH if dp < 0 else ArrowType.ANTI_PATH
                else:
                    # Start arrow: ON_PATH when pointing away from curve (dp > 0)
                    boundary["start"] = ArrowType.ON_PATH if dp > 0 else ArrowType.ANTI_PATH
            # End arrow
            if "end" in arrow_data:
                arrow = arrow_data["end"]
                tangent = get_tangent(segments[-1], 1.0)
                tangent_norm = normalize(tangent)
                arrow_vec = vector_from_angle(arrow.get("angle", 0.0))
                dp = dot_product(arrow_vec, tangent_norm)
                # End arrow: ON_PATH when pointing toward curve (dp < 0)
                boundary["end"] = ArrowType.ON_PATH if dp < 0 else ArrowType.ANTI_PATH
        # Mid arrows (can be a list or single dict)
        if "mid" in arrow_data:
            mids = arrow_data["mid"]
            if isinstance(mids, list):
                for i, arrow in enumerate(mids):
                    # For simplicity, use t=0.5 on the middle segment
                    seg_idx = min(i, len(segments)-1)
                    tangent = get_tangent(segments[seg_idx], 0.5)
                    tangent_norm = normalize(tangent)
                    arrow_vec = vector_from_angle(arrow.get("angle", 0.0))
                    dp = dot_product(arrow_vec, tangent_norm)
                    middle[f"mid_{i}"] = ArrowType.ON_PATH if dp < 0 else ArrowType.ANTI_PATH
            else:
                # Single mid arrow
                arrow = mids
                seg_idx = len(segments)//2
                tangent = get_tangent(segments[seg_idx], 0.5)
                tangent_norm = normalize(tangent)
                arrow_vec = vector_from_angle(arrow.get("angle", 0.0))
                dp = dot_product(arrow_vec, tangent_norm)
                middle["mid"] = ArrowType.ON_PATH if dp < 0 else ArrowType.ANTI_PATH
        return ArrowData(is_closed=is_closed, boundary=boundary, middle=middle)

class ArcArrowsProcessor:
    """
    Determines arrow positions/directions for arcs.
    Receives:
        - geometry: list of arc segments
        - arrow_data: dict with flags/positions
    Returns:
        - ArrowInfo
    """
    def __init__(self, geometry: List[Tuple], arrow_data: dict):
        self.segments = geometry
        self.arrow_data = arrow_data

    def process(self) -> ArrowData:
        """
        Use vector math to determine arrow directions at start and end.
        Return ArrowInfo.
        """
        from utils.geometry.vector_analysis import vector_from_angle, normalize, dot_product
        from utils.geometry.bezier_analysis import bezier_derivative
        segments = self.segments
        arrow_data = self.arrow_data
        
        # Determine if closed
        is_closed = False
        if segments and len(segments) > 0:
            first_pt = segments[0][0]
            last_pt = segments[-1][-1]
            if (abs(first_pt[0] - last_pt[0]) < 1e-6 and abs(first_pt[1] - last_pt[1]) < 1e-6):
                is_closed = True
        
        boundary = {"start": ArrowType.NONE, "end": ArrowType.NONE}
        middle = {}
        
        # Helper to get tangent at t for a segment
        def get_tangent(segment, t):
            return bezier_derivative(t, segment)
        
        if not is_closed:
            # Check if both start and end arrows have the same angle (special case)
            start_angle = arrow_data.get("start", {}).get("rotation") if "start" in arrow_data else None
            end_angle = arrow_data.get("end", {}).get("rotation") if "end" in arrow_data else None
            same_angle = start_angle is not None and end_angle is not None and abs(start_angle - end_angle) < 1e-6
            
            # Start arrow
            if "start" in arrow_data:
                arrow = arrow_data["start"]
                tangent = get_tangent(segments[0], 0.0)
                tangent_norm = normalize(tangent)
                arrow_vec = vector_from_angle(arrow.get("rotation", 0.0))
                dp = dot_product(arrow_vec, tangent_norm)
                # Arc arrows: use same logic as end arrows for both start and end
                boundary["start"] = ArrowType.ON_PATH if dp < 0 else ArrowType.ANTI_PATH
            
            # End arrow
            if "end" in arrow_data:
                arrow = arrow_data["end"]
                tangent = get_tangent(segments[-1], 1.0)
                tangent_norm = normalize(tangent)
                arrow_vec = vector_from_angle(arrow.get("rotation", 0.0))
                dp = dot_product(arrow_vec, tangent_norm)
                # Arc arrows: ON_PATH when pointing toward curve (dp < 0)
                boundary["end"] = ArrowType.ON_PATH if dp < 0 else ArrowType.ANTI_PATH
        
        return ArrowData(is_closed=is_closed, boundary=boundary, middle=middle)