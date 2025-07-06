"""
Weather & Alarm Application Main Class
-------------------------------------
This module contains the main application class for the Weather & Alarm application.
"""
import sys
import os
import json
import requests
from datetime import datetime
import time
import shutil

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QTabWidget, QStyleFactory, QMessageBox)
from PyQt6.QtCore import Qt, QTime, QTimer, QSettings
from PyQt6.QtGui import QIcon, QPalette, QColor
from qt_material import apply_stylesheet, list_themes

# Import widgets
from ..widgets.weather_widget import WeatherWidget
from ..widgets.alarm_widget import AlarmWidget
from ..widgets.settings_widget import SettingsWidget

# Import from utils
from ..utils.theme_utils import ThemeManager
from ..utils.svg_utils import ensure_icon_exists, ensure_weather_icons_dir, ensure_all_weather_svg_files

# Import from services
from ..services.weather_service import WeatherService
from ..services.alarm_service import AlarmThread

# Import configuration
from ..config import (
    API_KEY, 
    WEATHER_API_URL, 
    ONECALL_API_URL, 
    AIR_QUALITY_API_URL,
    WEATHER_REFRESH_INTERVAL,
    TIME_REFRESH_INTERVAL,
    APP_ICON_PATH,
    SCRIPT_DIR,
    WEATHER_ICONS_DIR,
    EXTERNAL_WEATHER_ICONS_PATH
)

class WeatherAlarmApp(QMainWindow):
    """Main application class"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weather & Alarm App")
        self.setGeometry(100, 100, 800, 600)
        
        # Set application icon
        try:
            if os.path.exists(APP_ICON_PATH):
                self.setWindowIcon(QIcon(APP_ICON_PATH))
            else:
                print(f"Warning: Icon file not found at {APP_ICON_PATH}")
        except Exception as e:
            print(f"Error setting application icon: {str(e)}")
        
        # Initialize settings
        self.settings = QSettings("WACAppPush", "settings")
        
        # Set dark mode as the only theme option
        self.settings.setValue("theme", "dark")
        
        # Load saved API key if available
        saved_api_key = self.settings.value("API_KEY", "")
        if saved_api_key:
            global API_KEY
            API_KEY = saved_api_key
        
        # Create theme manager (dark mode only)
        self.theme_manager = ThemeManager()
        
        # Initialize weather service
        self.weather_service = WeatherService()
        
        # Initialize UI
        self.init_ui()
        
        # Initialize variables
        self.alarm_threads = []
        self.alarms = []
        self.current_location = ""
        
        # Set up timers
        self.setup_timers()
        
        # Apply dark theme
        self.apply_theme()
        
    def init_ui(self):
        """Initialize the user interface"""
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Create tabs
        tabs = QTabWidget()
        tabs.currentChanged.connect(self.on_tab_changed)
        main_layout.addWidget(tabs)
        
        # Weather tab
        self.weather_widget = WeatherWidget(self)
        
        # Alarm tab
        self.alarm_widget = AlarmWidget(self)
        self.alarm_widget.alarm_added.connect(self.add_alarm)
        self.alarm_widget.alarm_deleted.connect(self.delete_alarm)
        
        # Settings tab
        self.settings_widget = SettingsWidget(self)
        # Theme-related connections are kept for compatibility but will have no effect
        # since we're now using dark mode exclusively
        self.settings_widget.theme_changed.connect(self.on_theme_changed)
        self.settings_widget.api_key_changed.connect(self.on_api_key_changed)
        
        # Set current settings - simplified for dark mode only
        self.settings_widget.set_current_settings(
            Theme.DARK,  # Always dark theme
            self.api_key
        )
        
        # Add tabs to tab widget
        tabs.addTab(self.weather_widget, "Weather")
        tabs.addTab(self.alarm_widget, "Alarm")
        tabs.addTab(self.settings_widget, "Settings")
        
    def setup_timers(self):
        """Set up the application timers"""
        # Update time every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(TIME_REFRESH_INTERVAL)
        
        # Update weather periodically if a location is set
        self.weather_timer = QTimer(self)
        self.weather_timer.timeout.connect(self.refresh_weather)
        self.weather_timer.start(WEATHER_REFRESH_INTERVAL)
        
        # Update time initially
        self.update_time()
        
    def on_tab_changed(self, index):
        """Handle tab change to maintain state between tabs"""
        # When switching to the weather tab, refresh the weather if a location is set
        if index == 0:  # Weather tab
            if hasattr(self, 'current_location') and self.current_location:
                self.refresh_weather()
            
        # When switching to the alarm tab, update the alarm list
        elif index == 1:  # Alarm tab
            self.refresh_alarm_list()
    
    def refresh_alarm_list(self):
        """Refresh the alarm list to ensure it matches the current state"""
        # First clear the list
        self.alarm_widget.alarms_list.clear()
        
        # Add all current alarms
        for i, alarm_time in enumerate(self.alarms):
            alarm_text = alarm_time.toString("HH:mm")
            
            # Check if this alarm has auto-dismiss
            if i < len(self.alarm_threads) and hasattr(self.alarm_threads[i], 'auto_dismiss_seconds'):
                auto_dismiss = self.alarm_threads[i].auto_dismiss_seconds
                if auto_dismiss > 0:
                    alarm_text += f" (Auto-dismiss: {auto_dismiss}s)"
                    
            self.alarm_widget.alarms_list.addItem(alarm_text)
    
    def update_time(self):
        """Update the time display"""
        current_time = QTime.currentTime()
        self.weather_widget.update_time(current_time)
    
    def refresh_weather(self):
        """Refresh weather data if a location is set"""
        if self.current_location:
            self.get_weather(self.current_location)
    
    def get_weather(self, city):
        """Fetch and process weather data for the given city"""
        self.current_location = city
        
        try:
            weather_data = self.weather_service.get_weather_data(city)
            if weather_data:
                self.weather_widget.update_weather_display(weather_data)
            else:
                QMessageBox.warning(self, "Weather Error", "Could not retrieve weather data.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def add_alarm(self, alarm_time, auto_dismiss=0):
        """Add a new alarm"""
        self.alarms.append(alarm_time)
        
        # Create and start alarm thread
        alarm_thread = AlarmThread(alarm_time, len(self.alarms) - 1, auto_dismiss)
        alarm_thread.alarm_signal.connect(self.trigger_alarm)
        alarm_thread.start()
        
        self.alarm_threads.append(alarm_thread)
    
    def delete_alarm(self, index):
        """Delete an alarm at the given index"""
        if index < len(self.alarm_threads):
            self.alarm_threads[index].stop()
            self.alarm_threads.pop(index)
            self.alarms.pop(index)
    
    def trigger_alarm(self, alarm_time, index):
        """Handle a triggered alarm"""
        QMessageBox.information(self, "Alarm", f"Alarm time: {alarm_time}")
        
        # Remove the triggered alarm
        self.alarms.pop(index)
        self.alarm_widget.remove_triggered_alarm(alarm_time)
    
    def apply_theme(self):
        """Apply dark theme to the application"""
        app = QApplication.instance()
        self.theme_manager.apply_theme()
    
    # Settings event handlers - simplified for dark mode only
    def on_theme_changed(self, theme):
        # Always use dark theme, kept for compatibility
        pass
    
    def on_api_key_changed(self, api_key):
        global API_KEY
        API_KEY = api_key
        self.settings.setValue("API_KEY", API_KEY)
        self.weather_service.set_api_key(api_key)
        # Refresh weather if a location is set
        if self.current_location:
            self.refresh_weather() 