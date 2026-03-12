"""
AI Settings Dialog for configuring AI model API.
"""
import logging

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt

from utils import t

# Configure logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


class AISettingsDialog(QDialog):
    """Dialog for configuring AI model API settings."""

    def __init__(self, config_manager, parent=None):
        """
        Initialize the AI settings dialog.

        Args:
            config_manager: ConfigManager instance for saving settings
            parent: Parent widget
        """
        super().__init__(parent)
        self._config = config_manager
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        """Setup the dialog UI."""
        self.setWindowTitle(t("ai_settings"))
        self.setMinimumWidth(500)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Enable AI checkbox
        self._enable_checkbox = QCheckBox(t("ai_enable"))
        self._enable_checkbox.setStyleSheet("font-weight: bold; font-size: 14px;")
        self._enable_checkbox.stateChanged.connect(self._on_enable_changed)
        layout.addWidget(self._enable_checkbox)

        # Settings group
        settings_group = QGroupBox(t("ai_api_config"))
        settings_layout = QVBoxLayout()
        settings_layout.setSpacing(10)

        # Base URL
        base_url_layout = QHBoxLayout()
        base_url_label = QLabel(t("ai_base_url"))
        base_url_label.setMinimumWidth(100)
        self._base_url_input = QLineEdit()
        self._base_url_input.setPlaceholderText("https://api.example.com/v1")
        base_url_layout.addWidget(base_url_label)
        base_url_layout.addWidget(self._base_url_input)
        settings_layout.addLayout(base_url_layout)

        # API Key
        api_key_layout = QHBoxLayout()
        api_key_label = QLabel(t("ai_api_key"))
        api_key_label.setMinimumWidth(100)
        self._api_key_input = QLineEdit()
        self._api_key_input.setEchoMode(QLineEdit.Password)
        self._api_key_input.setPlaceholderText(t("ai_api_key_placeholder"))
        api_key_layout.addWidget(api_key_label)
        api_key_layout.addWidget(self._api_key_input)
        settings_layout.addLayout(api_key_layout)

        # Model
        model_layout = QHBoxLayout()
        model_label = QLabel(t("ai_model"))
        model_label.setMinimumWidth(100)
        self._model_input = QLineEdit()
        self._model_input.setPlaceholderText("qwen-plus, gpt-3.5-turbo, etc.")
        model_layout.addWidget(model_label)
        model_layout.addWidget(self._model_input)
        settings_layout.addLayout(model_layout)

        # Hint label
        hint_label = QLabel(t("ai_settings_hint"))
        hint_label.setStyleSheet("color: #808080; font-size: 11px;")
        hint_label.setWordWrap(True)
        settings_layout.addWidget(hint_label)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        test_btn = QPushButton(t("ai_test_connection"))
        test_btn.clicked.connect(self._test_connection)
        button_layout.addWidget(test_btn)

        save_btn = QPushButton(t("save"))
        save_btn.clicked.connect(self._save_settings)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton(t("cancel"))
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def _on_enable_changed(self, state):
        """Handle enable checkbox state change."""
        # state is an int from stateChanged signal
        # Qt.Checked = 2, but we also accept True (bool) for direct calls
        enabled = state == Qt.Checked or state is True or state == 2
        self._base_url_input.setEnabled(enabled)
        self._api_key_input.setEnabled(enabled)
        self._model_input.setEnabled(enabled)

    def _load_settings(self):
        """Load settings from config."""
        enabled = self._config.get_ai_enabled()
        base_url = self._config.get_ai_base_url()
        api_key = self._config.get_ai_api_key()
        model = self._config.get_ai_model()

        # Block signals to prevent triggering _on_enable_changed during setup
        self._enable_checkbox.blockSignals(True)
        self._enable_checkbox.setChecked(enabled)
        self._enable_checkbox.blockSignals(False)

        # Set text and enable state
        self._base_url_input.setText(base_url)
        self._api_key_input.setText(api_key)
        self._model_input.setText(model)

        # Manually set enabled state
        self._base_url_input.setEnabled(enabled)
        self._api_key_input.setEnabled(enabled)
        self._model_input.setEnabled(enabled)

    def _save_settings(self):
        """Save settings to config."""
        enabled = self._enable_checkbox.isChecked()
        base_url = self._base_url_input.text().strip()
        api_key = self._api_key_input.text().strip()
        model = self._model_input.text().strip()

        # Validate
        if enabled:
            if not base_url:
                QMessageBox.warning(self, t("warning"), t("ai_base_url_required"))
                return
            if not api_key:
                QMessageBox.warning(self, t("warning"), t("ai_api_key_required"))
                return
            if not model:
                QMessageBox.warning(self, t("warning"), t("ai_model_required"))
                return

        # Save
        self._config.set_ai_enabled(enabled)
        self._config.set_ai_base_url(base_url)
        self._config.set_ai_api_key(api_key)
        self._config.set_ai_model(model)

        QMessageBox.information(self, t("success"), t("ai_settings_saved"))
        self.accept()

    def _test_connection(self):
        """Test the AI API connection."""
        base_url = self._base_url_input.text().strip()
        api_key = self._api_key_input.text().strip()
        model = self._model_input.text().strip()

        if not base_url or not api_key or not model:
            QMessageBox.warning(self, t("warning"), t("ai_fill_all_fields"))
            return

        # Test connection
        try:
            from openai import OpenAI

            client = OpenAI(
                api_key=api_key,
                base_url=base_url,
            )

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=10,
            )

            if response.choices:
                QMessageBox.information(self, t("success"), t("ai_connection_success"))
            else:
                QMessageBox.warning(self, t("warning"), t("ai_connection_failed"))

        except Exception as e:
            logger.error(f"AI connection test failed: {e}", exc_info=True)
            QMessageBox.critical(self, t("error"), f"{t('ai_connection_failed')}: {str(e)}")
