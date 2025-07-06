"""
Settings Widget Module
-------------------
This module provides the SettingsWidget class for managing application settings in the Weather & Alarm application.
"""
import logging
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QCheckBox, QFrame, QScrollArea, QFormLayout,
    QLineEdit, QFileDialog, QMessageBox, QGroupBox, QTabWidget, QSizePolicy
)
from PyQt6.QtCore import pyqtSignal, Qt, QSettings, QSize
from PyQt6.QtGui import QFont, QIcon

from ..utils.theme_manager import Theme
from ..utils.path_utils import get_icon_path

# Configure logging
logger = logging.getLogger(__name__)

class RoundedFrame(QFrame):
    """A custom frame with rounded corners and optional background color."""
    
    def __init__(self, parent=None, bg_color=None, border_radius=10):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)
        
        # Set background color and border radius
        style = f"""
            QFrame {{
                background-color: {bg_color if bg_color else 'rgba(35, 35, 40, 0.7)'};
                border-radius: {border_radius}px;
                padding: 16px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
        """
        self.setStyleSheet(style)

class SettingsWidget(QWidget):
    """Widget for managing application settings."""
    
    # Signal emitted when settings are changed
    settings_changed = pyqtSignal(dict)
    
    # Signal emitted when theme is changed (kept for compatibility)
    theme_changed = pyqtSignal(Theme)
    
    # Signal emitted when API key is changed
    api_key_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """
        Initialize the settings widget.
        
        Args:
            parent (QWidget, optional): Parent widget
        """
        super().__init__(parent)
        
        # Initialize settings
        self.settings = QSettings("WACApp", "WeatherAlarmClock")
        
        # Initialize UI
        self.init_ui()
        
        # Load settings
        self.load_settings()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Get the absolute paths to the icons
        check_icon = get_icon_path("check.svg", None)  # None means use root icons directory
        chevron_down_icon = get_icon_path("chevron-down.svg", None)  # None means use root icons directory
        
        # Create a scroll area with modern styling
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(255, 255, 255, 0.1);
                width: 8px;
                border-radius: 4px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: rgba(255, 255, 255, 0.4);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Create content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(24)
        
        # Add title with modern styling
        title_label = QLabel("Settings")
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #90CAF9;
            margin-bottom: 16px;
            padding-left: 4px;
        """)
        content_layout.addWidget(title_label)
        
        # Common styles
        group_style = """
            QGroupBox {
                background-color: rgba(40, 40, 50, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 24px;
                padding-top: 36px;
                margin-top: 16px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 8px 12px;
                color: #90CAF9;
                font-size: 18px;
                font-weight: bold;
            }
        """
        
        input_base_style = """
            background-color: rgba(50, 50, 60, 0.7);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 15px;
            min-height: 36px;
        """
        
        label_style = """
            color: rgba(255, 255, 255, 0.9);
            font-size: 15px;
            font-weight: normal;
        """
        
        # General settings group
        general_group = QGroupBox("General Settings")
        general_group.setStyleSheet(group_style)
        general_layout = QFormLayout(general_group)
        general_layout.setSpacing(16)
        general_layout.setContentsMargins(12, 24, 12, 12)
        
        # Startup settings
        self.startup_check = QCheckBox("Start application on system startup")
        self.startup_check.setStyleSheet("""
            QCheckBox {
                color: rgba(255, 255, 255, 0.9);
                font-size: 15px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 4px;
                background-color: rgba(50, 50, 60, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            QCheckBox::indicator:checked {
                background-color: #2196F3;
                border: none;
                image: url(D:/Coding/Python/WACAppPush/icons/check.svg);
            }
            QCheckBox::indicator:hover {
                background-color: rgba(60, 60, 70, 0.7);
            }
        """)
        general_layout.addRow("", self.startup_check)
        
        # Default city
        self.default_city_edit = QLineEdit()
        self.default_city_edit.setPlaceholderText("Enter default city")
        self.default_city_edit.setStyleSheet(f"""
            QLineEdit {{
                {input_base_style}
            }}
            QLineEdit:focus {{
                background-color: rgba(60, 60, 70, 0.7);
                border: 1px solid #64B5F6;
            }}
            QLineEdit::placeholder {{
                color: rgba(255, 255, 255, 0.5);
            }}
        """)
        general_layout.addRow(QLabel("Default City:"), self.default_city_edit)
        general_layout.labelForField(self.default_city_edit).setStyleSheet(label_style)
        
        content_layout.addWidget(general_group)
        
        # Weather settings group
        weather_group = QGroupBox("Weather Settings")
        weather_group.setStyleSheet(group_style)
        weather_layout = QFormLayout(weather_group)
        weather_layout.setSpacing(16)
        weather_layout.setContentsMargins(12, 24, 12, 12)
        
        # City input
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Enter your city")
        self.city_input.setMinimumSize(QSize(200, 36))
        self.city_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(50, 50, 60, 0.7);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 15px;
            }
            QLineEdit:focus {
                background-color: rgba(60, 60, 70, 0.7);
                border: 1px solid #64B5F6;
            }
        """)
        weather_layout.addRow("City:", self.city_input)
        
        # Units selection
        self.units_combo = QComboBox()
        self.units_combo.addItems(["Metric (°C)", "Imperial (°F)"])
        self.units_combo.setMinimumSize(QSize(200, 36))
        
        self.units_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: rgba(50, 50, 60, 0.7);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 15px;
            }}
            QComboBox:focus {{
                background-color: rgba(60, 60, 70, 0.7);
                border: 1px solid #64B5F6;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox::down-arrow {{
                image: url({chevron_down_icon});
                width: 12px;
                height: 12px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #2c2c2c;
                color: white;
                selection-background-color: #64B5F6;
                selection-color: white;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
        """)
        weather_layout.addRow("Units:", self.units_combo)
        weather_layout.labelForField(self.units_combo).setStyleSheet(label_style)
        
        # API Key
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("Enter your API key")
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_edit.setStyleSheet(f"""
            QLineEdit {{
                {input_base_style}
            }}
            QLineEdit:focus {{
                background-color: rgba(60, 60, 70, 0.7);
                border: 1px solid #64B5F6;
            }}
            QLineEdit::placeholder {{
                color: rgba(255, 255, 255, 0.5);
            }}
        """)
        weather_layout.addRow(QLabel("API Key:"), self.api_key_edit)
        weather_layout.labelForField(self.api_key_edit).setStyleSheet(label_style)
        
        # Refresh interval
        self.refresh_combo = QComboBox()
        self.refresh_combo.addItem("15 minutes", 15)
        self.refresh_combo.addItem("30 minutes", 30)
        self.refresh_combo.addItem("1 hour", 60)
        self.refresh_combo.addItem("3 hours", 180)
        self.refresh_combo.setStyleSheet(self.units_combo.styleSheet())
        weather_layout.addRow(QLabel("Refresh Interval:"), self.refresh_combo)
        weather_layout.labelForField(self.refresh_combo).setStyleSheet(label_style)
        
        content_layout.addWidget(weather_group)
        
        # Alarm settings group
        alarm_group = QGroupBox("Alarm Settings")
        alarm_group.setStyleSheet(group_style)
        alarm_layout = QFormLayout(alarm_group)
        alarm_layout.setSpacing(16)
        alarm_layout.setContentsMargins(12, 24, 12, 12)
        
        # Alarm sound
        self.alarm_sound_layout = QHBoxLayout()
        self.alarm_sound_layout.setSpacing(12)
        
        self.alarm_sound_edit = QLineEdit()
        self.alarm_sound_edit.setReadOnly(True)
        self.alarm_sound_edit.setStyleSheet(f"""
            QLineEdit {{
                {input_base_style}
                background-color: rgba(45, 45, 55, 0.7);
            }}
        """)
        
        self.alarm_sound_button = QPushButton("Browse...")
        self.alarm_sound_button.setMinimumSize(QSize(100, 36))
        self.alarm_sound_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(50, 50, 60, 0.7);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(60, 60, 70, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            QPushButton:pressed {
                background-color: rgba(45, 45, 55, 0.7);
            }
        """)
        self.alarm_sound_button.clicked.connect(self.browse_alarm_sound)
        
        self.alarm_sound_layout.addWidget(self.alarm_sound_edit)
        self.alarm_sound_layout.addWidget(self.alarm_sound_button)
        alarm_layout.addRow(QLabel("Alarm Sound:"), self.alarm_sound_layout)
        alarm_layout.labelForField(self.alarm_sound_layout).setStyleSheet(label_style)
        
        # Default alarm duration
        self.alarm_duration_combo = QComboBox()
        self.alarm_duration_combo.addItem("30 seconds", 30)
        self.alarm_duration_combo.addItem("1 minute", 60)
        self.alarm_duration_combo.addItem("2 minutes", 120)
        self.alarm_duration_combo.addItem("5 minutes", 300)
        self.alarm_duration_combo.setStyleSheet(self.units_combo.styleSheet())
        alarm_layout.addRow(QLabel("Default Duration:"), self.alarm_duration_combo)
        alarm_layout.labelForField(self.alarm_duration_combo).setStyleSheet(label_style)
        
        # Auto-dismiss by default
        self.auto_dismiss_check = QCheckBox("Auto-dismiss alarms by default")
        self.auto_dismiss_check.setStyleSheet(self.startup_check.styleSheet())
        alarm_layout.addRow("", self.auto_dismiss_check)
        
        content_layout.addWidget(alarm_group)
        
        # Add buttons with modern styling
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)
        
        button_style = """
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 15px;
                font-weight: bold;
                min-width: 120px;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: #42A5F5;
            }
            QPushButton:pressed {
                background-color: #1E88E5;
            }
        """
        
        # Add save button
        save_button = QPushButton("Save Settings")
        save_button.setStyleSheet(button_style)
        save_button.clicked.connect(self.save_settings)
        buttons_layout.addWidget(save_button)
        
        # Add reset button
        reset_button = QPushButton("Reset to Defaults")
        reset_button.setStyleSheet(button_style.replace(
            "#2196F3",
            "rgba(50, 50, 60, 0.7)"
        ).replace(
            "#42A5F5",
            "rgba(60, 60, 70, 0.7)"
        ).replace(
            "#1E88E5",
            "rgba(45, 45, 55, 0.7)"
        ))
        reset_button.clicked.connect(self.reset_settings)
        buttons_layout.addWidget(reset_button)
        
        buttons_layout.addStretch()
        content_layout.addLayout(buttons_layout)
        
        # Add stretch to push everything to the top
        content_layout.addStretch()
        
        # Set the scroll content
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
    
    def load_settings(self):
        """Load settings from QSettings."""
        # Theme is now always dark mode, so no need to load theme setting
        
        # Load startup setting
        startup = self.settings.value("startOnStartup", False, type=bool)
        self.startup_check.setChecked(startup)
        
        # Load default city
        default_city = self.settings.value("defaultCity", "")
        self.default_city_edit.setText(default_city)
        
        # Load units
        units = self.settings.value("weatherUnits", "metric")
        units_index = 0  # Default to metric
        
        if units == "imperial":
            units_index = 1
        elif units == "standard":
            units_index = 2
            
        self.units_combo.setCurrentIndex(units_index)
        
        # Load API key
        api_key = self.settings.value("apiKey", "")
        self.api_key_edit.setText(api_key)
        
        # Load refresh interval
        refresh = self.settings.value("weatherRefreshInterval", 30, type=int)
        refresh_index = 1  # Default to 30 minutes
        
        if refresh == 15:
            refresh_index = 0
        elif refresh == 60:
            refresh_index = 2
        elif refresh == 180:
            refresh_index = 3
            
        self.refresh_combo.setCurrentIndex(refresh_index)
        
        # Load alarm sound
        alarm_sound = self.settings.value("alarmSound", "")
        self.alarm_sound_edit.setText(alarm_sound)
        
        # Load alarm duration
        duration = self.settings.value("alarmDuration", 60, type=int)
        duration_index = 1  # Default to 60 seconds
        
        if duration == 30:
            duration_index = 0
        elif duration == 120:
            duration_index = 2
        elif duration == 300:
            duration_index = 3
            
        self.alarm_duration_combo.setCurrentIndex(duration_index)
        
        # Load auto-dismiss
        auto_dismiss = self.settings.value("autoDismiss", True, type=bool)
        self.auto_dismiss_check.setChecked(auto_dismiss)
        
        logger.debug("Settings loaded")
    
    def save_settings(self):
        """Save settings to QSettings."""
        # Theme is now always dark mode
        self.settings.setValue("theme", "dark")
        
        # Save other settings
        self.settings.setValue("startOnStartup", self.startup_check.isChecked())
        self.settings.setValue("defaultCity", self.default_city_edit.text())
        self.settings.setValue("weatherUnits", self.units_combo.currentData())
        self.settings.setValue("apiKey", self.api_key_edit.text())
        self.settings.setValue("weatherRefreshInterval", self.refresh_combo.currentData())
        self.settings.setValue("alarmSound", self.alarm_sound_edit.text())
        self.settings.setValue("alarmDuration", self.alarm_duration_combo.currentData())
        self.settings.setValue("autoDismiss", self.auto_dismiss_check.isChecked())
        
        # Emit settings changed signal
        self.settings_changed.emit(self.get_settings_dict())
        
        # Emit theme changed signal (always dark theme)
        self.theme_changed.emit(Theme.DARK)
        
        # Emit API key changed signal
        self.api_key_changed.emit(self.api_key_edit.text())
        
        # Show success message
        QMessageBox.information(self, "Settings", "Settings saved successfully")
        
        logger.debug("Settings saved")
    
    def reset_settings(self):
        """Reset settings to defaults."""
        # Ask for confirmation
        reply = QMessageBox.question(
            self, 
            "Reset Settings", 
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Reset settings
            self.settings.clear()
            
            # Reload settings
            self.load_settings()
            
            # Emit settings changed signal
            self.settings_changed.emit(self.get_settings_dict())
            
            # Show success message
            QMessageBox.information(self, "Settings", "Settings reset to defaults")
            
            logger.debug("Settings reset to defaults")
    
    def browse_alarm_sound(self):
        """Open file dialog to select alarm sound."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Alarm Sound",
            "",
            "Sound Files (*.mp3 *.wav *.ogg);;All Files (*)"
        )
        
        if file_path:
            self.alarm_sound_edit.setText(file_path)
    
    def on_theme_changed(self):
        """Handle theme change (kept for compatibility but always emits dark theme)."""
        # Always emit dark theme
        self.theme_changed.emit(Theme.DARK)
    
    def set_current_settings(self, theme, api_key):
        """
        Set current settings in the UI.
        
        Args:
            theme (Theme): The current theme (always dark)
            api_key (str): The API key
        """
        # Set API key
        if api_key:
            self.api_key_edit.setText(api_key)
    
    def get_settings_dict(self):
        """Get settings as a dictionary."""
        return {
            "theme": "dark",  # Always dark mode
            "startOnStartup": self.startup_check.isChecked(),
            "defaultCity": self.default_city_edit.text(),
            "weatherUnits": self.units_combo.currentData(),
            "apiKey": self.api_key_edit.text(),
            "weatherRefreshInterval": self.refresh_combo.currentData(),
            "alarmSound": self.alarm_sound_edit.text(),
            "alarmDuration": self.alarm_duration_combo.currentData(),
            "autoDismiss": self.auto_dismiss_check.isChecked()
        }