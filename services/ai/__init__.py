"""
AI service module.
"""

from .ai_metadata_service import AIMetadataService
from .acoustid_service import AcoustIDService

# Aliases for consistent naming
AiMetadataService = AIMetadataService
AcoustidService = AcoustIDService

__all__ = ['AiMetadataService', 'AIMetadataService', 'AcoustidService', 'AcoustIDService']
