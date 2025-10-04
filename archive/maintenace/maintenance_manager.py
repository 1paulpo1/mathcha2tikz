"""
Manager

Provides a robust, fault-tolerant pipeline system that isolates failures
and ensures the overall conversion process continues even when individual
components fail.
"""

import traceback
from typing import Dict, List, Callable, Any, Optional, Tuple
from utils import get_logger, error_handler


class PipelineStage:
    """Represents a single stage in the processing pipeline."""
    
    def __init__(self, name: str, processor: Callable, 
                 required: bool = False, fallback: Any = None):
        """
        Initialize a pipeline stage.
        
        Args:
            name: Name of the stage
            processor: Function to process the data
            required: Whether this stage is required for success
            fallback: Fallback value if processing fails
        """
        self.name = name
        self.processor = processor
        self.required = required
        self.fallback = fallback
        self.stats = {
            'executions': 0,
            'successes': 0,
            'failures': 0,
            'total_time': 0.0
        }
    
    def execute(self, data: Any, context: Dict = None) -> Tuple[Any, bool]:
        """
        Execute this pipeline stage.
        
        Args:
            data: Input data
            context: Additional context
            
        Returns:
            Tuple of (processed_data, success)
        """
        import time
        start_time = time.time()
        
        try:
            self.stats['executions'] += 1
            
            if context:
                result = self.processor(data, **context)
            else:
                result = self.processor(data)
            
            self.stats['successes'] += 1
            self.stats['total_time'] += time.time() - start_time
            
            return result, True
            
        except Exception as e:
            self.stats['failures'] += 1
            self.stats['total_time'] += time.time() - start_time
            
            logger = get_logger()
            logger.error(f"Pipeline stage '{self.name}' failed: {e}")
            logger.debug(f"Traceback: {traceback.format_exc()}")
            
            if self.fallback is not None:
                return self.fallback, False
            return data, False


class RobustPipeline:
    """
    A robust pipeline that can handle failures gracefully and continue processing.
    """
    
    def __init__(self, name: str = "default"):
        """
        Initialize the robust pipeline.
        
        Args:
            name: Name of the pipeline
        """
        self.name = name
        self.stages: List[PipelineStage] = []
        self.logger = get_logger()
        self.context: Dict = {}
        
    def add_stage(self, name: str, processor: Callable, 
                  required: bool = False, fallback: Any = None) -> 'RobustPipeline':
        """
        Add a stage to the pipeline.
        
        Args:
            name: Stage name
            processor: Processing function
            required: Whether stage is required
            fallback: Fallback value on failure
            
        Returns:
            Self for chaining
        """
        stage = PipelineStage(name, processor, required, fallback)
        self.stages.append(stage)
        return self
    
    def set_context(self, context: Dict):
        """Set context for pipeline execution."""
        self.context = context
    
    def execute(self, initial_data: Any) -> Tuple[Any, Dict]:
        """
        Execute the pipeline with robust error handling.
        
        Args:
            initial_data: Initial data to process
            
        Returns:
            Tuple of (final_data, execution_stats)
        """
        data = initial_data
        execution_stats = {
            'total_stages': len(self.stages),
            'executed_stages': 0,
            'successful_stages': 0,
            'failed_stages': 0,
            'required_failures': 0,
            'stage_details': []
        }
        
        self.logger.info(f"Starting pipeline '{self.name}' with {len(self.stages)} stages")
        
        for i, stage in enumerate(self.stages):
            try:
                self.logger.debug(f"Executing stage {i+1}/{len(self.stages)}: {stage.name}")
                
                result, success = stage.execute(data, self.context)
                
                execution_stats['executed_stages'] += 1
                
                if success:
                    execution_stats['successful_stages'] += 1
                    data = result
                    self.logger.debug(f"Stage '{stage.name}' completed successfully")
                else:
                    execution_stats['failed_stages'] += 1
                    if stage.required:
                        execution_stats['required_failures'] += 1
                        self.logger.error(f"Required stage '{stage.name}' failed - stopping pipeline")
                        break
                    else:
                        self.logger.warning(f"Optional stage '{stage.name}' failed - continuing")
                        data = result  # Use fallback result
                
                # Record stage details
                execution_stats['stage_details'].append({
                    'name': stage.name,
                    'success': success,
                    'required': stage.required,
                    'stats': stage.stats.copy()
                })
                
            except Exception as e:
                execution_stats['failed_stages'] += 1
                execution_stats['executed_stages'] += 1
                
                if stage.required:
                    execution_stats['required_failures'] += 1
                    self.logger.error(f"Required stage '{stage.name}' failed with exception: {e}")
                    break
                else:
                    self.logger.warning(f"Optional stage '{stage.name}' failed with exception: {e}")
                    if stage.fallback is not None:
                        data = stage.fallback
                
                # Record stage details
                execution_stats['stage_details'].append({
                    'name': stage.name,
                    'success': False,
                    'required': stage.required,
                    'stats': stage.stats.copy()
                })
        
        # Check if pipeline was successful
        if execution_stats['required_failures'] > 0:
            self.logger.error(f"Pipeline '{self.name}' failed due to required stage failures")
        else:
            self.logger.info(f"Pipeline '{self.name}' completed successfully")
        
        return data, execution_stats
    
    def get_stats(self) -> Dict:
        """Get comprehensive pipeline statistics."""
        stats = {
            'name': self.name,
            'total_stages': len(self.stages),
            'stage_stats': []
        }
        
        for stage in self.stages:
            stats['stage_stats'].append({
                'name': stage.name,
                'required': stage.required,
                'stats': stage.stats.copy()
            })
        
        return stats


class ConversionPipeline:
    """
    Specialized pipeline for Mathcha to TikZ conversion with robust error handling.
    """
    
    def __init__(self):
        """Initialize the conversion pipeline."""
        self.pipeline = RobustPipeline("Mathcha2TikZ")
        self._setup_pipeline()
    
    def _setup_pipeline(self):
        """Setup the conversion pipeline stages."""
        from handlers import ColorHandler, LineHandler, ShapeHandler
        from processors.dashes import DashHandler
        from utils import formatter
        
        # Create handlers
        self.handlers = {
            'colors': ColorHandler(),
            'lines': LineHandler(),
            'shapes': ShapeHandler(debug=False),
            'dash_styles': DashHandler(),
        }
        
        # Add pipeline stages with robust error handling
        self.pipeline.add_stage(
            "environment_removal",
            self._remove_environments,
            required=False,
            fallback=None
        )
        
        self.pipeline.add_stage(
            "color_processing",
            self._process_colors,
            required=False,
            fallback=None
        )
        
        self.pipeline.add_stage(
            "line_processing",
            self._process_lines,
            required=False,
            fallback=None
        )
        
        self.pipeline.add_stage(
            "shape_processing",
            self._process_shapes,
            required=False,
            fallback=None
        )
        
        self.pipeline.add_stage(
            "dash_style_processing",
            self._process_dash_styles,
            required=False,
            fallback=None
        )
        
        self.pipeline.add_stage(
            "final_formatting",
            self._final_formatting,
            required=False,
            fallback=None
        )
    
    def _remove_environments(self, tikz_code: str) -> str:
        """Remove existing document/tikzpicture environments."""
        from utils.formatter import _remove_existing_environments
        return _remove_existing_environments(tikz_code)
    
    def _process_colors(self, tikz_code: str) -> str:
        """Process colors in TikZ code."""
        return self.handlers['colors'].process(tikz_code)
    
    def _process_lines(self, tikz_code: str) -> str:
        """Process lines in TikZ code."""
        return self.handlers['lines'].process(tikz_code)
    
    def _process_shapes(self, tikz_code: str) -> str:
        """Process shapes in TikZ code."""
        return self.handlers['shapes'].process(tikz_code)
    
    def _process_dash_styles(self, tikz_code: str) -> str:
        """Process dash styles in TikZ code."""
        return self.handlers['dash_styles'].process(tikz_code)
    
    def _final_formatting(self, tikz_code: str) -> str:
        """Apply final formatting to TikZ code."""
        from utils import formatter
        return formatter.process(tikz_code)
    
    def convert(self, tikz_code: str) -> Tuple[str, Dict]:
        """
        Convert Mathcha TikZ code with robust error handling.
        
        Args:
            tikz_code: Input TikZ code
            
        Returns:
            Tuple of (converted_code, execution_stats)
        """
        return self.pipeline.execute(tikz_code)
    
    def get_used_colors(self) -> set:
        """Get used colors from color handler."""
        return self.handlers['colors'].get_used_colors()
    
    def get_dash_styles_dict(self) -> dict:
        """Get dash styles dictionary from dash style handler."""
        return self.handlers['dash_styles'].get_tikzset_dict()


# Global pipeline instance
conversion_pipeline = ConversionPipeline() 