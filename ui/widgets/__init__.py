"""
UI widgets module.
"""

from .ai_settings_dialog import AISettingsDialog
from .cloud_login_dialog import CloudLoginDialog
from .cover_download_dialog import CoverDownloadDialog
from .equalizer_widget import EqualizerWidget, EqualizerPreset
from .lyrics_widget_pro import LyricsWidget
from .player_controls import PlayerControls

__all__ = ['PlayerControls', 'LyricsWidget', 'CloudLoginDialog', 'AISettingsDialog', 'EqualizerWidget',
           'EqualizerPreset', 'CoverDownloadDialog']
