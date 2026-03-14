"""
Services module - Business logic layer organized by domain.
"""

# AI services
from .ai import AIMetadataService, AcoustIDService
# Cloud services
from .cloud import QuarkDriveService, CloudDownloadService
# Library services
from .library import LibraryService
# Lyrics services
from .lyrics import LyricsService
# Metadata services
from .metadata import MetadataService, CoverService
# Playback services
from .playback import PlaybackService, QueueService

__all__ = [
    'PlaybackService', 'QueueService',
    'LibraryService',
    'LyricsService',
    'MetadataService', 'CoverService',
    'QuarkDriveService', 'CloudDownloadService',
    'AIMetadataService', 'AcoustIDService',
]
