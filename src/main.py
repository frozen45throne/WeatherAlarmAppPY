"""
Weather & Alarm Application
-------------------------
Main application module that integrates all components.
"""
import sys
import logging
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QVBoxLayout, 
    QWidget, QMessageBox, QSystemTrayIcon, QMenu, QAction
)
from PyQt5.QtCore import Qt, QTimer, QTime
from PyQt5.QtGui import QIcon, QPixmap, QPainter

from .widgets.weather_widget import WeatherWidget
from .widgets.alarm_widget import AlarmWidget
from .widgets.settings_widget import SettingsWidget
from .utils.theme_manager import ThemeManager, Theme
from .utils.alarm_manager import AlarmManager
from .config import APP_ICON_PATH

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('wacapp.log')
    ]
)
logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        # Set up window properties
        self.setWindowTitle("Weather & Alarm")
        self.setMinimumSize(800, 600)
        
        # Set up icon
        icon = None
        if os.path.exists(APP_ICON_PATH):
            icon = QIcon(APP_ICON_PATH)
            if not icon.isNull():
                self.setWindowIcon(icon)
            else:
                logger.warning(f"Failed to load app icon from {APP_ICON_PATH}")
        else:
            logger.warning(f"App icon not found at {APP_ICON_PATH}")
        
        # Initialize managers
        self.theme_manager = ThemeManager()
        self.alarm_manager = AlarmManager()
        
        # Initialize UI
        self.init_ui()
        
        # Set up system tray with icon
        self.setup_system_tray(icon)
        
        # Set up clock timer
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)  # Update every second
        
        # Connect alarm signals
        self.alarm_manager.alarm_triggered.connect(self.on_alarm_triggered)
        self.alarm_manager.alarms_updated.connect(self.on_alarms_updated)
        
        # Apply theme
        self.apply_theme()
        
        logger.info("Application initialized")
    
    def init_ui(self):
        """Initialize the user interface."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create weather widget
        self.weather_widget = WeatherWidget()
        self.tab_widget.addTab(self.weather_widget, "Weather")
        
        # Create alarm widget
        self.alarm_widget = AlarmWidget()
        self.tab_widget.addTab(self.alarm_widget, "Alarms")
        
        # Create settings widget
        self.settings_widget = SettingsWidget()
        self.tab_widget.addTab(self.settings_widget, "Settings")
        
        # Add tab widget to main layout
        main_layout.addWidget(self.tab_widget)
        
        # Connect signals
        self.alarm_widget.alarm_added.connect(self.alarm_manager.add_alarm)
        self.alarm_widget.alarm_deleted.connect(self.alarm_manager.remove_alarm)
        self.settings_widget.theme_changed.connect(self.theme_manager.apply_theme)
        self.settings_widget.settings_changed.connect(self.on_settings_changed)
        
        # Update alarm widget with current alarms
        self.alarm_widget.update_alarms(self.alarm_manager.get_alarms())
    
    def setup_system_tray(self, icon=None):
        """
        Set up system tray icon and menu.
        
        Args:
            icon (QIcon, optional): Icon to use for the system tray
        """
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        
        # Set icon
        if os.path.exists(APP_ICON_PATH):
            icon = QIcon(APP_ICON_PATH)
            if not icon.isNull():
                self.tray_icon.setIcon(icon)
            else:
                logger.warning(f"Failed to load app icon from {APP_ICON_PATH}")
                self._create_default_tray_icon()
        else:
            logger.warning(f"App icon not found at {APP_ICON_PATH}")
            self._create_default_tray_icon()
        
        # Create tray menu
        tray_menu = QMenu()
        
        # Add actions
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.on_quit)
        
        # Add actions to menu
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        
        # Set tray menu
        self.tray_icon.setContextMenu(tray_menu)
        
        # Connect activated signal
        self.tray_icon.activated.connect(self.on_tray_activated)
        
        # Show tray icon
        self.tray_icon.show()
    
    def _create_default_tray_icon(self):
        """Create and set a default icon for the system tray"""
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setPen(Qt.black)
        painter.setBrush(Qt.black)
        painter.drawEllipse(8, 8, 16, 16)  # Draw a simple circle
        painter.end()
        self.tray_icon.setIcon(QIcon(pixmap))
        logger.warning("Using default icon for system tray")
    
    def update_clock(self):
        """Update the clock in the status bar."""
        current_time = QTime.currentTime()
        time_text = current_time.toString("hh:mm:ss")
        self.statusBar().showMessage(f"Current Time: {time_text}")
    
    def on_alarm_triggered(self, alarm):
        """
        Handle alarm triggered event.
        
        Args:
            alarm (Alarm): The triggered alarm
        """
        # Show notification
        time_str = alarm.time.toString("HH:mm")
        label_str = f" - {alarm.label}" if alarm.label else ""
        
        self.tray_icon.showMessage(
            "Alarm",
            f"Alarm at {time_str}{label_str} is ringing!",
            QSystemTrayIcon.Information,
            5000  # Show for 5 seconds
        )
        
        # Show message box if application is visible
        if self.isVisible():
            QMessageBox.information(
                self,
                "Alarm",
                f"Alarm at {time_str}{label_str} is ringing!"
            )
        
        logger.info(f"Alarm triggered: {alarm}")
    
    def on_alarms_updated(self, alarms):
        """
        Handle alarms updated event.
        
        Args:
            alarms (list): List of Alarm objects
        """
        # Update alarm widget
        self.alarm_widget.update_alarms(alarms)
    
    def on_settings_changed(self, settings):
        """
        Handle settings changed event.
        
        Args:
            settings (dict): Dictionary of settings
        """
        # Apply settings
        logger.info("Settings changed, applying new settings")
        
        # Set default city if provided
        default_city = settings.get("defaultCity")
        if default_city:
            self.weather_widget.set_city(default_city)
    
    def on_tray_activated(self, reason):
        """
        Handle tray icon activated event.
        
        Args:
            reason (QSystemTrayIcon.ActivationReason): Reason for activation
        """
        if reason == QSystemTrayIcon.DoubleClick:
            # Toggle visibility on double click
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()
    
    def on_quit(self):
        """Handle quit action."""
        # Confirm quit
        confirm = QMessageBox.question(
            self,
            "Confirm Quit",
            "Are you sure you want to quit the application?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            # Quit application
            QApplication.quit()
    
    def apply_theme(self):
        """Apply the current theme."""
        # Get stylesheet from theme manager
        stylesheet = self.theme_manager.get_stylesheet()
        
        # Apply stylesheet
        self.setStyleSheet(stylesheet)
    
    def closeEvent(self, event):
        """
        Handle close event.
        
        Args:
            event (QCloseEvent): Close event
        """
        # Minimize to tray instead of closing
        event.ignore()
        self.hide()
        
        # Show notification
        self.tray_icon.showMessage(
            "Weather & Alarm",
            "Application minimized to tray. Double-click the tray icon to restore.",
            QSystemTrayIcon.Information,
            3000  # Show for 3 seconds
        )


def main():
    """Main entry point for the application."""
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Weather & Alarm")
    app.setQuitOnLastWindowClosed(False)
    
    # Create main window
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 