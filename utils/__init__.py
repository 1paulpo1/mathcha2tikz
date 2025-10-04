"""
Utils package for mathcha2tikz.

Lightweight exports only. Avoid importing heavy maintenance modules at package import time.
"""
import logging

def get_logger(name: str | None = None) -> logging.Logger:
    """Return a standard library logger.
    This avoids depending on maintenance/log_handling during runtime.
    """
    return logging.getLogger(name or 'mathcha2tikz')

__all__ = ['get_logger']