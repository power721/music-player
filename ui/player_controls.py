"""
Player controls widget for playback control.
"""
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QSlider, QLabel, QToolButton, QMenu, QStyle
)
from PySide6.QtCore import Qt, Signal, QTimer, QTime
from PySide6.QtGui import QIcon, QFont
from typing import Optional
import threading

from player import PlayerController
from player.engine import PlayerState, PlayMode
from utils import format_time


class PlayerControls(QWidget):
    """Player controls widget at the bottom of the main window."""

    def __init__(self, player: PlayerController, parent=None):
        """
        Initialize player controls.

        Args:
            player: Player controller instance
            parent: Parent widget
        """
        super().__init__(parent)
        self._player = player
        self._current_duration = 0
        self._is_seeking = False

        self._setup_ui()
        self._setup_connections()

        # Update position timer
        self._position_timer = QTimer(self)
        self._position_timer.timeout.connect(self._update_position_display)
        self._position_timer.start(100)

    def _setup_ui(self):
        """Setup the user interface."""
        self.setObjectName('playerControls')
        self.setFixedHeight(90)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)

        # Current track info (left side)
        info_widget = self._create_info_widget()
        layout.addWidget(info_widget, 2)

        # Playback controls (center)
        controls_widget = self._create_playback_controls()
        layout.addWidget(controls_widget, 3)

        # Volume and extra controls (right side)
        volume_widget = self._create_volume_widget()
        layout.addWidget(volume_widget, 1)

        # Apply styles
        self._apply_styles()

    def _create_info_widget(self) -> QWidget:
        """Create track info widget."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Cover art placeholder
        self._cover_label = QLabel()
        self._cover_label.setFixedSize(60, 60)
        self._cover_label.setObjectName('coverArt')
        self._cover_label.setStyleSheet("""
            QLabel#coverArt {
                background-color: #282828;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self._cover_label)

        layout.addSpacing(10)

        # Track info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        self._title_label = QLabel('Not Playing')
        self._title_label.setObjectName('trackTitle')
        self._title_label.setStyleSheet("color: #ffffff; font-weight: bold;")

        self._artist_label = QLabel('')
        self._artist_label.setObjectName('trackArtist')
        self._artist_label.setStyleSheet("color: #b3b3b3;")

        info_layout.addWidget(self._title_label)
        info_layout.addWidget(self._artist_label)
        info_layout.addStretch()

        layout.addLayout(info_layout)
        layout.addStretch()

        # Favorite button
        self._favorite_btn = QPushButton('☆')
        self._favorite_btn.setObjectName('favoriteBtn')
        self._favorite_btn.setFixedSize(40, 40)
        self._favorite_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self._favorite_btn)

        return widget

    def _create_playback_controls(self) -> QWidget:
        """Create playback controls widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Progress bar
        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(10)

        self._current_time_label = QLabel('0:00')
        self._current_time_label.setObjectName('timeLabel')
        self._current_time_label.setStyleSheet("color: #b3b3b3; font-size: 11px;")
        self._current_time_label.setFixedWidth(40)

        self._progress_slider = QSlider(Qt.Horizontal)
        self._progress_slider.setObjectName('progressSlider')
        self._progress_slider.setRange(0, 1000)
        self._progress_slider.setValue(0)
        self._progress_slider.setCursor(Qt.PointingHandCursor)

        self._total_time_label = QLabel('0:00')
        self._total_time_label.setObjectName('timeLabel')
        self._total_time_label.setStyleSheet("color: #b3b3b3; font-size: 11px;")
        self._total_time_label.setFixedWidth(40)

        progress_layout.addWidget(self._current_time_label)
        progress_layout.addWidget(self._progress_slider)
        progress_layout.addWidget(self._total_time_label)

        layout.addLayout(progress_layout)

        # Control buttons
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)

        # Shuffle button
        self._shuffle_btn = self._create_control_button('🔀')
        self._shuffle_btn.setCheckable(True)
        controls_layout.addWidget(self._shuffle_btn)

        controls_layout.addStretch()

        # Previous button
        self._prev_btn = self._create_control_button('⏮')
        self._prev_btn.setFixedSize(40, 40)
        controls_layout.addWidget(self._prev_btn)

        # Play/Pause button
        self._play_pause_btn = self._create_control_button('▶️')
        self._play_pause_btn.setFixedSize(45, 45)
        self._play_pause_btn.setObjectName('playPauseBtn')
        controls_layout.addWidget(self._play_pause_btn)

        # Next button
        self._next_btn = self._create_control_button('⏭')
        self._next_btn.setFixedSize(40, 40)
        controls_layout.addWidget(self._next_btn)

        controls_layout.addStretch()

        # Repeat button
        self._repeat_btn = self._create_control_button('🔁')
        self._repeat_btn.setCheckable(True)
        controls_layout.addWidget(self._repeat_btn)

        layout.addLayout(controls_layout)

        return widget

    def _create_volume_widget(self) -> QWidget:
        """Create volume control widget."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()

        # Volume button (mute/unmute)
        self._volume_btn = QPushButton('🔊')
        self._volume_btn.setObjectName('volumeBtn')
        self._volume_btn.setFixedSize(35, 35)
        self._volume_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self._volume_btn)

        # Volume slider
        self._volume_slider = QSlider(Qt.Horizontal)
        self._volume_slider.setRange(0, 100)
        self._volume_slider.setValue(70)
        self._volume_slider.setFixedWidth(100)
        self._volume_slider.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self._volume_slider)

        # Queue button (placeholder)
        self._queue_btn = QPushButton('📋')
        self._queue_btn.setObjectName('queueBtn')
        self._queue_btn.setFixedSize(35, 35)
        self._queue_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self._queue_btn)

        return widget

    def _create_control_button(self, text: str) -> QPushButton:
        """Create a control button with styling."""
        btn = QPushButton(text)
        btn.setObjectName('controlBtn')
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton#controlBtn {
                background: transparent;
                border: none;
                color: #b3b3b3;
                font-size: 18px;
            }
            QPushButton#controlBtn:hover {
                color: #ffffff;
            }
            QPushButton#playPauseBtn {
                background: #ffffff;
                border-radius: 22px;
                color: #000000;
                font-size: 20px;
            }
            QPushButton#playPauseBtn:hover {
                transform: scale(1.05);
            }
        """)
        return btn

    def _apply_styles(self):
        """Apply widget styles."""
        self.setStyleSheet("""
            QWidget#playerControls {
                background-color: #181818;
                border-top: 1px solid #282828;
            }
            QPushButton#favoriteBtn {
                background: transparent;
                border: 2px solid #b3b3b3;
                color: #b3b3b3;
                border-radius: 20px;
                font-size: 20px;
            }
            QPushButton#favoriteBtn:hover {
                border-color: #1db954;
                color: #1db954;
            }
            QPushButton#favoriteBtn:checked {
                background-color: #1db954;
                border-color: #1db954;
                color: #ffffff;
            }
            QSlider#progressSlider::groove:horizontal {
                height: 4px;
                background: #4d4d4d;
                border-radius: 2px;
            }
            QSlider#progressSlider::handle:horizontal {
                width: 12px;
                height: 12px;
                background: #ffffff;
                border-radius: 6px;
                margin: -4px 0;
            }
            QSlider#progressSlider::handle:horizontal:hover {
                background: #1db954;
            }
            QPushButton#volumeBtn, QPushButton#queueBtn {
                background: transparent;
                border: none;
                color: #b3b3b3;
                font-size: 16px;
            }
            QPushButton#volumeBtn:hover, QPushButton#queueBtn:hover {
                color: #ffffff;
            }
        """)

    def _setup_connections(self):
        """Setup signal connections."""
        # Playback controls
        self._play_pause_btn.clicked.connect(self._toggle_play_pause)
        self._prev_btn.clicked.connect(self._player.engine.play_previous)
        self._next_btn.clicked.connect(self._player.engine.play_next)

        # Progress slider
        self._progress_slider.sliderPressed.connect(self._on_seek_start)
        self._progress_slider.sliderReleased.connect(self._on_seek_end)
        self._progress_slider.valueChanged.connect(self._on_seek)

        # Volume controls
        self._volume_slider.valueChanged.connect(self._on_volume_changed)
        self._volume_btn.clicked.connect(self._toggle_mute)

        # Favorite button
        self._favorite_btn.clicked.connect(self._toggle_favorite)

        # Shuffle and repeat
        self._shuffle_btn.clicked.connect(self._toggle_shuffle)
        self._repeat_btn.clicked.connect(self._toggle_repeat)

        # Engine connections
        self._player.engine.state_changed.connect(self._on_state_changed)
        self._player.engine.position_changed.connect(self._on_position_changed)
        self._player.engine.duration_changed.connect(self._on_duration_changed)
        self._player.engine.current_track_changed.connect(self._on_track_changed)

    def _toggle_play_pause(self):
        """Toggle play/pause."""
        if self._player.engine.state == PlayerState.PLAYING:
            self._player.engine.pause()
        else:
            self._player.engine.play()

    def _on_seek_start(self):
        """Handle seek start."""
        self._is_seeking = True

    def _on_seek_end(self):
        """Handle seek end."""
        self._is_seeking = False
        # Calculate position in milliseconds
        position_ms = int((self._progress_slider.value() / 1000) * self._current_duration * 1000)
        self._player.engine.seek(position_ms)

    def _on_seek(self, value: int):
        """Handle seek (update time label while dragging)."""
        if self._current_duration > 0:
            # Calculate position in seconds for display
            position_s = (value / 1000) * self._current_duration
            self._current_time_label.setText(format_time(position_s))

    def _on_volume_changed(self, value: int):
        """Handle volume change."""
        self._player.engine.set_volume(value)
        self._update_volume_button(value)

    def set_volume(self, volume: int):
        """
        Set volume and update slider.

        Args:
            volume: Volume level (0-100)
        """
        volume = max(0, min(100, volume))
        self._volume_slider.blockSignals(True)  # Prevent feedback loop
        self._volume_slider.setValue(volume)
        self._volume_slider.blockSignals(False)
        self._player.engine.set_volume(volume)
        self._update_volume_button(volume)

    def _update_volume_button(self, value: int):
        """Update volume button icon based on value."""
        if value == 0:
            self._volume_btn.setText('🔇')
        elif value < 50:
            self._volume_btn.setText('🔉')
        else:
            self._volume_btn.setText('🔊')

    def _toggle_mute(self):
        """Toggle mute."""
        if self._volume_slider.value() > 0:
            self._previous_volume = self._volume_slider.value()
            self._volume_slider.setValue(0)
        else:
            volume = getattr(self, '_previous_volume', 70)
            self._volume_slider.setValue(volume)

    def _toggle_favorite(self):
        """Toggle favorite status."""
        is_fav = self._player.toggle_favorite()
        self._favorite_btn.setChecked(is_fav)
        self._favorite_btn.setText('⭐' if is_fav else '☆')

    def _toggle_shuffle(self):
        """Toggle shuffle mode."""
        if self._shuffle_btn.isChecked():
            self._player.engine.set_play_mode(PlayMode.RANDOM)
            self._shuffle_btn.setStyleSheet(self._shuffle_btn.styleSheet() + " color: #1db954;")
        else:
            self._player.engine.set_play_mode(PlayMode.SEQUENTIAL)
            self._shuffle_btn.setStyleSheet(self._shuffle_btn.styleSheet().replace(" color: #1db954;", ""))

    def _toggle_repeat(self):
        """Toggle repeat mode."""
        current_mode = self._player.engine.play_mode

        if current_mode == PlayMode.SEQUENTIAL:
            self._player.engine.set_play_mode(PlayMode.PLAYLIST_LOOP)
            self._repeat_btn.setText('🔁')
            self._repeat_btn.setChecked(True)
        elif current_mode == PlayMode.PLAYLIST_LOOP:
            self._player.engine.set_play_mode(PlayMode.LOOP)
            self._repeat_btn.setText('🔂')
        else:
            self._player.engine.set_play_mode(PlayMode.SEQUENTIAL)
            self._repeat_btn.setText('🔁')
            self._repeat_btn.setChecked(False)

    def _on_state_changed(self, state: PlayerState):
        """Handle player state change."""
        if state == PlayerState.PLAYING:
            self._play_pause_btn.setText('⏸')
        else:
            self._play_pause_btn.setText('▶️')

    def _on_position_changed(self, position_ms: int):
        """Handle position change."""
        if not self._is_seeking and self._current_duration > 0:
            # Convert position to seconds for display
            position_s = position_ms / 1000
            self._current_time_label.setText(format_time(position_s))

            # Update progress slider (0-1000 range)
            value = int((position_ms / (self._current_duration * 1000)) * 1000)
            self._progress_slider.setValue(value)

    def _on_duration_changed(self, duration_ms: int):
        """Handle duration change."""
        self._current_duration = duration_ms / 1000  # Store in seconds
        self._total_time_label.setText(format_time(self._current_duration))

    def _on_track_changed(self, track_dict: dict):
        """Handle track change."""
        if track_dict:
            title = track_dict.get('title', 'Unknown')
            artist = track_dict.get('artist', 'Unknown')
            self._title_label.setText(title)
            self._artist_label.setText(artist)

            # Update favorite button
            track_id = track_dict.get('id')
            if track_id:
                is_fav = self._player.is_favorite(track_id)
                self._favorite_btn.setChecked(is_fav)
                self._favorite_btn.setText('⭐' if is_fav else '☆')

            # Clear cover immediately, load in background
            self._cover_label.clear()
            # Use QTimer to delay cover loading so UI doesn't block
            QTimer.singleShot(100, lambda: self._load_cover_art_async(track_dict))
        else:
            self._title_label.setText('Not Playing')
            self._artist_label.setText('')
            self._cover_label.clear()

    def _load_cover_art_async(self, track_dict: dict):
        """Load cover art in background thread."""
        def load_cover():
            from services import CoverService

            path = track_dict.get('path', '')
            title = track_dict.get('title', '')
            artist = track_dict.get('artist', '')
            album = track_dict.get('album', '')

            # Only try to get embedded cover, skip online (too slow)
            try:
                cover_path = CoverService._extract_embedded_cover(path)
                if cover_path:
                    return cover_path
            except Exception as e:
                print(f"Cover load error: {e}")
            return None

        def show_cover(cover_path):
            if cover_path:
                try:
                    pixmap = QPixmap(cover_path)
                    if not pixmap.isNull():
                        scaled_pixmap = pixmap.scaled(
                            60, 60,
                            Qt.KeepAspectRatioByExpanding,
                            Qt.SmoothTransformation
                        )
                        self._cover_label.setPixmap(scaled_pixmap)
                except:
                    pass

        # Run in thread
        thread = threading.Thread(target=lambda: self._load_cover_worker(load_cover, show_cover))
        thread.daemon = True
        thread.start()

    def _load_cover_worker(self, load_func, show_func):
        """Worker for loading cover in background."""
        cover_path = load_func()
        # Schedule UI update on main thread
        QTimer.singleShot(0, lambda: show_func(cover_path))

    def _update_position_display(self):
        """Update position display continuously."""
        if self._player.engine.state == PlayerState.PLAYING and not self._is_seeking:
            position_ms = self._player.engine.position() if hasattr(self._player.engine, 'position') else 0
            # Update handled by _on_position_changed signal
