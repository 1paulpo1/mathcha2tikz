"""
AST printer for debugging and visualization.

This module provides a visitor that can print a human-readable
representation of the AST.
"""
from typing import List, Optional
from .visitor import Visitor
from .ast import *


class AstPrinter(Visitor[None]):
    """Visitor that prints a human-readable representation of the AST."""
    
    def __init__(self, indent: int = 2):
        """Initialize the printer.
        
        Args:
            indent: Number of spaces to use for indentation
        """
        self.indent = ' ' * indent
        self.level = 0
    
    def _print_indented(self, text: str) -> None:
        """Print text with indentation."""
        print(f"{self.indent * self.level}{text}")
    
    def visit_document(self, node: Document) -> None:
        """Visit a Document node."""
        self._print_indented("Document:")
        self.level += 1
        for tikz_picture in node.tikz_pictures:
            self.visit(tikz_picture)
        self.level -= 1
    
    def visit_tikzpicture(self, node: TikzPicture) -> None:
        """Visit a TikzPicture node."""
        self._print_indented("TikzPicture:")
        self.level += 1
        for command in node.commands:
            self.visit(command)
        self.level -= 1
    
    def visit_command(self, node: Command) -> None:
        """Visit a Command node."""
        self._print_indented(f"Command: {node.name}")
        self.level += 1
        if node.options:
            self.visit(node.options)
        if node.path:
            self.visit(node.path)
        self.level -= 1
    
    def visit_shape(self, node: Shape) -> None:
        """Visit a Shape node."""
        id_str = f" (id: {node.shape_id})" if node.shape_id else ""
        self._print_indented(f"Shape: {node.shape_type}{id_str}")
        self.level += 1
        if node.options:
            self.visit(node.options)
        self.level -= 1
    
    def visit_path(self, node: Path) -> None:
        """Visit a Path node."""
        self._print_indented("Path:")
        self.level += 1
        for element in node.elements:
            if isinstance(element, Coordinate):
                self.visit_coordinate(element)
            elif isinstance(element, LineTo):
                self.visit_lineto(element)
            elif isinstance(element, CurveTo):
                self.visit_curveto(element)
            else:
                self.visit(element)
        self.level -= 1
    
    def visit_coordinate(self, node: Coordinate) -> None:
        """Visit a Coordinate node."""
        self._print_indented(f"Coordinate: ({node.x}, {node.y})")
    
    def visit_lineto(self, node: LineTo) -> None:
        """Visit a LineTo node."""
        self._print_indented("LineTo:")
        self.level += 1
        if hasattr(node, 'coordinate') and node.coordinate is not None:
            if isinstance(node.coordinate, Coordinate):
                self.visit_coordinate(node.coordinate)
            else:
                self.visit(node.coordinate)
        self.level -= 1
    
    def visit_curveto(self, node: CurveTo) -> None:
        """Visit a CurveTo node."""
        self._print_indented("CurveTo:")
        self.level += 1
        
        # Handle control1
        if hasattr(node, 'control1') and node.control1 is not None:
            self._print_indented("Control 1:")
            self.level += 1
            if isinstance(node.control1, Coordinate):
                self.visit_coordinate(node.control1)
            else:
                self.visit(node.control1)
            self.level -= 1
        
        # Handle control2
        if hasattr(node, 'control2') and node.control2 is not None:
            self._print_indented("Control 2:")
            self.level += 1
            if isinstance(node.control2, Coordinate):
                self.visit_coordinate(node.control2)
            else:
                self.visit(node.control2)
            self.level -= 1
        
        # Handle end point
        if hasattr(node, 'end') and node.end is not None:
            self._print_indented("End:")
            self.level += 1
            if isinstance(node.end, Coordinate):
                self.visit_coordinate(node.end)
            else:
                self.visit(node.end)
            self.level -= 1
            
        self.level -= 1
    
    def visit_options(self, node: Options) -> None:
        """Visit an Options node."""
        self._print_indented("Options:")
        self.level += 1
        for key, value in node.options.items():
            if isinstance(value, dict):
                self._print_indented(f"{key}:")
                self.level += 1
                for k, v in value.items():
                    self._print_indented(f"{k}: {v}")
                self.level -= 1
            else:
                self._print_indented(f"{key}: {value}")
        self.level -= 1
    
    def visit_text(self, node: Text) -> None:
        """Visit a Text node."""
        self._print_indented(f"Text: {node.content!r}")
    
    def visit_comment(self, node: Comment) -> None:
        """Visit a Comment node."""
        self._print_indented(f"Comment: {node.content!r}")


def print_ast(node: Node) -> None:
    """Print a human-readable representation of the AST.
    
    Args:
        node: The root node of the AST to print
    """
    printer = AstPrinter()
    printer.visit(node)
