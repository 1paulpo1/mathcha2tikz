"""
Error Handling Utilities

Provides centralized error handling patterns and decorators
to reduce code duplication across handlers and processors.
"""

import functools
from typing import Callable, Any, Optional
from utils import get_logger


def safe_processing(operation_name: str, fallback_return: Any = None):
    """
    Decorator for safe processing with consistent error handling.
    
    Args:
        operation_name: Name of the operation for error logging
        fallback_return: Value to return on error (defaults to original input)
        
    Returns:
        Decorated function with error handling
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, tikz_code: str, *args, **kwargs) -> str:
            try:
                return func(self, tikz_code, *args, **kwargs)
            except Exception as e:
                # Use the handler's logger if available, otherwise create one
                logger = getattr(self, 'logger', get_logger())
                logger.error(f"Error in {operation_name}: {e}")
                
                # Return fallback value or original input
                if fallback_return is not None:
                    return fallback_return
                return tikz_code
        
        return wrapper
    return decorator


def safe_regex_operation(operation_name: str):
    """
    Decorator for safe regex operations with error handling.
    
    Args:
        operation_name: Name of the regex operation for error logging
        
    Returns:
        Decorated function with regex error handling
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> str:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger = get_logger()
                logger.error(f"Regex error in {operation_name}: {e}")
                # Return original string on regex error
                if args and isinstance(args[0], str):
                    return args[0]
                return ""
        
        return wrapper
    return decorator


def safe_math_operation(operation_name: str, default_value: Any = None):
    """
    Decorator for safe mathematical operations with error handling.
    
    Args:
        operation_name: Name of the math operation for error logging
        default_value: Default value to return on error
        
    Returns:
        Decorated function with math error handling
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger = get_logger()
                logger.error(f"Math error in {operation_name}: {e}")
                return default_value
        
        return wrapper
    return decorator


class ErrorHandler:
    """
    Centralized error handler for common operations.
    """
    
    def __init__(self):
        """Initialize the error handler."""
        self.logger = get_logger()
    
    def safe_process(self, operation_name: str, processor_func: Callable, 
                    tikz_code: str, fallback_return: Any = None) -> str:
        """
        Safely process TikZ code with consistent error handling.
        
        Args:
            operation_name: Name of the operation
            processor_func: Function to process the code
            tikz_code: Input TikZ code
            fallback_return: Value to return on error
            
        Returns:
            Processed code or fallback value
        """
        try:
            return processor_func(tikz_code)
        except Exception as e:
            self.logger.error(f"Error in {operation_name}: {e}")
            return fallback_return if fallback_return is not None else tikz_code
    
    def safe_regex_sub(self, pattern: str, repl: str, string: str, 
                       operation_name: str = "regex substitution") -> str:
        """
        Safely perform regex substitution with error handling.
        
        Args:
            pattern: Regex pattern
            repl: Replacement string
            string: Input string
            operation_name: Name for error logging
            
        Returns:
            Substituted string or original string on error
        """
        try:
            import re
            return re.sub(pattern, repl, string)
        except Exception as e:
            self.logger.error(f"Regex error in {operation_name}: {e}")
            return string
    
    def safe_math_calculation(self, calculation_func: Callable, 
                             operation_name: str, default_value: Any = None, 
                             *args, **kwargs) -> Any:
        """
        Safely perform mathematical calculations with error handling.
        
        Args:
            calculation_func: Function to perform calculation
            operation_name: Name for error logging
            default_value: Default value on error
            *args, **kwargs: Arguments for calculation function
            
        Returns:
            Calculation result or default value
        """
        try:
            return calculation_func(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Math error in {operation_name}: {e}")
            return default_value


# Global error handler instance
error_handler = ErrorHandler() 