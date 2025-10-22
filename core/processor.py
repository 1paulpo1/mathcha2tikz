"""Shape Processor Module

Orchestrates shape processing workflow for all supported shape types.
Provides a unified processing framework with plugin architecture.
"""

from typing import Dict, Any, Optional, List, Type, Callable
import logging
import importlib
import inspect
import re
import os
from .exceptions import ProcessingError

# Configure logging
logger = logging.getLogger(__name__)

class ProcessorRegistry:
    """
    Registry for shape processors.
    Provides a centralized mechanism for registering and retrieving shape processors.
    """
    _processors: Dict[str, Type['BaseProcessor']] = {}
    _fallback_processor: Optional[Type['BaseProcessor']] = None

    @staticmethod
    def _normalize_shape_type(shape_type: Optional[str]) -> str:
        """Normalize shape type strings for consistent registry storage and lookup."""

        if not shape_type:
            return "unknown"

        normalized = shape_type.strip().lower()
        # Collapse whitespace or hyphen sequences to a single underscore for stability.
        normalized = re.sub(r"[\s\-]+", "_", normalized)
        return normalized or "unknown"

    @classmethod
    def register(cls, shape_type: str, processor_class: Type['BaseProcessor']):
        """
        Register a processor for a specific shape type.
        
        Args:
            shape_type: The shape type this processor handles
            processor_class: The processor class
        """
        normalized = cls._normalize_shape_type(shape_type)
        cls._processors[normalized] = processor_class
        logger.debug(
            "Registered processor for shape type '%s' (normalized: '%s'): %s",
            shape_type,
            normalized,
            processor_class.__name__,
        )
    
    @classmethod
    def register_fallback(cls, processor_class: Type['BaseProcessor']):
        """
        Register a fallback processor for shapes without a specific processor.
        
        Args:
            processor_class: The processor class to use as fallback
        """
        cls._fallback_processor = processor_class
        logger.debug(f"Registered fallback processor: {processor_class.__name__}")
    
    @classmethod
    def get_processor(cls, shape_type: str) -> Optional[Type['BaseProcessor']]:
        """
        Get the processor for a specific shape type.
        
        Args:
            shape_type: The shape type to get a processor for
            
        Returns:
            The processor class or fallback if not found
        """
        normalized = cls._normalize_shape_type(shape_type)
        processor = cls._processors.get(normalized)
        if not processor and cls._fallback_processor:
            logger.debug(
                "Using fallback processor for shape type '%s' (normalized: '%s')",
                shape_type,
                normalized,
            )
            return cls._fallback_processor
        return processor
    
    @classmethod
    def list_registered_processors(cls) -> List[str]:
        """
        List all registered shape types with processors.
        
        Returns:
            List of registered shape types
        """
        return list(cls._processors.keys())


class BaseProcessor:
    """
    Base class for all shape processors.
    Defines the interface that all processors must implement.
    """
    def __init__(self, shape_instance):
        self.shape_instance = shape_instance
    
    def process(self) -> Dict[str, Any]:
        """
        Process the shape instance.
        
        Returns:
            Dictionary with processed shape data
        """
        raise NotImplementedError("Subclasses must implement process()")
    
    def validate(self) -> bool:
        """
        Validate that the shape instance has all required data.
        
        Returns:
            True if valid, False otherwise
        """
        return True


class RawPassthroughProcessor(BaseProcessor):
    """Fallback processor that returns raw TikZ blocks unchanged."""

    def __init__(self, shape_instance=None):
        super().__init__(shape_instance)

    def process(self, raw_block: str = None) -> Dict[str, Any]:
        shape = self.shape_instance

        # Extract raw content and annotation from either dict or object instances
        if isinstance(shape, dict):
            annotation = shape.get('annotation', '')
            shape_type = shape.get('shape_type', 'unknown')
            shape_id = shape.get('id') or shape.get('shape_id')
            raw_content = raw_block or shape.get('raw_block') or shape.get('raw_command', '')
        else:
            annotation = getattr(shape, 'annotation', '')
            shape_type = getattr(shape, 'shape_type', getattr(shape, 'type', 'unknown'))
            shape_id = getattr(shape, 'id', None)
            raw_content = raw_block or getattr(shape, 'raw_block', '') or getattr(shape, 'raw_command', '')

        annotation_stripped = annotation.strip() if annotation else ''

        cleaned_raw_content = ''
        if raw_content:
            raw_lines = raw_content.splitlines()
            filtered_lines = []
            for line in raw_lines:
                line_stripped = line.strip()
                # Skip duplicate annotation comments inside the raw block
                if annotation_stripped and line_stripped == annotation_stripped:
                    continue
                filtered_lines.append(line)
            cleaned_raw_content = '\n'.join(filtered_lines).strip()

        lines: List[str] = []
        if annotation_stripped:
            lines.append(annotation_stripped)
        if cleaned_raw_content:
            lines.append(cleaned_raw_content)

        tikz_code = '\n'.join(lines)

        return {
            'tikz_code': tikz_code,
            'raw_block': raw_content,
            'annotation': annotation,
            'shape_type': shape_type,
            'id': shape_id,
            'passthrough': True,
        }


class Processor:
    """
    Global processor orchestrates shape processing pipeline.
    Uses the ProcessorRegistry to find appropriate processors for each shape type.
    """
    def __init__(self, shape_instance=None):
        self.shape_instance = shape_instance

    def process(self, shape_instance=None):
        """
        Process a shape instance using the appropriate processor.
        
        Args:
            shape_instance: Shape instance to process (uses self.shape_instance if not provided)
        Returns:
            Processed shape instance
        """
        if shape_instance is None:
            shape_instance = self.shape_instance

        if shape_instance is None:
            raise ProcessingError("No shape instance provided for processing")

        # Determine shape type
        shape_type = self._get_shape_type(shape_instance)
        normalized_shape_type = ProcessorRegistry._normalize_shape_type(shape_type)
        logger.debug(
            "Processing shape of type '%s' (normalized: '%s')",
            shape_type,
            normalized_shape_type,
        )
        processor_class = ProcessorRegistry.get_processor(shape_type)
        logger.debug(
            "Processor lookup: shape_type='%s' (normalized: '%s') -> processor_class=%s",
            shape_type,
            normalized_shape_type,
            processor_class.__name__ if processor_class else None,
        )
        if not processor_class:
            raise ProcessingError(f"No processor registered for shape type '{shape_type}'")

        try:
            processor = processor_class(shape_instance)

            if not processor.validate():
                raise ProcessingError(f"Shape validation failed for type '{shape_type}'")

            raw_block = getattr(shape_instance, 'raw_block', '')
            if not raw_block:
                raw_block = getattr(shape_instance, 'raw_command', '')
                if raw_block:
                    logger.debug("Processor: using 'raw_command' as raw_block for processing")
            annotation = getattr(shape_instance, 'annotation', '')

            full_block = annotation + '\n' + raw_block if annotation and raw_block else raw_block

            result = processor.process(full_block)
            if result is None:
                raise ProcessingError(f"Processor '{processor_class.__name__}' returned no result for type '{shape_type}'")

            if isinstance(result, dict):
                if 'start_point' in result and hasattr(shape_instance, 'start'):
                    shape_instance.start = result['start_point']
                if 'end_point' in result and hasattr(shape_instance, 'end'):
                    shape_instance.end = result['end_point']

            return result
        except ProcessingError as pe:
            raise pe
        except Exception as exc:
            raise ProcessingError(
                f"Error processing shape type '{shape_type}' with processor '{processor_class.__name__}': {exc}"
            ) from exc
    
    def _get_shape_type(self, shape_instance=None) -> str:
        """
        Determine the shape type from the shape instance.
        
        Args:
            shape_instance: Shape instance to analyze (uses self.shape_instance if not provided)
        
        Returns:
            Shape type string
        """
        if shape_instance is None:
            shape_instance = self.shape_instance
            
        if shape_instance is None:
            return "Unknown"
            
        # Try to get shape_type attribute
        if hasattr(shape_instance, 'shape_type'):
            logger.debug(f"Shape type from attribute: {shape_instance.shape_type}")
            return shape_instance.shape_type
        
        # Try to get from class name
        if hasattr(shape_instance, '__class__'):
            class_name = shape_instance.__class__.__name__
            logger.debug(f"Shape type from class name: {class_name}")
            return class_name
        
        # If it's a dict with shape_type
        if isinstance(shape_instance, dict) and 'shape_type' in shape_instance:
            logger.debug(f"Shape type from dict: {shape_instance['shape_type']}")
            return shape_instance['shape_type']
        
        # Default to Unknown
        logger.debug("Shape type defaulting to Unknown")
        return "Unknown"


# Import and register built-in processors
def register_builtin_processors():
    """Register all built-in processors with the registry."""
    try:
        # Import straight line processor
        from modules.shapes.straight.straight_processor import StraightProcessor
        # Import curve line processor
        from modules.shapes.curve.curve_processor import CurveProcessor
        # Import ellipse/circle processor
        from modules.shapes.ellipse.ellipse_processor import EllipseProcessor
        # Import arc processor
        from modules.shapes.arc.arc_processor import ArcProcessor
        
        # Register it with the registry
        ProcessorRegistry.register("StraightLine", StraightProcessor)
        ProcessorRegistry.register("Line", StraightProcessor)  # Alias
        # Curve registrations
        ProcessorRegistry.register("CurveLine", CurveProcessor)
        ProcessorRegistry.register("Curve", CurveProcessor)  # Alias
        # Ellipse/Circle registrations
        ProcessorRegistry.register("EllipseShape", EllipseProcessor)
        ProcessorRegistry.register("Ellipse", EllipseProcessor)
        ProcessorRegistry.register("Circle", EllipseProcessor)
        # Arc registrations
        ProcessorRegistry.register("ArcShape", ArcProcessor)
        ProcessorRegistry.register("Arc", ArcProcessor)
        ProcessorRegistry.register("arc", ArcProcessor)  # lowercase for detector compatibility
        
        # Register other built-in processors here
        # ...

        # Fallback processor to passthrough unknown shapes
        ProcessorRegistry.register_fallback(RawPassthroughProcessor)

        logger.debug("Built-in processors registered successfully")
    except ImportError as e:
        logger.warning(f"Could not import built-in processors: {e}")

_BUILTIN_PROCESSORS_REGISTERED = False


def ensure_builtin_processors_registered() -> None:
    """Ensure built-in processors are registered exactly once per process."""

    global _BUILTIN_PROCESSORS_REGISTERED
    if not _BUILTIN_PROCESSORS_REGISTERED:
        register_builtin_processors()
        _BUILTIN_PROCESSORS_REGISTERED = True

# Alias for backward compatibility
GlobalProcessor = Processor