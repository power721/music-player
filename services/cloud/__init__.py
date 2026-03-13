"""
Cloud service module.
"""

from .quark_service import QuarkDriveService
from .download_service import CloudDownloadService

# Alias for new naming convention
QuarkService = QuarkDriveService

__all__ = ['QuarkDriveService', 'QuarkService', 'CloudDownloadService']
