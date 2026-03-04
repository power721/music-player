"""
Queue view for managing the current playback queue.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLabel,
    QMenu,
    QAbstractItemView,
    QInputDialog,
    QMessageBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QAction, QColor, QBrush
from typing import List

from player import PlayerController
from utils import format_duration


class QueueView(QWidget):
    """View for managing the current playback queue."""

    play_track = Signal(int)

    def __init__(self, player: PlayerController, parent=None):
        """
        Initialize queue view.

        Args:
            player: Player controller
            parent: Parent widget
        """
        super().__init__(parent)
        self._player = player
        self._setup_ui()
        self._setup_connections()
        self._refresh_timer = None
        self._start_auto_refresh()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(10)

        # Header
        header = QWidget()
        header.setObjectName("queueHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 10, 0, 10)
        header_layout.setSpacing(10)

        title = QLabel("🎶 Play Queue")
        title.setStyleSheet("""
            color: #1db954;
            font-size: 24px;
            font-weight: bold;
        """)
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Clear button
        self._clear_btn = QPushButton("Clear Queue")
        self._clear_btn.setObjectName("queueActionBtn")
        self._clear_btn.setCursor(Qt.PointingHandCursor)
        self._clear_btn.clicked.connect(self._clear_queue)
        header_layout.addWidget(self._clear_btn)

        layout.addWidget(header)

        # Queue list
        self._queue_list = QListWidget()
        self._queue_list.setObjectName("queueList")
        self._queue_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._queue_list.setAlternatingRowColors(True)
        self._queue_list.setDragDropMode(QAbstractItemView.InternalMove)
        self._queue_list.model().rowsMoved.connect(self._on_rows_moved)
        self._queue_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self._queue_list.customContextMenuRequested.connect(self._show_context_menu)
        self._queue_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self._queue_list)

        # Status bar
        self._status_label = QLabel("0 tracks in queue")
        self._status_label.setStyleSheet("color: #808080; font-size: 13px;")
        layout.addWidget(self._status_label)

        # Add track hint
        hint = QLabel(
            "💡 Tip: Right-click on tracks in the library to add them to the queue"
        )
        hint.setStyleSheet("color: #606060; font-size: 11px;")
        layout.addWidget(hint)

        # Apply modern styles
        self.setStyleSheet("""
            QWidget#queueHeader {
                background-color: #141414;
            }
            QPushButton#queueActionBtn {
                background: transparent;
                border: 2px solid #404040;
                color: #c0c0c0;
                padding: 6px 14px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton#queueActionBtn:hover {
                border-color: #1db954;
                color: #1db954;
                background-color: rgba(29, 185, 84, 0.1);
            }
            QListWidget#queueList {
                background-color: #1e1e1e;
                border: none;
                outline: none;
                border-radius: 8px;
            }
            QListWidget#queueList::item {
                padding: 14px 18px;
                color: #e0e0e0;
                border-bottom: 1px solid #2a2a2a;
                margin: 1px 0px;
                background-color: #1e1e1e;
            }
            /* Alternating row colors */
            QListWidget#queueList::item:alternate {
                background-color: #252525;
            }
            QListWidget#queueList::item:!alternate {
                background-color: #1e1e1e;
            }
            QListWidget#queueList::item:selected {
                background-color: #1db954;
                color: #000000;
                font-weight: bold;
            }
            QListWidget#queueList::item:selected:!alternate {
                background-color: #1db954;
            }
            QListWidget#queueList::item:selected:alternate {
                background-color: #1ed760;
            }
            QListWidget#queueList::item:hover {
                background-color: #2d2d2d;
                color: #1db954;
            }
            QListWidget#queueList::item:selected:hover {
                background-color: #1ed760;
            }
            QListWidget#queueList::item[current] {
                background-color: #1db954;
                color: #000000;
                font-weight: bold;
                border-left: 4px solid #000000;
            }
            QListWidget QScrollBar:vertical {
                background-color: #1e1e1e;
                width: 12px;
                border-radius: 6px;
            }
            QListWidget QScrollBar::handle:vertical {
                background-color: #404040;
                border-radius: 6px;
                min-height: 40px;
            }
            QListWidget QScrollBar::handle:vertical:hover {
                background-color: #505050;
            }
        """)

    def _setup_connections(self):
        """Setup signal connections."""
        # Connect to engine signals to update current track indicator
        self._player.engine.current_track_changed.connect(
            self._on_current_track_changed
        )

    def _start_auto_refresh(self):
        """Start auto-refresh timer."""
        from PySide6.QtCore import QTimer

        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._refresh_queue)
        self._refresh_timer.start(1000)  # Refresh every second

    def _refresh_queue(self):
        """Refresh the queue display."""
        # Get current playlist from engine
        playlist = self._player.engine.playlist
        current_index = self._player.engine.current_index

        # Save current selection
        selected_items = self._queue_list.selectedItems()
        selected_indices = [self._queue_list.row(item) for item in selected_items]

        # Block signals to prevent feedback
        self._queue_list.blockSignals(True)

        # Clear and repopulate
        self._queue_list.clear()

        for i, track in enumerate(playlist):
            title = track.get("title", "Unknown")
            artist = track.get("artist", "Unknown")

            # Create item with formatted text
            item_text = f"{i + 1}. {title} - {artist}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, track)

            # Set default text color
            item.setForeground(QBrush(QColor("#e0e0e0")))

            # Highlight current track
            if i == current_index:
                item.setData(Qt.UserRole + 1, True)  # Mark as current
                item.setBackground(QColor("#1db954"))
                item.setForeground(QBrush(QColor("#000000")))

            self._queue_list.addItem(item)

        # Restore selection
        for row in selected_indices:
            if row < self._queue_list.count():
                self._queue_list.setItemSelected(self._queue_list.item(row), True)

        self._queue_list.blockSignals(False)

        # Update current track styling
        self._update_current_track_indicator()

        # Update status
        self._status_label.setText(f"{len(playlist)} tracks in queue")

    def _update_current_track_indicator(self):
        """Update the visual indicator for current track."""
        current_index = self._player.engine.current_index

        for i in range(self._queue_list.count()):
            item = self._queue_list.item(i)
            if i == current_index:
                item.setBackground(QColor("#1db954"))
                item.setForeground(QColor("#000000"))
            else:
                item.setBackground(Qt.transparent)
                item.setForeground(QColor("#e0e0e0"))

    def _on_current_track_changed(self, track_dict):
        """Handle current track change."""
        self._update_current_track_indicator()

        # Scroll to current track
        current_index = self._player.engine.current_index
        if 0 <= current_index < self._queue_list.count():
            self._queue_list.scrollToItem(
                self._queue_list.item(current_index), QListWidget.PositionAtCenter
            )

    def _on_rows_moved(self):
        """Handle row move (drag and drop reorder)."""
        # Build new playlist from current list order
        new_playlist = []
        for i in range(self._queue_list.count()):
            item = self._queue_list.item(i)
            track = item.data(Qt.UserRole)
            if track:
                new_playlist.append(track)

        # Update engine playlist
        self._player.engine.load_playlist(new_playlist)

    def _on_item_double_clicked(self, item: QListWidgetItem):
        """Handle item double click."""
        track = item.data(Qt.UserRole)
        if track:
            track_id = track.get("id")
            if track_id:
                self.play_track.emit(track_id)

    def _clear_queue(self):
        """Clear the queue."""
        reply = QMessageBox.question(
            self,
            "Clear Queue",
            "Are you sure you want to clear the entire queue?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self._player.engine.clear_playlist()

    def _remove_selected(self):
        """Remove selected tracks from queue."""
        selected_items = self._queue_list.selectedItems()
        if not selected_items:
            return

        # Get indices in reverse order to remove from back to front
        rows_to_remove = sorted(
            [self._queue_list.row(item) for item in selected_items], reverse=True
        )

        # Remove from engine playlist
        for row in rows_to_remove:
            self._player.engine.remove_track(row)

    def _show_context_menu(self, pos):
        """Show context menu."""
        item = self._queue_list.itemAt(pos)
        if not item:
            return

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #282828;
                color: #ffffff;
                border: 1px solid #404040;
            }
            QMenu::item {
                padding: 8px 20px;
            }
            QMenu::item:selected {
                background-color: #1db954;
            }
        """)

        remove_action = menu.addAction("Remove from Queue")
        remove_action.triggered.connect(self._remove_selected)

        menu.addSeparator()

        edit_action = menu.addAction("Edit Media Info")
        edit_action.triggered.connect(lambda: self._edit_media_info())

        menu.exec_(self._queue_list.mapToGlobal(pos))

    def add_tracks(self, track_ids: List[int]):
        """
        Add tracks to the queue.

        Args:
            track_ids: List of track IDs to add
        """
        from database import DatabaseManager, Track

        db = DatabaseManager()

        for track_id in track_ids:
            track = db.get_track(track_id)
            if track:
                from pathlib import Path

                if Path(track.path).exists():
                    track_dict = {
                        "id": track.id,
                        "path": track.path,
                        "title": track.title,
                        "artist": track.artist,
                        "album": track.album,
                        "duration": track.duration,
                    }
                    self._player.engine.add_track(track_dict)

        db.close()

    def closeEvent(self, event):
        """Handle close event."""
        if self._refresh_timer:
            self._refresh_timer.stop()
        event.accept()

    def _edit_media_info(self):
        """Edit media information for selected track."""
        from PySide6.QtWidgets import (
            QDialog,
            QVBoxLayout,
            QFormLayout,
            QLabel,
            QLineEdit,
            QDialogButtonBox,
        )
        from services import MetadataService

        selected_items = self._queue_list.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        track_id = item.data(Qt.UserRole)

        if not track_id:
            return

        track = self._db.get_track(track_id)
        if not track:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Media Info")
        dialog.setMinimumWidth(450)
        dialog.setStyleSheet("""
            QDialog { background-color: #282828; color: #ffffff; }
            QLabel { color: #ffffff; font-size: 13px; }
            QLineEdit {
                background-color: #181818;
                color: #ffffff;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
            QLineEdit:focus { border: 1px solid #1db954; }
            QPushButton {
                background-color: #1db954;
                color: #000000;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1ed760; }
            QPushButton[role="cancel"] { background-color: #404040; color: #ffffff; }
            QPushButton[role="cancel"]:hover { background-color: #505050; }
        """)

        layout = QVBoxLayout(dialog)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignRight)

        title_input = QLineEdit(track.title or "")
        title_input.setPlaceholderText("Enter title")
        artist_input = QLineEdit(track.artist or "")
        artist_input.setPlaceholderText("Enter artist")
        album_input = QLineEdit(track.album or "")
        album_input.setPlaceholderText("Enter album")

        path_label = QLabel(track.path)
        path_label.setStyleSheet("color: #808080; font-size: 11px;")
        path_label.setWordWrap(True)

        form_layout.addRow("Title:", title_input)
        form_layout.addRow("Artist:", artist_input)
        form_layout.addRow("Album:", album_input)
        form_layout.addRow("File:", path_label)

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox()
        ok_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        cancel_button.setProperty("role", "cancel")

        buttons.addButton(ok_button, QDialogButtonBox.AcceptRole)
        buttons.addButton(cancel_button, QDialogButtonBox.RejectRole)

        layout.addWidget(buttons)

        def save_changes():
            new_title = title_input.text().strip() or track.title
            new_artist = artist_input.text().strip() or track.artist
            new_album = album_input.text().strip() or track.album

            success = MetadataService.save_metadata(
                track.path, title=new_title, artist=new_artist, album=new_album
            )

            if success:
                self._db.update_track(
                    track_id, title=new_title, artist=new_artist, album=new_album
                )
                QMessageBox.information(
                    self, "Success", "Media information saved successfully."
                )
                self.refresh()
            else:
                QMessageBox.warning(self, "Error", "Failed to save media information.")

            dialog.accept()

        ok_button.clicked.connect(save_changes)
        cancel_button.clicked.connect(dialog.reject)

        dialog.exec_()
