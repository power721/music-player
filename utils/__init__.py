"""
Utils module - Shared utilities.

Note: Config, EventBus, i18n, and hotkeys have been moved to system/ module.
This module provides backward compatibility imports.
"""

from .helpers import (
    format_duration,
    format_time,
    find_lyric_line,
    sanitize_filename,
    truncate_text,
    format_count_message,
)
from .lrc_parser import parse_lrc

# Backward compatibility - import from system module
from system.config import ConfigManager
from system.i18n import t, set_language, get_language, get_available_languages
from system.event_bus import EventBus

__all__ = [
    "format_duration",
    "format_time",
    "parse_lrc",
    "find_lyric_line",
    "sanitize_filename",
    "truncate_text",
    "format_count_message",
    "ConfigManager",
    "EventBus",
    "t",
    "set_language",
    "get_language",
    "get_available_languages",
]
