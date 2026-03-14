"""
Album card widget for displaying album information in a grid.
"""

import logging
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFrame,
    QGraphicsDropShadowEffect,
)
from PySide6.QtCore import Qt, Signal, QSize, QPropertyAnimation, QRect, QEasingCurve
from PySide6.QtGui import QPixmap, QColor, QPainter, QFont

from domain.album import Album

logger = logging.getLogger(__name__)


class AlbumCard(QWidget):
    """
    Card widget for displaying album information.

    Features:
        - Album cover with hover effect
        - Album name and artist
        - Click signal for navigation
    """

    clicked = Signal(object)  # Emits Album object

    # Card size constants
    COVER_SIZE = 180
    CARD_WIDTH = 180
    CARD_HEIGHT = 240
    BORDER_RADIUS = 8

    def __init__(self, album: Album, parent=None):
        super().__init__(parent)
        self._album = album
        self._is_hovering = False

        self._setup_ui()
        self._load_cover()

    def _setup_ui(self):
        """Set up the card UI."""
        self.setFixedSize(self.CARD_WIDTH, self.CARD_HEIGHT)
        self.setCursor(Qt.PointingHandCursor)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Cover container
        self._cover_container = QFrame()
        self._cover_container.setFixedSize(self.COVER_SIZE, self.COVER_SIZE)
        self._cover_container.setStyleSheet(f"""
            QFrame {{
                background-color: #2a2a2a;
                border-radius: {self.BORDER_RADIUS}px;
            }}
        """)

        # Cover label
        self._cover_label = QLabel(self._cover_container)
        self._cover_label.setFixedSize(self.COVER_SIZE, self.COVER_SIZE)
        self._cover_label.setAlignment(Qt.AlignCenter)
        self._cover_label.setStyleSheet(f"""
            QLabel {{
                border-radius: {self.BORDER_RADIUS}px;
            }}
        """)

        # Info container
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(4, 0, 4, 0)
        info_layout.setSpacing(2)

        # Album name
        self._name_label = QLabel(self._album.display_name)
        self._name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._name_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 13px;
                font-weight: bold;
                background: transparent;
            }
        """)
        self._name_label.setWordWrap(True)
        self._name_label.setMaximumHeight(36)

        # Artist name
        self._artist_label = QLabel(self._album.display_artist)
        self._artist_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._artist_label.setStyleSheet("""
            QLabel {
                color: #b3b3b3;
                font-size: 12px;
                background: transparent;
            }
        """)

        info_layout.addWidget(self._name_label)
        info_layout.addWidget(self._artist_label)

        layout.addWidget(self._cover_container, 0, Qt.AlignHCenter)
        layout.addWidget(info_widget)
        layout.addStretch()

    def _load_cover(self):
        """Load album cover image."""
        cover_path = self._album.cover_path

        if cover_path and Path(cover_path).exists():
            try:
                pixmap = QPixmap(cover_path)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(
                        self.COVER_SIZE, self.COVER_SIZE,
                        Qt.KeepAspectRatioByExpanding,
                        Qt.SmoothTransformation
                    )
                    self._cover_label.setPixmap(scaled)
                    return
            except Exception as e:
                logger.debug(f"Error loading cover: {e}")

        # Default cover
        self._set_default_cover()

    def _set_default_cover(self):
        """Set default cover when no cover is available."""
        pixmap = QPixmap(self.COVER_SIZE, self.COVER_SIZE)
        pixmap.fill(QColor("#3d3d3d"))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw music note icon
        painter.setPen(QColor("#666666"))
        font = QFont()
        font.setPixelSize(60)
        painter.setFont(font)
        painter.drawText(
            QRect(0, 0, self.COVER_SIZE, self.COVER_SIZE),
            Qt.AlignCenter, "\u266B"  # Music note
        )
        painter.end()

        self._cover_label.setPixmap(pixmap)

    def enterEvent(self, event):
        """Handle mouse enter for hover effect."""
        self._is_hovering = True
        self._cover_container.setStyleSheet(f"""
            QFrame {{
                background-color: #2a2a2a;
                border-radius: {self.BORDER_RADIUS}px;
                border: 2px solid #1db954;
            }}
        """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave for hover effect."""
        self._is_hovering = False
        self._cover_container.setStyleSheet(f"""
            QFrame {{
                background-color: #2a2a2a;
                border-radius: {self.BORDER_RADIUS}px;
            }}
        """)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Handle mouse click."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self._album)
        super().mousePressEvent(event)

    def get_album(self) -> Album:
        """Get the album object."""
        return self._album
