"""
Centralized logging system for the Mathcha to TikZ converter.

Provides structured logging with different levels and proper error handling.
"""

import logging
import sys
from typing import Optional
from enum import Enum


class LogLevel(Enum):
    """Log levels for the application."""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class Logger:
    """Centralized logger for the Mathcha to TikZ converter."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._setup_logger()
            self._initialized = True
    
    def _setup_logger(self):
        """Setup the logger with proper configuration."""
        self.logger = logging.getLogger('mathcha2tikz')
        self.logger.setLevel(logging.INFO)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(console_handler)
    
    def set_level(self, level: LogLevel):
        """Set the logging level."""
        self.logger.setLevel(level.value)
        for handler in self.logger.handlers:
            handler.setLevel(level.value)
    
    def debug(self, message: str, context: Optional[str] = None):
        """Log a debug message."""
        if context:
            self.logger.debug(f"{message} (Context: {context})")
        else:
            self.logger.debug(message)
    
    def info(self, message: str, context: Optional[str] = None):
        """Log an info message."""
        if context:
            self.logger.info(f"{message} (Context: {context})")
        else:
            self.logger.info(message)
    
    def warning(self, message: str, context: Optional[str] = None):
        """Log a warning message."""
        if context:
            self.logger.warning(f"{message} (Context: {context})")
        else:
            self.logger.warning(message)
    
    def error(self, message: str, context: Optional[str] = None):
        """Log an error message."""
        if context:
            self.logger.error(f"{message} (Context: {context})")
        else:
            self.logger.error(message)
    
    def critical(self, message: str, context: Optional[str] = None):
        """Log a critical message."""
        if context:
            self.logger.critical(f"{message} (Context: {context})")
        else:
            self.logger.critical(message)


# Global logger instance
logger = Logger()


def get_logger() -> Logger:
    """Get the global logger instance."""
    return logger 