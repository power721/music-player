"""
Cloud file domain models - Backward compatibility module.

This module re-exports classes from their new locations:
- CloudProvider, CloudAccount, CloudFile -> domain.cloud
- PlayQueueItem -> domain.playback
- PlayHistory, Favorite -> domain.history
"""

# Re-export from new locations for backward compatibility
from .cloud import CloudProvider, CloudAccount, CloudFile
from .playback import PlayQueueItem
from .history import PlayHistory, Favorite

__all__ = [
    'CloudProvider', 'CloudAccount', 'CloudFile',
    'PlayQueueItem',
    'PlayHistory', 'Favorite',
]
