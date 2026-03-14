"""
UI views module.
"""

from .albums_view import AlbumsView
from .artist_view import ArtistView
from .artists_view import ArtistsView
from .cloud_view import CloudDriveView
from .library_view import LibraryView
from .playlist_view import PlaylistView
from .queue_view import QueueView

__all__ = [
    'LibraryView', 'PlaylistView', 'QueueView', 'CloudDriveView',
    'AlbumsView', 'ArtistsView', 'ArtistView',
]
