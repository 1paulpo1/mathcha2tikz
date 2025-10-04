"""
Advanced optimization utilities for the Mathcha to TikZ converter.

Provides object pooling, result caching, and performance optimizations.
"""

import time
import hashlib
from typing import Dict, Any, Optional, Callable, List, Tuple
from functools import lru_cache, wraps
from collections import defaultdict
import threading
from .log_handling import get_logger


class ObjectPool:
    """Object pool for frequently created objects to reduce GC pressure."""
    
    def __init__(self, max_size: int = 100):
        """Initialize the object pool."""
        self.max_size = max_size
        self.pool: Dict[str, List[Any]] = defaultdict(list)
        self.lock = threading.Lock()
        self.logger = get_logger()
    
    def get(self, obj_type: str, factory: Callable[[], Any]) -> Any:
        """
        Get an object from the pool or create a new one.
        
        Args:
            obj_type: Type identifier for the object
            factory: Function to create new objects
            
        Returns:
            Object from pool or newly created
        """
        with self.lock:
            if self.pool[obj_type]:
                obj = self.pool[obj_type].pop()
                self.logger.debug(f"Reused {obj_type} from pool")
                return obj
            else:
                obj = factory()
                self.logger.debug(f"Created new {obj_type}")
                return obj
    
    def put(self, obj_type: str, obj: Any):
        """
        Return an object to the pool.
        
        Args:
            obj_type: Type identifier for the object
            obj: Object to return to pool
        """
        with self.lock:
            if len(self.pool[obj_type]) < self.max_size:
                self.pool[obj_type].append(obj)
                self.logger.debug(f"Returned {obj_type} to pool")
    
    def clear(self):
        """Clear all pools."""
        with self.lock:
            self.pool.clear()


class ResultCache:
    """Cache for conversion results to avoid redundant processing."""
    
    def __init__(self, max_size: int = 1000):
        """Initialize the result cache."""
        self.max_size = max_size
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.lock = threading.Lock()
        self.logger = get_logger()
    
    def _generate_key(self, data: str) -> str:
        """Generate a cache key from input data."""
        return hashlib.md5(data.encode()).hexdigest()
    
    def get(self, data: str) -> Optional[Any]:
        """
        Get cached result for input data.
        
        Args:
            data: Input data to look up
            
        Returns:
            Cached result or None if not found
        """
        key = self._generate_key(data)
        with self.lock:
            if key in self.cache:
                result, timestamp = self.cache[key]
                # Check if cache entry is still valid (24 hours)
                if time.time() - timestamp < 86400:
                    self.logger.debug("Cache hit")
                    return result
                else:
                    del self.cache[key]
        return None
    
    def put(self, data: str, result: Any):
        """
        Cache a result for input data.
        
        Args:
            data: Input data
            result: Result to cache
        """
        key = self._generate_key(data)
        with self.lock:
            # Implement LRU eviction if cache is full
            if len(self.cache) >= self.max_size:
                oldest_key = min(self.cache.keys(), 
                               key=lambda k: self.cache[k][1])
                del self.cache[oldest_key]
            
            self.cache[key] = (result, time.time())
            self.logger.debug("Cached result")
    
    def clear(self):
        """Clear the cache."""
        with self.lock:
            self.cache.clear()


class CoordinateCache:
    """Cache for coordinate normalization and formatting."""
    
    def __init__(self, max_size: int = 10000):
        """Initialize the coordinate cache."""
        self.max_size = max_size
        self.cache: Dict[str, str] = {}
        self.lock = threading.Lock()
    
    def normalize_coordinate(self, coord_str: str) -> str:
        """
        Normalize coordinate string with caching.
        
        Args:
            coord_str: Coordinate string to normalize
            
        Returns:
            Normalized coordinate string
        """
        with self.lock:
            if coord_str in self.cache:
                return self.cache[coord_str]
            
            # Simple normalization: remove extra spaces, round to 2 decimal places
            try:
                # Parse coordinate
                if ',' in coord_str:
                    x, y = coord_str.split(',', 1)
                    x = x.strip()
                    y = y.strip()
                    
                    # Try to convert to float and round
                    try:
                        x_val = float(x)
                        y_val = float(y)
                        normalized = f"{x_val:.2f}, {y_val:.2f}"
                    except ValueError:
                        normalized = f"{x}, {y}"
                else:
                    normalized = coord_str.strip()
                
                # Cache result
                if len(self.cache) < self.max_size:
                    self.cache[coord_str] = normalized
                
                return normalized
            except Exception:
                return coord_str.strip()
    
    def clear(self):
        """Clear the coordinate cache."""
        with self.lock:
            self.cache.clear()


class BatchProcessor:
    """Process multiple operations in batches for better performance."""
    
    def __init__(self, batch_size: int = 100):
        """Initialize the batch processor."""
        self.batch_size = batch_size
        self.logger = get_logger()
    
    def process_batch(self, items: List[Any], processor: Callable[[Any], Any]) -> List[Any]:
        """
        Process items in batches.
        
        Args:
            items: List of items to process
            processor: Function to apply to each item
            
        Returns:
            List of processed items
        """
        results = []
        total_items = len(items)
        
        for i in range(0, total_items, self.batch_size):
            batch = items[i:i + self.batch_size]
            batch_results = [processor(item) for item in batch]
            results.extend(batch_results)
            
            self.logger.debug(f"Processed batch {i//self.batch_size + 1}/{(total_items + self.batch_size - 1)//self.batch_size}")
        
        return results


# Global instances
object_pool = ObjectPool()
result_cache = ResultCache()
coordinate_cache = CoordinateCache()
batch_processor = BatchProcessor()


def optimize_conversion(func: Callable) -> Callable:
    """
    Decorator to optimize conversion functions with caching and pooling.
    
    Args:
        func: Function to optimize
        
    Returns:
        Optimized function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check cache first
        if len(args) > 0 and isinstance(args[0], str):
            cached_result = result_cache.get(args[0])
            if cached_result is not None:
                return cached_result
        
        # Execute function
        result = func(*args, **kwargs)
        
        # Cache result
        if len(args) > 0 and isinstance(args[0], str):
            result_cache.put(args[0], result)
        
        return result
    
    return wrapper


def optimize_coordinates(func: Callable) -> Callable:
    """
    Decorator to optimize coordinate processing functions.
    
    Args:
        func: Function to optimize
        
    Returns:
        Optimized function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Use coordinate cache for coordinate strings
        if len(args) > 0 and isinstance(args[0], str):
            if any(char.isdigit() for char in args[0]):
                # Likely a coordinate string
                return coordinate_cache.normalize_coordinate(args[0])
        
        return func(*args, **kwargs)
    
    return wrapper


def clear_all_caches():
    """Clear all optimization caches."""
    object_pool.clear()
    result_cache.clear()
    coordinate_cache.clear()


def get_cache_stats() -> Dict[str, Any]:
    """Get statistics about all caches."""
    return {
        'object_pool': {
            'total_objects': sum(len(pool) for pool in object_pool.pool.values()),
            'pool_types': list(object_pool.pool.keys())
        },
        'result_cache': {
            'size': len(result_cache.cache),
            'max_size': result_cache.max_size
        },
        'coordinate_cache': {
            'size': len(coordinate_cache.cache),
            'max_size': coordinate_cache.max_size
        }
    } 