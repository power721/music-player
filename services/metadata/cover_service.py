"""
Cover art service for extracting and fetching album covers.
"""
import logging

from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
from typing import Optional
import requests
import hashlib

from .metadata_service import MetadataService


class CoverService:
    """Service for extracting and fetching album covers."""

    # User agent for web requests
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    # Cache directory
    CACHE_DIR = Path.home() / '.cache' / 'harmony_player' / 'covers'

    @classmethod
    def get_cover(cls, track_path: str, title: str, artist: str, album: str = "") -> Optional[str]:
        """
        Get cover art for a track, prioritizing embedded art.

        Args:
            track_path: Path to the audio file
            title: Track title
            artist: Track artist
            album: Album name

        Returns:
            Path to the cover image, or None
        """
        # First try embedded cover
        cover_path = cls._extract_embedded_cover(track_path)
        if cover_path:
            return cover_path

        # Fall back to cached covers
        cache_key = cls._get_cache_key(artist, album or title)
        cached_cover = cls._get_cached_cover(cache_key)
        if cached_cover and cached_cover.exists():
            return str(cached_cover)

        # Try online sources
        return cls._fetch_online_cover(title, artist, album, cache_key)

    @classmethod
    def _extract_embedded_cover(cls, track_path: str) -> Optional[str]:
        """
        Extract embedded cover from audio file.

        Args:
            track_path: Path to the audio file

        Returns:
            Path to extracted cover, or None
        """
        try:
            # Create cache directory if needed
            cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)

            # Generate cache filename
            track_file = Path(track_path)
            cache_filename = f"{track_file.stem}_{hash(track_path)}.jpg"
            cache_path = cls.CACHE_DIR / cache_filename

            # Check if already cached
            if cache_path.exists():
                return str(cache_path)

            # Extract cover using metadata service
            if MetadataService.save_cover(track_path, str(cache_path)):
                return str(cache_path)

        except Exception as e:
            logger.error(f"Error extracting embedded cover from {track_path}: {e}", exc_info=True)

        return None

    @classmethod
    def save_cover_from_metadata(cls, track_path: str, cover_data: bytes) -> Optional[str]:
        """
        Save cover art from already extracted metadata.

        Args:
            track_path: Path to the audio file (used for generating cache filename)
            cover_data: Cover image data from metadata

        Returns:
            Path to saved cover, or None
        """
        if not cover_data:
            return None

        try:
            # Create cache directory if needed
            cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)

            # Generate cache filename
            track_file = Path(track_path)
            # Determine extension from data
            if cover_data[:4] == b'\x89PNG':
                ext = '.png'
            else:
                ext = '.jpg'
            cache_filename = f"{track_file.stem}_{hash(track_path)}{ext}"
            cache_path = cls.CACHE_DIR / cache_filename

            # Check if already cached
            if cache_path.exists():
                return str(cache_path)

            # Save cover data
            with open(cache_path, 'wb') as f:
                f.write(cover_data)

            return str(cache_path)

        except Exception as e:
            logger.error(f"Error saving cover from metadata: {e}", exc_info=True)
            return None

    @classmethod
    def _get_cache_key(cls, artist: str, album: str) -> str:
        """Generate cache key for cover art."""
        key = f"{artist}:{album}".lower()
        return hashlib.md5(key.encode()).hexdigest()

    @classmethod
    def _get_cached_cover(cls, cache_key: str) -> Optional[Path]:
        """Get cached cover by cache key."""
        for ext in ['.jpg', '.jpeg', '.png']:
            cover_path = cls.CACHE_DIR / f"{cache_key}{ext}"
            if cover_path.exists():
                return cover_path
        return None

    @classmethod
    def _fetch_online_cover(cls, title: str, artist: str, album: str, cache_key: str) -> Optional[str]:
        """
        Fetch cover art from online sources.

        Args:
            title: Track title
            artist: Track artist
            album: Album name
            cache_key: Cache key for storing the cover

        Returns:
            Path to downloaded cover, or None
        """
        sources = [
            cls._fetch_from_lastfm,
            cls._fetch_from_musicbrainz,
            cls._fetch_from_itunes,
        ]

        for source in sources:
            try:
                cover_data = source(artist, album or title)
                if cover_data:
                    return cls._save_cover_to_cache(cover_data, cache_key)
            except Exception as e:
                logger.error(f"Error fetching cover from {source.__name__}: {e}", exc_info=True)
                continue

        return None

    @classmethod
    def _fetch_from_lastfm(cls, artist: str, album: str) -> Optional[bytes]:
        """
        Fetch cover from Last.fm API.

        Args:
            artist: Artist name
            album: Album name

        Returns:
            Cover image data, or None
        """
        try:
            # Last.fm album.getinfo API
            api_key = "YOUR_LASTFM_API_KEY"  # Users should provide their own API key
            url = "http://ws.audioscrobbler.com/2.0/"

            params = {
                'method': 'album.getinfo',
                'api_key': api_key,
                'artist': artist,
                'album': album,
                'format': 'json'
            }

            response = requests.get(url, params=params, headers=cls.HEADERS, timeout=3)

            if response.status_code == 200:
                data = response.json()
                image_url = None

                # Try to get the largest image
                if 'album' in data and 'image' in data['album']:
                    for img in reversed(data['album']['image']):
                        if img.get('#text'):
                            image_url = img['#text']
                            break

                if image_url:
                    img_response = requests.get(image_url, headers=cls.HEADERS, timeout=3)
                    if img_response.status_code == 200:
                        return img_response.content

        except Exception as e:
            print(f"Last.fm fetch error: {e}")

        return None

    @classmethod
    def _fetch_from_musicbrainz(cls, artist: str, album: str) -> Optional[bytes]:
        """
        Fetch cover from MusicBrainz Cover Art Archive.

        Args:
            artist: Artist name
            album: Album name

        Returns:
            Cover image data, or None
        """
        try:
            # First, search for the release
            search_url = "https://musicbrainz.org/ws/2/release/"
            params = {
                'query': f'artist:"{artist}" AND release:"{album}"',
                'limit': 1,
                'fmt': 'json'
            }

            response = requests.get(
                search_url,
                params=params,
                headers={'User-Agent': 'HarmonyPlayer/1.0'},
                timeout=3
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('releases'):
                    release_id = data['releases'][0]['id']

                    # Get cover art from Cover Art Archive
                    cover_url = f"https://coverartarchive.org/release/{release_id}/front-500"
                    cover_response = requests.get(cover_url, timeout=3)

                    if cover_response.status_code == 200:
                        return cover_response.content

        except Exception as e:
            print(f"MusicBrainz fetch error: {e}")

        return None

    @classmethod
    def _fetch_from_itunes(cls, artist: str, album: str) -> Optional[bytes]:
        """
        Fetch cover from iTunes Search API.

        Args:
            artist: Artist name
            album: Album name

        Returns:
            Cover image data, or None
        """
        try:
            search_url = "https://itunes.apple.com/search"
            params = {
                'term': f'{artist} {album}',
                'media': 'music',
                'entity': 'album',
                'limit': 1
            }

            response = requests.get(search_url, params=params, headers=cls.HEADERS, timeout=3)

            if response.status_code == 200:
                data = response.json()
                if data.get('results') and len(data['results']) > 0:
                    artwork_url = data['results'][0].get('artworkUrl100')
                    if artwork_url:
                        # Get larger version
                        artwork_url = artwork_url.replace('100x100', '600x600')
                        img_response = requests.get(artwork_url, headers=cls.HEADERS, timeout=3)
                        if img_response.status_code == 200:
                            return img_response.content

        except Exception as e:
            print(f"iTunes fetch error: {e}")

        return None

    @classmethod
    def _save_cover_to_cache(cls, cover_data: bytes, cache_key: str) -> Optional[str]:
        """
        Save cover data to cache.

        Args:
            cover_data: Image data
            cache_key: Cache key

        Returns:
            Path to cached cover, or None
        """
        try:
            cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)

            # Try to determine format from data
            if cover_data[:4] == b'\x89PNG':
                ext = '.png'
            else:
                ext = '.jpg'

            cache_path = cls.CACHE_DIR / f"{cache_key}{ext}"

            with open(cache_path, 'wb') as f:
                f.write(cover_data)

            return str(cache_path)

        except Exception as e:
            logger.error(f"Error saving cover to cache: {e}", exc_info=True)
            return None

    @classmethod
    def clear_cache(cls):
        """Clear all cached cover art."""
        try:
            if cls.CACHE_DIR.exists():
                for file in cls.CACHE_DIR.iterdir():
                    if file.is_file():
                        file.unlink()
        except Exception as e:
            logger.error(f"Error clearing cover cache: {e}", exc_info=True)
