"""
Settings Widget Module
-------------------
This module provides the SettingsWidget class for managing application settings in the Weather & Alarm application.
"""
import logging
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QCheckBox, QFrame, QScrollArea, QFormLayout,
    QLineEdit, QFileDialog, QMessageBox, QGroupBox
)
from PyQt5.QtCore import pyqtSignal, Qt, QSettings

from ..utils.theme_manager import Theme

# Configure logging
logger = logging.getLogger(__name__)

class SettingsWidget(QWidget):
    """Widget for managing application settings."""
    
    # Signal emitted when settings are changed
    settings_changed = pyqtSignal(dict)
    
    # Signal emitted when theme is changed
    theme_changed = pyqtSignal(Theme)
    
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
        
        # Create a scroll area for the content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Create a widget to hold the scrollable content
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(16, 16, 16, 16)
        scroll_layout.setSpacing(16)
        
        # Add title
        title_label = QLabel("Settings")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        scroll_layout.addWidget(title_label)
        
        # General settings group
        general_group = QGroupBox("General Settings")
        general_layout = QFormLayout(general_group)
        
        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Light", Theme.LIGHT)
        self.theme_combo.addItem("Dark", Theme.DARK)
        self.theme_combo.addItem("System", Theme.SYSTEM)
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        general_layout.addRow("Theme:", self.theme_combo)
        
        # Startup settings
        self.startup_check = QCheckBox("Start application on system startup")
        general_layout.addRow("", self.startup_check)
        
        # Default city
        self.default_city_edit = QLineEdit()
        self.default_city_edit.setPlaceholderText("Enter default city")
        general_layout.addRow("Default City:", self.default_city_edit)
        
        scroll_layout.addWidget(general_group)
        
        # Weather settings group
        weather_group = QGroupBox("Weather Settings")
        weather_layout = QFormLayout(weather_group)
        
        # Units selection
        self.units_combo = QComboBox()
        self.units_combo.addItem("Metric (°C, m/s)", "metric")
        self.units_combo.addItem("Imperial (°F, mph)", "imperial")
        self.units_combo.addItem("Standard (K, m/s)", "standard")
        weather_layout.addRow("Units:", self.units_combo)
        
        # API Key
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("Enter OpenWeatherMap API key")
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        weather_layout.addRow("API Key:", self.api_key_edit)
        
        # Refresh interval
        self.refresh_combo = QComboBox()
        self.refresh_combo.addItem("15 minutes", 15)
        self.refresh_combo.addItem("30 minutes", 30)
        self.refresh_combo.addItem("1 hour", 60)
        self.refresh_combo.addItem("3 hours", 180)
        weather_layout.addRow("Refresh Interval:", self.refresh_combo)
        
        scroll_layout.addWidget(weather_group)
        
        # Alarm settings group
        alarm_group = QGroupBox("Alarm Settings")
        alarm_layout = QFormLayout(alarm_group)
        
        # Alarm sound
        self.alarm_sound_layout = QHBoxLayout()
        self.alarm_sound_edit = QLineEdit()
        self.alarm_sound_edit.setReadOnly(True)
        self.alarm_sound_button = QPushButton("Browse...")
        self.alarm_sound_button.clicked.connect(self.browse_alarm_sound)
        self.alarm_sound_layout.addWidget(self.alarm_sound_edit)
        self.alarm_sound_layout.addWidget(self.alarm_sound_button)
        alarm_layout.addRow("Alarm Sound:", self.alarm_sound_layout)
        
        # Default alarm duration
        self.alarm_duration_combo = QComboBox()
        self.alarm_duration_combo.addItem("30 seconds", 30)
        self.alarm_duration_combo.addItem("1 minute", 60)
        self.alarm_duration_combo.addItem("2 minutes", 120)
        self.alarm_duration_combo.addItem("5 minutes", 300)
        alarm_layout.addRow("Default Duration:", self.alarm_duration_combo)
        
        # Auto-dismiss by default
        self.auto_dismiss_check = QCheckBox("Auto-dismiss alarms by default")
        alarm_layout.addRow("", self.auto_dismiss_check)
        
        scroll_layout.addWidget(alarm_group)
        
        # Add save button
        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(self.save_settings)
        scroll_layout.addWidget(save_button)
        
        # Add reset button
        reset_button = QPushButton("Reset to Defaults")
        reset_button.clicked.connect(self.reset_settings)
        scroll_layout.addWidget(reset_button)
        
        # Add stretch to push everything to the top
        scroll_layout.addStretch()
        
        # Set the scroll content
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
    
    def load_settings(self):
        """Load settings from QSettings."""
        # Load theme
        theme_value = self.settings.value("theme", "system")
        theme_index = 2  # Default to system theme
        
        if theme_value == "light":
            theme_index = 0
        elif theme_value == "dark":
            theme_index = 1
            
        self.theme_combo.setCurrentIndex(theme_index)
        
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
        # Get theme
        theme_index = self.theme_combo.currentIndex()
        theme_data = self.theme_combo.itemData(theme_index)
        theme_name = theme_data.value if theme_data else "system"
        
        # Save settings
        self.settings.setValue("theme", theme_name)
        self.settings.setValue("startOnStartup", self.startup_check.isChecked())
        self.settings.setValue("defaultCity", self.default_city_edit.text())
        self.settings.setValue("weatherUnits", self.units_combo.currentData())
        self.settings.setValue("apiKey", self.api_key_edit.text())
        self.settings.setValue("weatherRefreshInterval", self.refresh_combo.currentData())
        self.settings.setValue("alarmSound", self.alarm_sound_edit.text())
        self.settings.setValue("alarmDuration", self.alarm_duration_combo.currentData())
        self.settings.setValue("autoDismiss", self.auto_dismiss_check.isChecked())
        
        # Sync settings
        self.settings.sync()
        
        # Get settings as dictionary
        settings_dict = self.get_settings_dict()
        
        # Emit signals
        self.settings_changed.emit(settings_dict)
        self.theme_changed.emit(theme_data)
        
        # Show confirmation
        QMessageBox.information(self, "Settings Saved", "Your settings have been saved successfully.")
        
        logger.info("Settings saved")
    
    def reset_settings(self):
        """Reset settings to defaults."""
        # Confirm reset
        confirm = QMessageBox.question(
            self,
            "Confirm Reset",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            # Clear settings
            self.settings.clear()
            
            # Reload defaults
            self.load_settings()
            
            # Show confirmation
            QMessageBox.information(self, "Settings Reset", "Your settings have been reset to defaults.")
            
            logger.info("Settings reset to defaults")
    
    def browse_alarm_sound(self):
        """Browse for an alarm sound file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Alarm Sound",
            "",
            "Sound Files (*.mp3 *.wav *.ogg);;All Files (*.*)"
        )
        
        if file_path:
            self.alarm_sound_edit.setText(file_path)
    
    def on_theme_changed(self):
        """Handle theme change."""
        theme = self.theme_combo.currentData()
        self.theme_changed.emit(theme)
    
    def get_settings_dict(self):
        """
        Get settings as a dictionary.
        
        Returns:
            dict: Dictionary of settings
        """
        return {
            "theme": self.theme_combo.currentData().value,
            "startOnStartup": self.startup_check.isChecked(),
            "defaultCity": self.default_city_edit.text(),
            "weatherUnits": self.units_combo.currentData(),
            "apiKey": self.api_key_edit.text(),
            "weatherRefreshInterval": self.refresh_combo.currentData(),
            "alarmSound": self.alarm_sound_edit.text(),
            "alarmDuration": self.alarm_duration_combo.currentData(),
            "autoDismiss": self.auto_dismiss_check.isChecked()
        }