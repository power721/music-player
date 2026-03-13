"""
Infrastructure database module.
"""

from .sqlite_manager import DatabaseManager

# Alias for new architecture
SqliteManager = DatabaseManager

__all__ = ['DatabaseManager', 'SqliteManager']
