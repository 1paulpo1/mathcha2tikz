"""
Performance monitoring utilities for the Mathcha to TikZ converter.

Provides timing, memory usage tracking, and performance analytics.
"""

import time
import psutil
import os
from typing import Dict, Any, Optional, Callable
from functools import wraps
from contextlib import contextmanager
from utils import get_logger


class PerformanceMonitor:
    """Monitors performance metrics during conversion."""
    
    def __init__(self):
        """Initialize the performance monitor."""
        self.logger = get_logger()
        self.metrics = {
            'timings': {},
            'memory_usage': {},
            'cache_hits': 0,
            'cache_misses': 0
        }
        self.start_time = None
        self.start_memory = None
    
    def start_monitoring(self):
        """Start monitoring performance."""
        self.start_time = time.time()
        self.start_memory = psutil.Process(os.getpid()).memory_info().rss
    
    def end_monitoring(self) -> Dict[str, Any]:
        """
        End monitoring and return performance metrics.
        
        Returns:
            Dictionary with performance metrics
        """
        if self.start_time is None:
            return {}
        
        end_time = time.time()
        end_memory = psutil.Process(os.getpid()).memory_info().rss
        
        total_time = end_time - self.start_time
        memory_used = end_memory - self.start_memory
        
        metrics = {
            'total_time': total_time,
            'memory_used_mb': memory_used / 1024 / 1024,
            'timings': self.metrics['timings'].copy(),
            'cache_stats': {
                'hits': self.metrics['cache_hits'],
                'misses': self.metrics['cache_misses'],
                'hit_rate': self.metrics['cache_hits'] / max(1, self.metrics['cache_hits'] + self.metrics['cache_misses'])
            }
        }
        
        self.logger.info(f"Performance metrics: {total_time:.3f}s, {memory_used/1024/1024:.1f}MB")
        return metrics
    
    def reset_monitoring(self):
        """Reset the monitoring state without creating a new instance."""
        self.start_time = None
        self.start_memory = None
        self.metrics = {
            'timings': {},
            'memory_usage': {},
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    def record_timing(self, operation: str, duration: float):
        """Record timing for a specific operation."""
        if operation not in self.metrics['timings']:
            self.metrics['timings'][operation] = []
        self.metrics['timings'][operation].append(duration)
    
    def record_cache_hit(self):
        """Record a cache hit."""
        self.metrics['cache_hits'] += 1
    
    def record_cache_miss(self):
        """Record a cache miss."""
        self.metrics['cache_misses'] += 1


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def timing_decorator(operation_name: str):
    """
    Decorator to time function execution.
    
    Args:
        operation_name: Name of the operation being timed
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                performance_monitor.record_timing(operation_name, duration)
        return wrapper
    return decorator


@contextmanager
def timing_context(operation_name: str):
    """
    Context manager for timing code blocks.
    
    Args:
        operation_name: Name of the operation being timed
    """
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        performance_monitor.record_timing(operation_name, duration)


def get_performance_summary() -> Dict[str, Any]:
    """
    Get a summary of performance metrics.
    
    Returns:
        Dictionary with performance summary
    """
    return performance_monitor.end_monitoring()


def reset_performance_monitor():
    """Reset the performance monitor."""
    global performance_monitor
    performance_monitor.reset_monitoring() 