"""
Weather & Alarm Application
-------------------------
Main application module that integrates all components.
"""
import sys
import logging
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout,
    QWidget, QMessageBox, QSystemTrayIcon, QMenu, QStyle,
    QSizePolicy, QScrollArea, QFrame, QPushButton, QStackedWidget,
    QLabel, QToolButton, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import (
    Qt, QTimer, QTime, QSettings, QSize, QRect, 
    QPropertyAnimation, QEasingCurve, QPoint
)
from PyQt6.QtGui import (
    QIcon, QPixmap, QPainter, QAction, QGuiApplication, 
    QScreen, QFont, QColor, QCursor, QPainterPath, QRegion
)

from .widgets.weather_widget import WeatherWidget
from .widgets.alarm_widget import AlarmWidget
from .widgets.settings_widget import SettingsWidget
from .widgets.note_widget import NoteWidget
from .widgets.calendar_widget import CalendarWidget
from .widgets.weather_map_widget import WeatherMapWidget
from .widgets.notification_widget import NotificationWidget
from .utils.theme_manager import ThemeManager, Theme
from .utils.alarm_manager import AlarmManager
from .utils.notification_manager import NotificationManager
from .config import APP_ICON_PATH
from .utils.path_utils import get_icon_path

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

class SidebarButton(QPushButton):
    """Custom button for sidebar menu."""
    
    def __init__(self, text, icon_path=None, fallback_emoji=None, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedHeight(50)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Set custom font
        font = QFont("Protofo Regular", 14)
        self.setFont(font)
        
        # Store text and icon information
        self.full_text = text
        self.icon_path = icon_path
        self.fallback_emoji = fallback_emoji
        
        # Try to load SVG icon using get_icon_path, fall back to emoji if failed
        if icon_path:
            full_icon_path = get_icon_path(icon_path, "menu")
            if os.path.exists(full_icon_path):
                icon = QIcon(full_icon_path)
                self.setIcon(icon)
                self.setIconSize(QSize(24, 24))
                self.icon_only_text = ""
                logger.info(f"Successfully loaded icon: {full_icon_path}")
            else:
                self.icon_only_text = fallback_emoji
                logger.warning(f"Icon not found at {full_icon_path}, using emoji fallback")
        else:
            self.icon_only_text = fallback_emoji
        
        # Set initial state (collapsed)
        self.set_collapsed(True)
        
        # Set style
        self.setStyleSheet("""
            QPushButton {
                text-align: center;
                padding: 10px 15px;
                border: none;
                border-radius: 0;
                color: #94a3b8;
                background: transparent;
                font-size: 14px;
                font-family: 'Protofo Regular';
            }
            
            QPushButton:hover {
                color: #e2e8f0;
                background: rgba(255, 255, 255, 0.1);
            }
            
            QPushButton:checked {
                color: #ffffff;
                background: rgba(255, 255, 255, 0.15);
                border-left: 3px solid #1db954;
                padding-left: 12px;
            }
            
            QPushButton:checked:hover {
                background: rgba(255, 255, 255, 0.2);
            }
        """)
    
    def set_collapsed(self, collapsed):
        """Update button text based on collapsed state."""
        if collapsed:
            if self.icon_path and self.icon():
                self.setText("")  # Show only icon
            else:
                self.setText(self.fallback_emoji)  # Show emoji if no icon
            self.setStyleSheet(self.styleSheet().replace("text-align: left", "text-align: center"))
        else:
            self.setText(self.full_text)
            self.setStyleSheet(self.styleSheet().replace("text-align: center", "text-align: left"))
    
    def paintEvent(self, event):
        """Custom paint event to handle icon coloring."""
        # First, let the default implementation draw everything
        super().paintEvent(event)
        
        # Then, if we have an icon, draw our custom colored version on top
        if self.icon():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Get the icon pixmap
            icon_size = self.iconSize()
            pixmap = self.icon().pixmap(icon_size)
            
            # Create a new pixmap for colored version
            colored = QPixmap(pixmap.size())
            colored.fill(Qt.GlobalColor.transparent)
            
            # Create painter for the colored pixmap
            colored_painter = QPainter(colored)
            colored_painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Draw the original icon
            colored_painter.drawPixmap(0, 0, pixmap)
            
            # Apply color overlay - keep the same color in all states
            colored_painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
            colored_painter.fillRect(colored.rect(), QColor("#94a3b8"))  # Slate-300
            colored_painter.end()
            
            # Calculate position for the icon
            if not self.text():  # Collapsed state
                x = (self.width() - icon_size.width()) // 2
                y = (self.height() - icon_size.height()) // 2
            else:  # Expanded state
                x = 15  # Left-aligned icon
                y = (self.height() - icon_size.height()) // 2
            
            # Draw the colored icon
            painter.drawPixmap(x, y, colored)
            painter.end()
    
    def enterEvent(self, event):
        """Handle mouse enter event."""
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave event."""
        super().leaveEvent(event)
    
    def checkStateSet(self):
        """Handle check state changes."""
        super().checkStateSet()

class Sidebar(QWidget):
    """Spotify-like sidebar widget."""
    
    # Define menu items as class attribute with icon paths
    MENU_ITEMS = [
        ("Weather", "sun-solid.svg", "☀️"),
        ("Weather Map", "map-location-dot-solid.svg", "🗺️"),
        ("Alarms", "clock-solid.svg", "⏰"),
        ("Calendar", "calendar-check-solid.svg", "📅"),
        ("Notes", "note-sticky-solid.svg", "📝"),
        ("Notifications", "bell-solid.svg", "🔔"),
        ("Settings", "user-gear-solid.svg", "⚙️")
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(60)  # Start collapsed
        
        # Create width animation
        self._width_animation = QPropertyAnimation(self, b"minimumWidth", self)
        self._width_animation.setDuration(250)  # 250ms duration
        self._width_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Track collapsed state
        self._is_collapsed = True  # Start collapsed
        
        # Initialize UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the sidebar UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # App icon only (removed title)
        title_layout = QHBoxLayout()
        app_icon = QLabel()
        icon_pixmap = QIcon(APP_ICON_PATH).pixmap(QSize(32, 32))
        app_icon.setPixmap(icon_pixmap)
        app_icon.setStyleSheet("padding: 20px 10px;")
        
        title_layout.addWidget(app_icon)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("""
            QFrame {
                border: none;
                background-color: #282828;
                min-height: 1px;
                max-height: 1px;
            }
        """)
        layout.addWidget(separator)
        
        # Create menu buttons with icons
        self.buttons = []
        for text, icon_path, emoji in self.MENU_ITEMS:
            btn = SidebarButton(text, icon_path, emoji)
            self.buttons.append(btn)
            layout.addWidget(btn)
        
        # Add stretch at the bottom
        layout.addStretch()
        
        # Add collapse button at the bottom
        self.collapse_button = QPushButton("≡")  # Hamburger menu icon
        self.collapse_button.setFixedHeight(40)
        self.collapse_button.clicked.connect(self.toggle_collapse)
        self.collapse_button.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 0;
                color: #b3b3b3;
                background: transparent;
                font-size: 24px;
                padding: 5px;
            }
            QPushButton:hover {
                color: white;
                background: rgba(255, 255, 255, 0.1);
            }
        """)
        layout.addWidget(self.collapse_button)
        
        # Set background color
        self.setStyleSheet("""
            Sidebar {
                background-color: #121212;
                border-right: 1px solid #282828;
            }
        """)
    
    def toggle_collapse(self):
        """Toggle sidebar collapse state with animation."""
        if self._width_animation.state() == QPropertyAnimation.State.Running:
            return
        
        self._is_collapsed = not self._is_collapsed
        target_width = 60 if self._is_collapsed else 200
        
        # Animate the width
        self._width_animation.setStartValue(self.width())
        self._width_animation.setEndValue(target_width)
        self._width_animation.start()
        
        # Update button texts
        for button in self.buttons:
            button.set_collapsed(self._is_collapsed)
        
        # Update collapse button
        self.collapse_button.setText("≡")
    
    def enterEvent(self, event):
        """Handle mouse enter event."""
        if self._is_collapsed:
            self.toggle_collapse()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave event."""
        if not self._is_collapsed and not self.rect().contains(self.mapFromGlobal(QCursor.pos())):
            self.toggle_collapse()
        super().leaveEvent(event)

class TitleBar(QWidget):
    """Custom title bar for borderless window."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the title bar UI."""
        # Set fixed height
        self.setFixedHeight(32)
        
        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(0)
        
        # Add title label
        self.title_label = QLabel("Weather & Alarm")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(self.title_label)
        
        # Add spacer
        layout.addStretch()
        
        # Create window control buttons
        self.minimize_button = QToolButton()
        self.minimize_button.setFixedSize(30, 30)
        self.minimize_button.setText("—")
        self.minimize_button.setToolTip("Minimize")
        self.minimize_button.clicked.connect(self.parent.showMinimized)
        
        self.maximize_button = QToolButton()
        self.maximize_button.setFixedSize(30, 30)
        self.maximize_button.setText("□")
        self.maximize_button.setToolTip("Maximize")
        self.maximize_button.clicked.connect(self.toggle_maximize)
        
        self.close_button = QToolButton()
        self.close_button.setFixedSize(30, 30)
        self.close_button.setText("✕")
        self.close_button.setToolTip("Close")
        self.close_button.clicked.connect(self.parent.close)
        
        # Add buttons to layout
        layout.addWidget(self.minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(self.close_button)
        
    def toggle_maximize(self):
        """Toggle between maximized and normal window state."""
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.maximize_button.setText("□")
        else:
            self.parent.showMaximized()
            self.maximize_button.setText("❐")
            
    def mousePressEvent(self, event):
        """Handle mouse press events for window dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.parent._drag_pos = event.globalPosition().toPoint()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events for window dragging."""
        if event.buttons() & Qt.MouseButton.LeftButton and self.parent._drag_pos is not None:
            # Calculate the difference between current position and drag start position
            diff = event.globalPosition().toPoint() - self.parent._drag_pos
            # Move the window
            self.parent.move(self.parent.pos() + diff)
            # Update drag position
            self.parent._drag_pos = event.globalPosition().toPoint()
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events for window dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.parent._drag_pos = None
        super().mouseReleaseEvent(event)

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        # Set window flags for borderless mode
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # Disabled to prevent UpdateLayeredWindowIndirect error on Windows
        
        # Variables for window dragging
        self._drag_pos = None
        
        # Initialize managers
        self.theme_manager = ThemeManager()
        self.alarm_manager = AlarmManager()
        self.notification_manager = NotificationManager()
        
        # Set size policy for main window
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Set fixed default size
        self.setMinimumSize(800, 600)  # Minimum size for usability
        self.resize(1280, 720)  # Default size
        
        # Initialize UI
        self.init_ui()
        
        # Setup system tray
        self.setup_system_tray()
        
        # Apply default theme
        self.theme_manager.apply_theme(Theme.DARK)  # Changed to dark theme for Spotify-like look
        # Explicitly apply theme to all widgets
        self.apply_theme()
        
        # Add shadow effect
        self.add_shadow_effect()
        
        # Center window on screen
        self.center_on_screen()
        
        # Restore window state
        self.restore_window_state()
        
        # Set up clock timer
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)  # Update every second
        
        # Connect alarm signals
        self.alarm_manager.alarm_triggered.connect(self.on_alarm_triggered)
        self.alarm_manager.alarms_updated.connect(self.on_alarms_updated)
        
        logger.info("Application initialized with borderless window mode")
    
    def add_shadow_effect(self):
        """Add shadow effect to the window."""
        # Create shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 0)
        
        # Apply shadow to central widget
        self.centralWidget().setGraphicsEffect(shadow)
    
    def center_on_screen(self):
        """Center the window on the screen."""
        # Get the primary screen
        screen = QGuiApplication.primaryScreen()
        if not screen:
            return
            
        # Get available geometry
        available_geometry = screen.availableGeometry()
        
        # Calculate center point
        frame_geometry = self.frameGeometry()
        center_point = available_geometry.center()
        
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())
    
    def init_ui(self):
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle("Weather & Alarm")
        
        # Create central widget
        central_widget = QWidget()
        central_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Add custom title bar
        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)
        
        # Create content layout
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        main_layout.addLayout(content_layout)
        
        # Create sidebar
        self.sidebar = Sidebar()
        content_layout.addWidget(self.sidebar)
        
        # Create stacked widget for content
        self.content_stack = QStackedWidget()
        self.content_stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        content_layout.addWidget(self.content_stack)
        
        # Create and add widgets
        self.weather_widget = WeatherWidget()
        self.weather_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.content_stack.addWidget(self.create_scrollable_widget(self.weather_widget))
        
        self.weather_map_widget = WeatherMapWidget()
        self.weather_map_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.content_stack.addWidget(self.create_scrollable_widget(self.weather_map_widget))
        
        self.alarm_widget = AlarmWidget()
        self.alarm_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.content_stack.addWidget(self.create_scrollable_widget(self.alarm_widget))
        
        self.calendar_widget = CalendarWidget()
        self.calendar_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.content_stack.addWidget(self.create_scrollable_widget(self.calendar_widget))
        
        self.note_widget = NoteWidget()
        self.note_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.content_stack.addWidget(self.create_scrollable_widget(self.note_widget))
        
        self.notification_widget = NotificationWidget(self.notification_manager)
        self.notification_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.content_stack.addWidget(self.create_scrollable_widget(self.notification_widget))
        
        self.settings_widget = SettingsWidget()
        self.settings_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.content_stack.addWidget(self.create_scrollable_widget(self.settings_widget))
        
        # Connect sidebar buttons
        for i, button in enumerate(self.sidebar.buttons):
            button.clicked.connect(lambda checked, index=i: self.on_sidebar_button_clicked(index))
            if i == 0:  # Select first button by default
                button.setChecked(True)
        
        # Connect signals
        self.alarm_widget.alarm_added.connect(self.alarm_manager.add_alarm)
        self.alarm_widget.alarm_deleted.connect(self.alarm_manager.remove_alarm)
        self.settings_widget.theme_changed.connect(self.theme_manager.apply_theme)
        self.settings_widget.theme_changed.connect(lambda _: self.apply_theme())
        self.settings_widget.settings_changed.connect(self.on_settings_changed)
        self.weather_widget.weather_updated.connect(self.on_weather_updated)
        self.calendar_widget.event_updated.connect(self.on_calendar_event_updated)
        
        # Update alarm widget with current alarms
        self.alarm_widget.update_alarms(self.alarm_manager.get_alarms())
        
        # Apply initial settings
        settings_dict = self.settings_widget.get_settings_dict()
        if settings_dict:
            self.on_settings_changed(settings_dict)
    
    def create_scrollable_widget(self, widget):
        """Create a scrollable container for a widget."""
        scroll = QScrollArea()
        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # The scrollbar styling is now handled by the theme manager
        return scroll
    
    def on_sidebar_button_clicked(self, index):
        """Handle sidebar button clicks."""
        # Uncheck other buttons
        for i, button in enumerate(self.sidebar.buttons):
            if i != index:
                button.setChecked(False)
        
        # Switch to the corresponding widget
        self.content_stack.setCurrentIndex(index)
    
    def setup_system_tray(self):
        """Setup the system tray icon and menu."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            logger.warning("System tray is not available")
            return
        
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(APP_ICON_PATH))
        self.tray_icon.setToolTip("Weather & Alarm")
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)
        
        # Set the menu
        self.tray_icon.setContextMenu(tray_menu)
        
        # Show the icon
        self.tray_icon.show()
    
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
        
        # Add notification
        self.notification_manager.add_notification(
            "Alarm",
            f"Alarm at {time_str}{label_str} is ringing!",
            QSystemTrayIcon.MessageIcon.Information,
            "alarm"
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
            
        # Apply theme if provided - always use dark theme
        self.theme_manager.apply_theme(Theme.DARK)
        self.apply_theme()
    
    def on_weather_updated(self, weather_data):
        """
        Handle weather updated event.
        
        Args:
            weather_data (dict): Weather data
        """
        # Update weather map if coordinates are available
        if 'lat' in weather_data and 'lon' in weather_data:
            self.weather_map_widget.set_location(
                weather_data['lat'],
                weather_data['lon'],
                weather_data.get('city')
            )
            
            # Schedule a weather notification for tomorrow morning
            self.notification_manager.schedule_weather_notification(weather_data)
    
    def on_calendar_event_updated(self, event_data):
        """
        Handle calendar event updated event.
        
        Args:
            event_data (dict): Event data
        """
        # Schedule a notification for the event
        self.notification_manager.schedule_calendar_notification(event_data)
    
    def on_tray_activated(self, reason):
        """
        Handle tray icon activation.
        
        Args:
            reason (QSystemTrayIcon.ActivationReason): Reason for activation
        """
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # Show/hide the window on double click
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.tray_icon.isVisible():
            QMessageBox.information(
                self,
                "Weather & Alarm",
                "The application will keep running in the system tray. "
                "To terminate the program, choose Quit in the context menu "
                "of the system tray entry."
            )
            self.hide()
            event.ignore()
        else:
            self.save_window_state()
            event.accept()
    
    def save_window_state(self):
        """Save window state and geometry."""
        settings = QSettings()
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
    
    def restore_window_state(self):
        """Restore window state and geometry."""
        settings = QSettings()
        geometry = settings.value("geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)
        
        state = settings.value("windowState")
        if state is not None:
            self.restoreState(state)
    
    def apply_theme(self):
        """Apply dark theme to the application."""
        # Get stylesheet from theme manager
        stylesheet = self.theme_manager.get_stylesheet()
        
        # Add custom styles for borderless window
        custom_styles = """
        QMainWindow {
            background: transparent;
        }
        
        QWidget#centralWidget {
            background-color: #1e1e1e;
            border-radius: 10px;
            border: 1px solid #333333;
        }
        
        TitleBar {
            background-color: #1e1e1e;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            border-bottom: 1px solid #333333;
        }
        
        TitleBar QToolButton {
            background-color: transparent;
            border: none;
            color: #aaaaaa;
            font-weight: bold;
        }
        
        TitleBar QToolButton:hover {
            background-color: #333333;
            color: #ffffff;
        }
        
        TitleBar QToolButton#closeButton:hover {
            background-color: #e81123;
            color: #ffffff;
        }
        
        /* Fix for missing check.svg icon */
        QCheckBox::indicator:checked {
            image: none;
            background-color: #4CAF50;
            border: 1px solid #2E7D32;
            border-radius: 2px;
        }
        
        QCheckBox::indicator:unchecked {
            image: none;
            background-color: #424242;
            border: 1px solid #757575;
            border-radius: 2px;
        }
        
        /* Fix for missing chevron-down.svg icon */
        QComboBox::down-arrow {
            image: none;
            width: 0;
            height: 0;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #aaaaaa;
            margin-right: 5px;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        """
        
        # Combine stylesheets
        combined_stylesheet = stylesheet + custom_styles
        
        # Apply stylesheet to the main application
        QApplication.instance().setStyleSheet(combined_stylesheet)
        
        # Apply theme to individual widgets for more specific styling
        for widget in [
            self.weather_widget, self.alarm_widget, self.note_widget, 
            self.settings_widget, self.calendar_widget, self.weather_map_widget,
            self.notification_widget, self.content_stack, self.centralWidget(),
            self.sidebar, self.title_bar
        ]:
            if hasattr(widget, 'setStyleSheet'):
                widget.setStyleSheet(combined_stylesheet)
                
            # If widget has a method to apply theme, call it
            if hasattr(widget, 'apply_theme'):
                widget.apply_theme()
        
        # Set object name for central widget to apply specific styles
        self.centralWidget().setObjectName("centralWidget")
        
        # Set object name for close button to apply specific styles
        self.title_bar.close_button.setObjectName("closeButton")
        
        # Apply theme to all scroll areas in the application
        self.apply_theme_to_scroll_areas(self)
        
        # Force update of all widgets to ensure theme is applied
        QApplication.processEvents()
        
        # Ensure the sidebar is properly styled
        if hasattr(self.sidebar, 'update'):
            self.sidebar.update()
        
        logger.info("Applied dark theme with borderless styling")
    
    def apply_theme_to_scroll_areas(self, parent_widget):
        """
        Recursively apply theme to all scroll areas in the widget hierarchy.
        
        Args:
            parent_widget (QWidget): The parent widget to start the search from
        """
        # Get stylesheet from theme manager
        stylesheet = self.theme_manager.get_stylesheet()
        
        # Add custom styles for borderless window
        custom_styles = """
        QMainWindow {
            background: transparent;
        }
        
        QWidget#centralWidget {
            background-color: #1e1e1e;
            border-radius: 10px;
            border: 1px solid #333333;
        }
        
        TitleBar {
            background-color: #1e1e1e;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            border-bottom: 1px solid #333333;
        }
        
        TitleBar QToolButton {
            background-color: transparent;
            border: none;
            color: #aaaaaa;
            font-weight: bold;
        }
        
        TitleBar QToolButton:hover {
            background-color: #333333;
            color: #ffffff;
        }
        
        TitleBar QToolButton#closeButton:hover {
            background-color: #e81123;
            color: #ffffff;
        }
        
        /* Fix for missing check.svg icon */
        QCheckBox::indicator:checked {
            image: none;
            background-color: #4CAF50;
            border: 1px solid #2E7D32;
            border-radius: 2px;
        }
        
        QCheckBox::indicator:unchecked {
            image: none;
            background-color: #424242;
            border: 1px solid #757575;
            border-radius: 2px;
        }
        
        /* Fix for missing chevron-down.svg icon */
        QComboBox::down-arrow {
            image: none;
            width: 0;
            height: 0;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #aaaaaa;
            margin-right: 5px;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        """
        
        # Combine stylesheets
        combined_stylesheet = stylesheet + custom_styles
        
        # Find all scroll areas in the widget hierarchy
        for child in parent_widget.findChildren(QScrollArea):
            child.setStyleSheet(combined_stylesheet)
            
            # Also apply to the viewport and its children
            if child.viewport():
                child.viewport().setStyleSheet(combined_stylesheet)

    def resizeEvent(self, event):
        """Handle window resize events."""
        super().resizeEvent(event)
        # Ensure all widgets update their layouts
        self.centralWidget().updateGeometry()
        self.content_stack.updateGeometry()
        
        # Log resize for debugging
        logger.debug(f"Window resized to {event.size().width()}x{event.size().height()}")

    def mousePressEvent(self, event):
        """Handle mouse press events for window dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events for window dragging."""
        if event.buttons() & Qt.MouseButton.LeftButton and self._drag_pos is not None:
            # Calculate the difference between current position and drag start position
            diff = event.globalPosition().toPoint() - self._drag_pos
            # Move the window
            self.move(self.pos() + diff)
            # Update drag position
            self._drag_pos = event.globalPosition().toPoint()
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events for window dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = None
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        """Custom paint event to draw shadow and rounded corners."""
        # Create a painter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # No need to draw background as we're using stylesheet for that
        painter.end()

def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Weather & Alarm")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("WACApp")
    app.setOrganizationDomain("wacapp.local")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 