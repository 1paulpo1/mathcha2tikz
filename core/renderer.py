"""TikZ Renderer Module

Handles TikZ code generation for all shape types using a plugin architecture.
Provides a flexible rendering system with registry for shape-specific renderers.
"""

from typing import List, Dict, Any, Type, Optional
import logging
import re
from .exceptions import RenderingError
from .templates import apply_template

# Configure logging
logger = logging.getLogger(__name__)

class RendererRegistry:
    """
    Registry for shape renderers.
    Provides a centralized mechanism for registering and retrieving shape renderers.
    """
    _renderers: Dict[str, Type['BaseRenderer']] = {}
    _fallback_renderer: Optional[Type['BaseRenderer']] = None

    @staticmethod
    def _normalize_shape_type(shape_type: Optional[str]) -> str:
        """Normalize shape type identifiers for consistent registry access."""

        if not shape_type:
            return "unknown"

        normalized = shape_type.strip().lower()
        normalized = re.sub(r"[\s\-]+", "_", normalized)
        return normalized or "unknown"
    
    @classmethod
    def register(cls, shape_type: str, renderer_class: Type['BaseRenderer']):
        """
        Register a renderer for a specific shape type.
        
        Args:
            shape_type: The shape type this renderer handles
            renderer_class: The renderer class
        """
        normalized = cls._normalize_shape_type(shape_type)
        cls._renderers[normalized] = renderer_class
        logger.debug(
            "Registered renderer for shape type '%s' (normalized: '%s'): %s",
            shape_type,
            normalized,
            renderer_class.__name__,
        )
    
    @classmethod
    def register_fallback(cls, renderer_class: Type['BaseRenderer']):
        """
        Register a fallback renderer for shapes without a specific renderer.
        
        Args:
            renderer_class: The renderer class to use as fallback
        """
        cls._fallback_renderer = renderer_class
        logger.debug(f"Registered fallback renderer: {renderer_class.__name__}")
    
    @classmethod
    def get_renderer(cls, shape_type: str) -> Optional[Type['BaseRenderer']]:
        """
        Get the renderer for a specific shape type.
        
        Args:
            shape_type: The shape type to get a renderer for
            
        Returns:
            The renderer class or fallback if not found
        """
        normalized = cls._normalize_shape_type(shape_type)
        renderer = cls._renderers.get(normalized)
        if not renderer and cls._fallback_renderer:
            logger.debug(
                "Using fallback renderer for shape type '%s' (normalized: '%s')",
                shape_type,
                normalized,
            )
            return cls._fallback_renderer
        return renderer
    
    @classmethod
    def list_registered_renderers(cls) -> List[str]:
        """
        List all registered shape types with renderers.
        
        Returns:
            List of registered shape types
        """
        return list(cls._renderers.keys())


class BaseRenderer:
    """
    Base class for all shape renderers.
    Defines the interface that all renderers must implement.
    """
    def __init__(self):
        pass
    
    def render(self, shape_data: Dict[str, Any]) -> str:
        """
        Render shape data to TikZ code.
        
        Args:
            shape_data: Dictionary with shape data
            
        Returns:
            TikZ code string
        """
        raise NotImplementedError("Subclasses must implement render()")


class GlobalRenderer:
    """
    Global renderer orchestrates TikZ code generation for all shape types.
    Uses the RendererRegistry to find appropriate renderers for each shape.
    """
    def __init__(self, processed_shapes=None, config=None):
        self.processed_shapes = processed_shapes or []
        self._renderers_cache = {}
        self._helper_processors = {}
        self.config = config or {}
        self.used_colors = set() # TODO: Analyze purpose of used_colors
        self._initialize_helpers()
    
    def _initialize_helpers(self):
        """Initialize helper processors for special rendering tasks."""
        try:
            from modules.shapes.straight.straight_arrows import StraightArrows
            self._helper_processors['arrows'] = StraightArrows()
        except ImportError as e:
            logger.warning(f"Could not import arrow processor: {e}")
            
    def configure(self, config: dict) -> None:
        """
        Configure the renderer with the provided settings.
        
        Args:
            config: Dictionary of configuration options
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        if not isinstance(config, dict):
            from .exceptions import ConfigurationError
            raise ConfigurationError("Renderer config must be a dictionary")
        self.config = config

    def render(self, processed_shapes: List[Any] = None, mode: str = 'classic') -> str:
        """
        Render all processed shapes to TikZ code.
        
        Args:
            processed_shapes: List of processed shape instances or dictionaries.
                            If None, uses the shapes provided in the constructor.
            mode: Output mode ('classic' or 'obsidian')
            
        Returns:
            str: Complete TikZ code string
        """
        if processed_shapes is not None:
            self.processed_shapes = processed_shapes
            
        if not self.processed_shapes:
            return ""
            
        tikz_code_parts = []
        
        # Add a comment with the mode
        tikz_code_parts.append(f"% Rendered in {mode.capitalize()} mode\n")
        
        # Collect used colors from all shapes
        self.used_colors = set()
        for shape_data in self.processed_shapes:
            if isinstance(shape_data, dict) and 'styles' in shape_data:
                self._collect_colors_from_styles(shape_data['styles'])
            elif hasattr(shape_data, 'styles'):
                self._collect_colors_from_styles(shape_data.styles)
        
        for shape_data in self.processed_shapes:
            # Handle both dictionary and object formats
            if isinstance(shape_data, dict):
                # If it's a dictionary with tikz_code, use it directly
                if 'tikz_code' in shape_data:
                    tikz_code_parts.append(shape_data['tikz_code'])
                    continue
                if 'tikz' in shape_data:
                    tikz_code_parts.append(shape_data['tikz'])
                    continue

                shape = shape_data.get('shape')
                styles = shape_data.get('styles', [])

                if shape is None:
                    # Treat dict itself as the shape payload (e.g. ellipse output)
                    shape = shape_data
            else:
                shape = shape_data
                styles = getattr(shape, 'styles', [])

            if shape is None:
                continue
                
            # Get shape type
            shape_type = self._get_shape_type(shape)
            normalized_shape_type = RendererRegistry._normalize_shape_type(shape_type)

            # Get renderer from registry
            renderer_class = RendererRegistry.get_renderer(shape_type)
            
            if not renderer_class:
                raise RenderingError(f"No renderer registered for shape type '{shape_type}'")

            try:
                if normalized_shape_type not in self._renderers_cache:
                    self._renderers_cache[normalized_shape_type] = renderer_class()
                renderer = self._renderers_cache[normalized_shape_type]

                render_data = self._prepare_render_data(shape, styles, shape_type)

                tikz_code = renderer.render(render_data)
                if isinstance(tikz_code, dict):
                    tikz_code = tikz_code.get('tikz_code', '')
                tikz_code_parts.append(tikz_code)

            except RenderingError:
                raise
            except Exception as exc:
                raise RenderingError(
                    f"Error rendering shape type '{shape_type}' with renderer '{renderer_class.__name__}': {exc}"
                ) from exc
        
        # Join all parts with newlines
        tikz_code = "\n".join(tikz_code_parts)

        # Color post-processing is handled in the main Pipeline after rendering.
        # Intentionally no color transformation here.
        
        # Apply the selected output mode template if available
        if 'apply_template' in globals():
            try:
                tikz_code = apply_template(tikz_code, mode=mode)
            except Exception as e:
                logger.error(f"Error applying {mode} template: {e}")
                # Return the raw TikZ code if template application fails
        
        return tikz_code

    def compose_output(self, color_definitions: str, processed_body: str, mode: str = 'classic') -> str:
        """Собрать итоговый TikZ с учётом выбранного режима."""
        color_definitions = color_definitions or ""
        processed_body = processed_body or ""

        if mode and mode.lower() == 'classic':
            preamble_lines = []
            tikz_lines = []
            in_tikzpicture = False

            for line in processed_body.splitlines():
                stripped = line.strip()
                if stripped.startswith('% copy to preamble') or stripped.startswith('% \\usetikzlibrary') or stripped.startswith('% \\tikzset') or stripped.startswith('% Classic Mode'):
                    preamble_lines.append(line)
                elif stripped.startswith('\\begin{tikzpicture}'):
                    in_tikzpicture = True
                    tikz_lines.append(line)
                elif in_tikzpicture:
                    tikz_lines.append(line)
                else:
                    tikz_lines.append(line)

            parts = []
            if color_definitions:
                parts.append(color_definitions.rstrip())
            if preamble_lines:
                parts.append("\n".join(preamble_lines).rstrip())
            if tikz_lines:
                parts.append("\n".join(tikz_lines).rstrip())

            return "\n".join(part for part in parts if part).rstrip() + "\n"

        return f"{color_definitions}{processed_body}".rstrip() + "\n"
    
    def _prepare_render_data(self, shape, styles, shape_type):
        """Prepare a normalized render payload for the renderer cascade."""

        if isinstance(shape, dict):
            render_data: Dict[str, Any] = dict(shape)
        else:
            render_data = {}
            if hasattr(shape, '__dict__'):
                render_data.update(
                    {
                        key: value
                        for key, value in vars(shape).items()
                        if not key.startswith('_')
                    }
                )

        render_data.setdefault('type', shape_type)
        render_data['normalized_type'] = RendererRegistry._normalize_shape_type(
            render_data.get('type')
        )

        if 'id' not in render_data and hasattr(shape, 'id'):
            render_data['id'] = getattr(shape, 'id')

        styles_merge = self._merge_styles(
            render_data.get('styles'),
            styles,
            render_data.get('style_str'),
        )

        if styles_merge['styles'] is not None:
            render_data['styles'] = styles_merge['styles']
        elif 'styles' in render_data:
            render_data.pop('styles')

        if styles_merge['style_str']:
            render_data['style_str'] = styles_merge['style_str']
        elif 'style_str' in render_data:
            render_data.pop('style_str')

        return render_data

    def _merge_styles(
        self,
        primary: Any,
        secondary: Any,
        existing_style_str: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Merge style sources into a unified dict/list and style string."""

        style_dict: Dict[str, Any] = {}
        style_tokens: List[str] = []

        def _flatten(source: Any) -> None:
            if not source:
                return
            if isinstance(source, dict):
                for key, value in source.items():
                    style_dict[str(key)] = value
            elif isinstance(source, (list, tuple, set)):
                for item in source:
                    _flatten(item)
            else:
                token = str(source).strip()
                if token:
                    style_tokens.append(token)

        _flatten(primary)
        _flatten(secondary)

        if existing_style_str:
            stripped = existing_style_str.strip()
            if stripped.startswith('[') and stripped.endswith(']'):
                stripped = stripped[1:-1]
            for token in stripped.split(','):
                token = token.strip()
                if token:
                    style_tokens.append(token)

        ordered_tokens: List[str] = []
        seen_tokens = set()
        for token in style_tokens:
            if token not in seen_tokens:
                ordered_tokens.append(token)
                seen_tokens.add(token)

        if style_dict:
            for key, value in style_dict.items():
                token = f"{key}={value}"
                if token not in seen_tokens:
                    ordered_tokens.append(token)
                    seen_tokens.add(token)

        style_str = ', '.join(ordered_tokens) if ordered_tokens else ''

        merged_styles: Optional[Any]
        if style_dict:
            merged_styles = style_dict
        elif ordered_tokens:
            merged_styles = ordered_tokens
        else:
            merged_styles = None

        return {
            'styles': merged_styles,
            'style_str': style_str,
        }
        
    def _get_shape_type(self, shape):
        """Extract shape type from shape data or object."""
        # If it's a dictionary with 'type' key
        if isinstance(shape, dict):
            return shape.get('type', 'unknown')
            
        # If it's a class instance with a type attribute
        if hasattr(shape, 'type'):
            return shape.type
            
        # Try to get from class name
        if hasattr(shape, '__class__'):
            return shape.__class__.__name__
        
        # If it's a dict with shape_type
        if isinstance(shape, dict) and 'shape_type' in shape:
            return shape['shape_type']
        
        # Default to Unknown
        return "Unknown"
        
    def _collect_colors_from_styles(self, styles):
        """Collect used colors from styles."""
        if not styles:
            return
            
        if isinstance(styles, dict):
            styles = [f"{k}={v}" for k, v in styles.items()]
        elif not isinstance(styles, (list, tuple)):
            return
            
        for style in styles:
            if 'color=' in style:
                # Extract color value, handling different formats
                color_match = re.search(r'color\s*=\s*([^,\]]+)', style)
                if color_match:
                    color = color_match.group(1).strip()
                    # Remove quotes if present
                    if (color.startswith('"') and color.endswith('"')) or \
                       (color.startswith("'") and color.endswith("'")):
                        color = color[1:-1]
                    self.used_colors.add(color)
    
_BUILTIN_RENDERERS_REGISTERED = False


def register_builtin_renderers():
    """Register all built-in renderers with the registry."""
    try:
        from modules.shapes.straight.straight_renderer import StraightRenderer
        from modules.shapes.ellipse.ellipse_renderer import EllipseRenderer
        from modules.shapes.arc.arc_renderer import ArcRenderer

        class StraightLineRenderer(BaseRenderer):
            def __init__(self):
                super().__init__()
                self.renderer = StraightRenderer()

            def render(self, shape_data):
                return self.renderer.render(shape_data)

        RendererRegistry.register("StraightLine", StraightLineRenderer)
        RendererRegistry.register("Line", StraightLineRenderer)

        class EllipseShapeRenderer(BaseRenderer):
            def __init__(self):
                super().__init__()
                self.renderer = EllipseRenderer()

            def render(self, shape_data):
                return self.renderer.render(shape_data)

        RendererRegistry.register("EllipseShape", EllipseShapeRenderer)
        RendererRegistry.register("Ellipse", EllipseShapeRenderer)
        RendererRegistry.register("Circle", EllipseShapeRenderer)

        class ArcShapeRenderer(BaseRenderer):
            def __init__(self):
                super().__init__()
                self.renderer = ArcRenderer()

            def render(self, shape_data):
                return self.renderer.render(shape_data)

        RendererRegistry.register("ArcShape", ArcShapeRenderer)
        RendererRegistry.register("Arc", ArcShapeRenderer)
        RendererRegistry.register("arc", ArcShapeRenderer)

        logger.debug("Built-in renderers registered successfully")
    except ImportError as e:
        logger.warning(f"Could not import built-in renderers: {e}")


def ensure_builtin_renderers_registered() -> None:
    """Ensure built-in renderers are registered exactly once per process."""

    global _BUILTIN_RENDERERS_REGISTERED
    if not _BUILTIN_RENDERERS_REGISTERED:
        register_builtin_renderers()
        _BUILTIN_RENDERERS_REGISTERED = True

class Renderer:
    """Wrapper for backward compatibility with tests"""
    def __init__(self, processed_shapes=None):
        self.processed_shapes = processed_shapes or []
        self._renderer = GlobalRenderer()
        self.config = {}

    def render(self, processed_shapes=None, mode: str = 'classic'):
        shapes_to_render = processed_shapes if processed_shapes is not None else self.processed_shapes
        return self._renderer.render(shapes_to_render, mode=mode)

    def compose_output(self, color_definitions: str, processed_body: str, mode: str = 'classic') -> str:
        return self._renderer.compose_output(color_definitions, processed_body, mode=mode)

    def configure(self, config: dict) -> None:
        if not isinstance(config, dict):
            from .exceptions import ConfigurationError
            raise ConfigurationError("Renderer config must be a dictionary")
        self.config = config
        self._renderer.configure(config)