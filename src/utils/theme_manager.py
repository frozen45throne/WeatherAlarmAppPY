"""
Theme Manager Module
-----------------
This module provides the ThemeManager class for managing application themes in the Weather & Alarm application.
The application now exclusively uses dark mode.
"""
import logging
from enum import Enum
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QApplication

# Configure logging
logger = logging.getLogger(__name__)

class Theme(Enum):
    """Enum representing available themes (only dark mode now)."""
    DARK = "dark"

class ThemeManager:
    """Manager for handling application themes (dark mode only)."""
    
    # Define color palette for dark theme
    DARK_PALETTE = {
        QPalette.ColorRole.Window: QColor(33, 33, 33),           # Darker background
        QPalette.ColorRole.WindowText: QColor(255, 255, 255),    # White text
        QPalette.ColorRole.Base: QColor(18, 18, 18),             # Even darker for input fields
        QPalette.ColorRole.AlternateBase: QColor(45, 45, 45),    # Slightly lighter for alternating rows
        QPalette.ColorRole.ToolTipBase: QColor(33, 33, 33),      # Dark tooltip background
        QPalette.ColorRole.ToolTipText: QColor(255, 255, 255),   # White tooltip text
        QPalette.ColorRole.Text: QColor(255, 255, 255),          # White text
        QPalette.ColorRole.Button: QColor(45, 45, 45),           # Slightly lighter for buttons
        QPalette.ColorRole.ButtonText: QColor(255, 255, 255),    # White button text
        QPalette.ColorRole.BrightText: QColor(255, 128, 128),    # Light red for bright text
        QPalette.ColorRole.Link: QColor(66, 165, 245),           # Lighter blue for links
        QPalette.ColorRole.Highlight: QColor(33, 150, 243),      # Blue highlight
        QPalette.ColorRole.HighlightedText: QColor(255, 255, 255), # White text on highlight
        QPalette.ColorGroup.Disabled: {                           # Disabled state colors
            QPalette.ColorRole.WindowText: QColor(128, 128, 128),
            QPalette.ColorRole.Text: QColor(128, 128, 128),
            QPalette.ColorRole.ButtonText: QColor(128, 128, 128),
            QPalette.ColorRole.Highlight: QColor(80, 80, 80),
            QPalette.ColorRole.HighlightedText: QColor(180, 180, 180)
        }
    }
    
    # Material Design color scheme for dark mode
    MATERIAL_DARK = {
        "primary": QColor(33, 150, 243),        # Blue 500
        "primary_light": QColor(100, 181, 246), # Blue 300
        "primary_dark": QColor(25, 118, 210),   # Blue 700
        "accent": QColor(255, 64, 129),         # Pink A400
        "text_primary": QColor(255, 255, 255),  # White
        "text_secondary": QColor(189, 189, 189), # Grey 400
        "divider": QColor(66, 66, 66),          # Darker divider
        "background": QColor(33, 33, 33),       # Darker background
        "card": QColor(45, 45, 45),             # Slightly lighter card background
        "error": QColor(244, 67, 54),           # Red 500
        "surface": QColor(18, 18, 18),          # Even darker surface
        "on_surface": QColor(255, 255, 255),    # White text on surface
        "disabled": QColor(97, 97, 97),         # Grey 700 for disabled elements
        "hover": QColor(55, 55, 55),            # Slightly lighter for hover states
        "selected": QColor(66, 165, 245, 50)    # Semi-transparent blue for selected items
    }
    
    def __init__(self):
        """Initialize the theme manager with dark mode."""
        self.current_theme = Theme.DARK
        self.material_colors = self.MATERIAL_DARK
        
        # Apply dark theme
        self.apply_theme()
    
    def apply_theme(self, theme=None):
        """
        Apply dark theme to the application.
        
        Args:
            theme: Parameter kept for compatibility but ignored (always applies dark theme)
        """
        app = QApplication.instance()
        
        if app:
            # Create palette
            palette = QPalette()
            
            # Apply dark theme
            for role, color in self.DARK_PALETTE.items():
                if role != QPalette.ColorGroup.Disabled:
                    palette.setColor(role, color)
                    
            # Handle disabled state separately
            if QPalette.ColorGroup.Disabled in self.DARK_PALETTE:
                disabled_colors = self.DARK_PALETTE[QPalette.ColorGroup.Disabled]
                for role, color in disabled_colors.items():
                    palette.setColor(QPalette.ColorGroup.Disabled, role, color)
                    
            self.material_colors = self.MATERIAL_DARK
            
            # Apply palette to application
            app.setPalette(palette)
            
            logger.info("Applied dark theme")
        else:
            logger.warning("No QApplication instance found. Theme not applied.")
    
    def get_color(self, color_name):
        """
        Get a color from the material design color scheme.
        
        Args:
            color_name (str): Name of the color to get
            
        Returns:
            QColor: The requested color or primary color if not found
        """
        return self.material_colors.get(color_name, self.material_colors["primary"])
    
    def get_stylesheet(self):
        """
        Get a stylesheet for the dark theme.
        
        Returns:
            str: CSS stylesheet for the dark theme
        """
        # Convert material colors to CSS variables
        colors = {name: f"rgb({color.red()}, {color.green()}, {color.blue()})" 
                 for name, color in self.material_colors.items()}
        
        # Create a stylesheet with CSS variables
        stylesheet = f"""
        /* Base Styles */
        QWidget {{
            background-color: {colors['background']};
            color: {colors['text_primary']};
        }}
        
        QMainWindow, QDialog {{
            background-color: {colors['background']};
        }}
        
        QFrame {{
            background-color: {colors.get('surface', colors['card'])};
            border-radius: 4px;
        }}
        
        QPushButton {{
            background-color: {colors['primary']};
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: {colors['primary_dark']};
        }}
        
        QPushButton:pressed {{
            background-color: {colors['primary_light']};
        }}
        
        QPushButton:disabled {{
            background-color: {colors.get('disabled', 'rgb(97, 97, 97)')};
            color: rgba(255, 255, 255, 0.5);
        }}
        
        QLineEdit, QComboBox, QSpinBox, QTimeEdit, QDateEdit, QDateTimeEdit {{
            border: 1px solid {colors['divider']};
            border-radius: 4px;
            padding: 8px;
            background-color: {colors.get('surface', colors['card'])};
            color: {colors['text_primary']};
            selection-background-color: {colors['primary']};
            selection-color: white;
        }}
        
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTimeEdit:focus, QDateEdit:focus, QDateTimeEdit:focus {{
            border: 1px solid {colors['primary']};
        }}
        
        QLabel {{
            color: {colors['text_primary']};
            background-color: transparent;
        }}
        
        QTabWidget::pane {{
            border: 1px solid {colors['divider']};
            border-radius: 4px;
            background-color: {colors['card']};
        }}
        
        QTabBar::tab {{
            background-color: {colors['background']};
            color: {colors['text_secondary']};
            padding: 8px 16px;
            border-bottom: 2px solid transparent;
        }}
        
        QTabBar::tab:selected {{
            color: {colors['primary']};
            border-bottom: 2px solid {colors['primary']};
        }}
        
        QTabBar::tab:hover:!selected {{
            color: {colors['text_primary']};
            background-color: {colors.get('hover', 'rgb(55, 55, 55)')};
        }}
        
        /* Calendar Widget Styling */
        QCalendarWidget {{
            background-color: {colors['background']};
            color: {colors['text_primary']};
        }}
        
        QCalendarWidget QWidget {{
            alternate-background-color: {colors['card']};
        }}
        
        QCalendarWidget QAbstractItemView:enabled {{
            background-color: {colors['background']};
            color: {colors['text_primary']};
            selection-background-color: {colors['primary']};
            selection-color: white;
        }}
        
        QCalendarWidget QAbstractItemView:disabled {{
            color: {colors.get('disabled', 'rgb(97, 97, 97)')};
        }}
        
        QCalendarWidget QMenu {{
            background-color: {colors['card']};
            color: {colors['text_primary']};
        }}
        
        QCalendarWidget QToolButton {{
            background-color: transparent;
            color: {colors['text_primary']};
            border: none;
            border-radius: 4px;
            padding: 4px;
            margin: 2px;
        }}
        
        QCalendarWidget QToolButton:hover {{
            background-color: {colors.get('hover', 'rgba(255, 255, 255, 0.1)')};
        }}
        
        QCalendarWidget QToolButton:pressed {{
            background-color: {colors.get('selected', 'rgba(66, 165, 245, 0.2)')};
        }}
        
        QCalendarWidget QToolButton::menu-indicator {{
            image: none;
        }}
        
        QCalendarWidget QSpinBox {{
            background-color: {colors['card']};
            color: {colors['text_primary']};
            border: 1px solid {colors['divider']};
            border-radius: 4px;
            padding: 2px;
        }}
        
        QCalendarWidget QTableView {{
            alternate-background-color: {colors.get('surface', colors['card'])};
            background-color: {colors['background']};
            selection-background-color: {colors['primary']};
            selection-color: white;
        }}
        
        /* Custom styling for calendar cells */
        QCalendarWidget QTableView::item:selected {{
            background-color: {colors['primary']};
            color: white;
        }}
        
        QCalendarWidget QTableView::item:hover {{
            background-color: {colors.get('hover', 'rgba(255, 255, 255, 0.1)')};
        }}
        
        /* Custom Scrollbar Styling */
        QScrollBar:vertical {{
            background-color: {colors['background']};
            width: 6px;
            margin: 0px;
            border-radius: 3px;
            border: none;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {colors.get('divider', 'rgb(66, 66, 66)')};
            min-height: 30px;
            border-radius: 3px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {colors['primary']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
            background: none;
            border: none;
        }}
        
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
            border: none;
        }}
        
        QScrollBar:horizontal {{
            background-color: {colors['background']};
            height: 6px;
            margin: 0px;
            border-radius: 3px;
            border: none;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {colors.get('divider', 'rgb(66, 66, 66)')};
            min-width: 30px;
            border-radius: 3px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {colors['primary']};
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
            background: none;
            border: none;
        }}
        
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            background: none;
            border: none;
        }}
        
        QScrollArea {{
            background-color: transparent;
            border: none;
        }}
        
        QScrollArea > QWidget > QWidget {{
            background-color: transparent;
        }}
        
        QMenu {{
            background-color: {colors['card']};
            border: 1px solid {colors['divider']};
            border-radius: 4px;
        }}
        
        QMenu::item {{
            padding: 6px 16px;
            color: {colors['text_primary']};
        }}
        
        QMenu::item:selected {{
            background-color: {colors.get('selected', 'rgba(66, 165, 245, 0.2)')};
        }}
        
        QCheckBox {{
            color: {colors['text_primary']};
            background-color: transparent;
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 1px solid {colors['divider']};
            border-radius: 2px;
            background-color: {colors.get('surface', colors['card'])};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {colors['primary']};
            border-color: {colors['primary']};
        }}
        
        QGroupBox {{
            border: 1px solid {colors['divider']};
            border-radius: 4px;
            margin-top: 1.5ex;
            padding-top: 1ex;
            font-weight: bold;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 3px;
            color: {colors['text_primary']};
            background-color: transparent;
        }}
        
        QListView, QTreeView, QTableView {{
            background-color: {colors.get('surface', colors['card'])};
            border: 1px solid {colors['divider']};
            border-radius: 4px;
            alternate-background-color: {colors.get('hover', 'rgb(55, 55, 55)')};
        }}
        
        QListView::item:selected, QTreeView::item:selected, QTableView::item:selected {{
            background-color: {colors.get('selected', 'rgba(66, 165, 245, 0.2)')};
            color: {colors['text_primary']};
        }}
        
        QHeaderView::section {{
            background-color: {colors['card']};
            color: {colors['text_secondary']};
            padding: 4px;
            border: none;
            border-right: 1px solid {colors['divider']};
            border-bottom: 1px solid {colors['divider']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        QComboBox::down-arrow {{
            image: url(:/icons/arrow_down.png);
            width: 12px;
            height: 12px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {colors['card']};
            border: 1px solid {colors['divider']};
            selection-background-color: {colors.get('selected', 'rgba(66, 165, 245, 0.2)')};
            selection-color: {colors['text_primary']};
        }}
        
        QSpinBox::up-button, QSpinBox::down-button,
        QTimeEdit::up-button, QTimeEdit::down-button,
        QDateEdit::up-button, QDateEdit::down-button,
        QDateTimeEdit::up-button, QDateTimeEdit::down-button {{
            background-color: {colors['card']};
            border: none;
            width: 16px;
            border-radius: 2px;
        }}
        
        QSpinBox::up-button:hover, QSpinBox::down-button:hover,
        QTimeEdit::up-button:hover, QTimeEdit::down-button:hover,
        QDateEdit::up-button:hover, QDateEdit::down-button:hover,
        QDateTimeEdit::up-button:hover, QDateTimeEdit::down-button:hover {{
            background-color: {colors.get('hover', 'rgb(55, 55, 55)')};
        }}
        
        QSpinBox::up-arrow, QTimeEdit::up-arrow, QDateEdit::up-arrow, QDateTimeEdit::up-arrow {{
            image: url(:/icons/arrow_up.png);
            width: 12px;
            height: 12px;
        }}
        
        QSpinBox::down-arrow, QTimeEdit::down-arrow, QDateEdit::down-arrow, QDateTimeEdit::down-arrow {{
            image: url(:/icons/arrow_down.png);
            width: 12px;
            height: 12px;
        }}
        
        QProgressBar {{
            border: 1px solid {colors['divider']};
            border-radius: 4px;
            background-color: {colors['card']};
            text-align: center;
            color: {colors['text_primary']};
        }}
        
        QProgressBar::chunk {{
            background-color: {colors['primary']};
            border-radius: 3px;
        }}
        
        QSlider::groove:horizontal {{
            border: none;
            height: 4px;
            background-color: {colors['card']};
            border-radius: 2px;
        }}
        
        QSlider::handle:horizontal {{
            background-color: {colors['primary']};
            border: none;
            width: 16px;
            height: 16px;
            margin: -6px 0;
            border-radius: 8px;
        }}
        
        QSlider::handle:horizontal:hover {{
            background-color: {colors['primary_light']};
        }}
        
        QSlider::add-page:horizontal {{
            background-color: {colors['card']};
        }}
        
        QSlider::sub-page:horizontal {{
            background-color: {colors['primary']};
        }}
        """
        
        return stylesheet 