"""
Shape Registry Module

Provides a centralized registry for shape handlers and processors.
"""
from typing import Dict, Type, Any, List, Callable, Optional
import logging

logger = logging.getLogger(__name__)

class ShapeRegistry:
    """
    Registry for shape handlers and processors.
    Provides a centralized mechanism for registering and retrieving shape handlers.
    """
    _shape_handlers: Dict[str, Type[Any]] = {}
    _shape_aliases: Dict[str, str] = {}
    _shape_post_processors: Dict[str, List[Callable]] = {}
    
    @classmethod
    def register_shape(cls, shape_type: str, handler_class: Type[Any], aliases: List[str] = None):
        """
        Register a shape handler class for a specific shape type.
        
        Args:
            shape_type: The canonical name of the shape type
            handler_class: The class that handles this shape type
            aliases: Alternative names for this shape type
        """
        cls._shape_handlers[shape_type] = handler_class
        if aliases:
            for alias in aliases:
                cls._shape_aliases[alias] = shape_type
        logger.debug(f"Registered shape handler for {shape_type}")
    
    @classmethod
    def register_post_processor(cls, shape_type: str, processor: Callable):
        """
        Register a post-processing function for a specific shape type.
        
        Args:
            shape_type: The shape type to apply this processor to
            processor: A function that takes a shape instance and modifies it
        """
        if shape_type not in cls._shape_post_processors:
            cls._shape_post_processors[shape_type] = []
        cls._shape_post_processors[shape_type].append(processor)
        logger.debug(f"Registered post-processor for {shape_type}")
    
    @classmethod
    def get_handler(cls, shape_type: str) -> Optional[Type[Any]]:
        """
        Get the handler class for a specific shape type.
        
        Args:
            shape_type: The shape type to get a handler for
            
        Returns:
            The handler class or None if not found
        """
        # Check if this is an alias
        canonical_type = cls._shape_aliases.get(shape_type, shape_type)
        return cls._shape_handlers.get(canonical_type)
    
    @classmethod
    def get_post_processors(cls, shape_type: str) -> List[Callable]:
        """
        Get all post-processors for a specific shape type.
        
        Args:
            shape_type: The shape type to get post-processors for
            
        Returns:
            List of post-processor functions
        """
        canonical_type = cls._shape_aliases.get(shape_type, shape_type)
        return cls._shape_post_processors.get(canonical_type, [])
    
    @classmethod
    def resolve_shape_type(cls, name: str) -> Optional[str]:
        """Resolve canonical shape type for a provided name using aliases and handlers."""
        if not name:
            return None
        normalized = name.strip().lower()
        for candidate in cls._generate_name_variants(normalized):
            if candidate in cls._shape_handlers:
                return candidate
            if candidate in cls._shape_aliases:
                return cls._shape_aliases[candidate]
        return None

    @staticmethod
    def _generate_name_variants(name: str) -> List[str]:
        variants: List[str] = []
        transformations = (
            lambda value: value,
            lambda value: value.replace(" ", "_"),
            lambda value: value.replace(" ", ""),
            lambda value: value.replace("_", ""),
        )
        for transform in transformations:
            variant = transform(name)
            if variant and variant not in variants:
                variants.append(variant)
        return variants

    @classmethod
    def list_registered_shapes(cls) -> List[str]:
        """
        List all registered shape types.
        
        Returns:
            List of registered shape types
        """
        return list(cls._shape_handlers.keys())

    @classmethod
    def clear(cls) -> None:
        """Clear all registered handlers, aliases, and post-processors."""

        cls._shape_handlers.clear()
        cls._shape_aliases.clear()
        cls._shape_post_processors.clear()
