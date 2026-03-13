"""
Infrastructure audio module.
"""

from .audio_engine import AudioEngine, PlayerEngine

# Aliases for backward compatibility
# Note: PlayerState and PlayMode are defined in domain.playback
# Import from domain for new code

__all__ = ['AudioEngine', 'PlayerEngine']
