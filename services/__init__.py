"""
Services module - Business logic layer organized by domain.
"""

# Playback services
from .playback import PlaybackService, PlaybackManager, QueueService, PlayerController

# Library services
from .library import LibraryService

# Lyrics services
from .lyrics import LyricsService

# Metadata services
from .metadata import MetadataService, CoverService

# Cloud services
from .cloud import QuarkDriveService, QuarkService, CloudDownloadService

# AI services
from .ai import AiMetadataService

__all__ = [
    'PlaybackService', 'PlaybackManager', 'QueueService', 'PlayerController',
    'LibraryService',
    'LyricsService',
    'MetadataService', 'CoverService',
    'QuarkDriveService', 'QuarkService', 'CloudDownloadService',
    'AiMetadataService',
]
