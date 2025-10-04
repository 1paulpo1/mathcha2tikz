"""
Abstract Syntax Tree (AST) for TikZ document structure.

This module defines the node classes that represent the structure of a TikZ document.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Union, Dict, Any


class NodeType(Enum):
    """Types of AST nodes."""
    DOCUMENT = auto()
    TIKZ_PICTURE = auto()
    COMMAND = auto()
    SHAPE = auto()
    PATH = auto()
    COORDINATE = auto()
    OPTIONS = auto()
    TEXT = auto()
    COMMENT = auto()


@dataclass
class Position:
    """Position in the source code."""
    line: int = 1
    column: int = 1
    end_line: Optional[int] = None
    end_column: Optional[int] = None


@dataclass
class Node:
    """Base class for all AST nodes."""
    node_type: NodeType
    position: Position = field(default_factory=Position)
    parent: Optional[Node] = field(default=None, repr=False)
    
    def __post_init__(self):
        """Set the parent of all child nodes."""
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, Node):
                field_value.parent = self
            elif isinstance(field_value, list):
                for item in field_value:
                    if isinstance(item, Node):
                        item.parent = self
    
    def __str__(self) -> str:
        """Return a string representation of the node."""
        attrs = []
        for field_name, field_value in self.__dict__.items():
            if field_name in ['node_type', 'position', 'parent']:
                continue
            if isinstance(field_value, (str, int, float, bool)) or field_value is None:
                attrs.append(f"{field_name}={field_value!r}")
            elif isinstance(field_value, list):
                attrs.append(f"{field_name}=[{len(field_value)} items]")
            elif isinstance(field_value, dict):
                attrs.append(f"{field_name}={{{len(field_value)} items}}")
            elif isinstance(field_value, Node):
                attrs.append(f"{field_name}={field_value.__class__.__name__}")
            else:
                attrs.append(f"{field_name}={field_value.__class__.__name__}")
        
        return f"{self.__class__.__name__}({', '.join(attrs)})"


@dataclass
class Document(Node):
    """Root node representing the entire TikZ document."""
    def __init__(self, tikz_pictures: List['TikzPicture'] = None, **kwargs):
        super().__init__(node_type=NodeType.DOCUMENT, **kwargs)
        self.tikz_pictures: List[TikzPicture] = tikz_pictures or []


@dataclass
class TikzPicture(Node):
    """Represents a single tikzpicture environment."""
    def __init__(self, commands: List[Union['Command', 'Shape']] = None, **kwargs):
        super().__init__(node_type=NodeType.TIKZ_PICTURE, **kwargs)
        self.commands: List[Union[Command, Shape]] = commands or []


@dataclass
class Command(Node):
    """Represents a TikZ command (e.g., \\draw, \\fill, \\node)."""
    def __init__(self, 
                 name: str, 
                 options: Optional['Options'] = None, 
                 path: Optional['Path'] = None,
                 **kwargs):
        super().__init__(node_type=NodeType.COMMAND, **kwargs)
        self.name: str = name
        self.options: Optional[Options] = options
        self.path: Optional[Path] = path


@dataclass
class Shape(Node):
    """Base class for all shape nodes."""
    def __init__(self, 
                 shape_type: str, 
                 shape_id: Optional[str] = None,
                 options: Optional['Options'] = None,
                 **kwargs):
        super().__init__(node_type=NodeType.SHAPE, **kwargs)
        self.shape_type: str = shape_type
        self.shape_id: Optional[str] = shape_id
        self.options: Optional[Options] = options


@dataclass
class Path(Node):
    """Represents a path in TikZ."""
    def __init__(self, elements: List[Union['PathElement', 'PathOperation']] = None, **kwargs):
        super().__init__(node_type=NodeType.PATH, **kwargs)
        self.elements: List[Union[PathElement, PathOperation]] = elements or []


@dataclass
class PathElement(Node):
    """Base class for path elements."""
    def __init__(self, **kwargs):
        super().__init__(node_type=NodeType.PATH, **kwargs)


@dataclass
class Coordinate(PathElement):
    """Represents a coordinate in TikZ (e.g., (1,2))."""
    def __init__(self, x: float, y: float, **kwargs):
        super().__init__(**kwargs)
        self.x: float = x
        self.y: float = y
        self.node_type = NodeType.COORDINATE


@dataclass
class PathOperation(PathElement):
    """Base class for path operations (e.g., --, .. controls, etc.)."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@dataclass
class LineTo(PathOperation):
    """Represents a line-to operation (--)."""
    def __init__(self, coordinate: Coordinate, **kwargs):
        super().__init__(**kwargs)
        self.coordinate: Coordinate = coordinate
        self.node_type = NodeType.COMMAND  # Or a more specific type if needed


@dataclass
class CurveTo(PathOperation):
    """Represents a curve-to operation (.. controls ... and ... ..)."""
    def __init__(self, 
                 control1: Coordinate, 
                 control2: Coordinate, 
                 end: Coordinate, 
                 **kwargs):
        super().__init__(**kwargs)
        self.control1: Coordinate = control1
        self.control2: Coordinate = control2
        self.end: Coordinate = end
        self.node_type = NodeType.COMMAND  # Or a more specific type if needed


@dataclass
class Options(Node):
    """Represents a set of TikZ options in square brackets."""
    def __init__(self, options: Dict[str, Any] = None, **kwargs):
        super().__init__(node_type=NodeType.OPTIONS, **kwargs)
        self.options: Dict[str, Any] = options or {}


@dataclass
class Text(Node):
    """Represents a text node in TikZ."""
    def __init__(self, content: str, **kwargs):
        super().__init__(node_type=NodeType.TEXT, **kwargs)
        self.content: str = content


@dataclass
class Comment(Node):
    """Represents a comment in the TikZ code."""
    def __init__(self, content: str, **kwargs):
        super().__init__(node_type=NodeType.COMMENT, **kwargs)
        self.content: str = content
