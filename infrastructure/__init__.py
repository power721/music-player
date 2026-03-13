"""
Infrastructure module - Technical implementations.
"""

from .audio import AudioEngine
from .database import SqliteManager

__all__ = ['AudioEngine', 'SqliteManager']
