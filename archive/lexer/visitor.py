"""
Visitor pattern implementation for traversing and processing the AST.
"""
from __future__ import annotations
from typing import Any, TypeVar, Generic, Optional, List, Union
from .ast import *

T = TypeVar('T')

class Visitor(Generic[T]):
    """
    Base visitor class for traversing the AST.
    
    This class implements the visitor pattern for traversing and processing AST nodes.
    To use it, create a subclass and override the visit_* methods for the node types
    you're interested in.
    """
    
    def visit(self, node: Node) -> T:
        """
        Visit a node and return the result of processing it.
        
        Args:
            node: The node to visit
            
        Returns:
            The result of processing the node
            
        Raises:
            ValueError: If an unsupported node type is encountered
        """
        method_name = f'visit_{node.node_type.name.lower()}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node: Node) -> T:
        """
        Default visitor method that is called when no specific visit_* method is found.
        
        Args:
            node: The node to visit
            
        Returns:
            The result of processing the node
            
        Raises:
            ValueError: If an unsupported node type is encountered
        """
        method_name = f'visit_{node.__class__.__name__.lower()}'
        if hasattr(self, method_name):
            return getattr(self, method_name)(node)
        
        # If we get here, no specific visitor method was found
        raise ValueError(f"No visitor method found for {node.__class__.__name__}")
    
    def visit_document(self, node: Document) -> T:
        """Visit a Document node."""
        results = []
        for tikz_picture in node.tikz_pictures:
            results.append(self.visit(tikz_picture))
        return self.aggregate_document_results(results)
    
    def visit_tikzpicture(self, node: TikzPicture) -> T:
        """Visit a TikzPicture node."""
        results = []
        for command in node.commands:
            results.append(self.visit(command))
        return self.aggregate_tikzpicture_results(results)
    
    def visit_command(self, node: Command) -> T:
        """Visit a Command node."""
        result = {
            'name': node.name,
            'options': self.visit(node.options) if node.options else None,
            'path': self.visit(node.path) if node.path else None
        }
        return self.aggregate_command_result(result)
    
    def visit_shape(self, node: Shape) -> T:
        """Visit a Shape node."""
        result = {
            'shape_type': node.shape_type,
            'shape_id': node.shape_id,
            'options': self.visit(node.options) if node.options else None
        }
        return self.aggregate_shape_result(result)
    
    def visit_path(self, node: Path) -> T:
        """Visit a Path node."""
        results = []
        for element in node.elements:
            results.append(self.visit(element))
        return self.aggregate_path_results(results)
    
    def visit_coordinate(self, node: Coordinate) -> T:
        """Visit a Coordinate node."""
        return self.aggregate_coordinate_result((node.x, node.y))
    
    def visit_lineto(self, node: LineTo) -> T:
        """Visit a LineTo node."""
        return self.aggregate_lineto_result(self.visit(node.coordinate))
    
    def visit_curveto(self, node: CurveTo) -> T:
        """Visit a CurveTo node."""
        return self.aggregate_curveto_result(
            self.visit(node.control1),
            self.visit(node.control2),
            self.visit(node.end)
        )
    
    def visit_options(self, node: Options) -> T:
        """Visit an Options node."""
        return self.aggregate_options_result(node.options)
    
    def visit_text(self, node: Text) -> T:
        """Visit a Text node."""
        return self.aggregate_text_result(node.content)
    
    def visit_comment(self, node: Comment) -> T:
        """Visit a Comment node."""
        return self.aggregate_comment_result(node.content)
    
    # Aggregation methods that can be overridden by subclasses
    
    def aggregate_document_results(self, results: List[T]) -> T:
        """Aggregate results from visiting document children."""
        return results[0] if results else None
    
    def aggregate_tikzpicture_results(self, results: List[T]) -> T:
        """Aggregate results from visiting tikzpicture children."""
        return results
    
    def aggregate_command_result(self, result: dict) -> T:
        """Process command node result."""
        return result
    
    def aggregate_shape_result(self, result: dict) -> T:
        """Process shape node result."""
        return result
    
    def aggregate_path_results(self, results: List[T]) -> T:
        """Aggregate results from visiting path children."""
        return results
    
    def aggregate_coordinate_result(self, coord: tuple) -> T:
        """Process coordinate result."""
        return coord
    
    def aggregate_lineto_result(self, coord: T) -> T:
        """Process line-to result."""
        return coord
    
    def aggregate_curveto_result(self, control1: T, control2: T, end: T) -> T:
        """Process curve-to result."""
        return (control1, control2, end)
    
    def aggregate_options_result(self, options: dict) -> T:
        """Process options result."""
        return options
    
    def aggregate_text_result(self, text: str) -> T:
        """Process text result."""
        return text
    
    def aggregate_comment_result(self, comment: str) -> T:
        """Process comment result."""
        return comment
