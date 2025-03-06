"""
Theme Manager Utility
-------------------
This module provides utilities for managing application themes in the Weather & Alarm application.
"""
import logging
from enum import Enum
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QApplication

# Configure logging
logger = logging.getLogger(__name__)

class Theme(Enum):
    """Enum representing available themes."""
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"

class ThemeManager:
    """Manager for handling application themes."""
    
    # Define color palettes for different themes
    LIGHT_PALETTE = {
        QPalette.Window: QColor(240, 240, 240),
        QPalette.WindowText: QColor(0, 0, 0),
        QPalette.Base: QColor(255, 255, 255),
        QPalette.AlternateBase: QColor(233, 233, 233),
        QPalette.ToolTipBase: QColor(255, 255, 255),
        QPalette.ToolTipText: QColor(0, 0, 0),
        QPalette.Text: QColor(0, 0, 0),
        QPalette.Button: QColor(240, 240, 240),
        QPalette.ButtonText: QColor(0, 0, 0),
        QPalette.BrightText: QColor(255, 0, 0),
        QPalette.Link: QColor(42, 130, 218),
        QPalette.Highlight: QColor(42, 130, 218),
        QPalette.HighlightedText: QColor(255, 255, 255),
    }
    
    DARK_PALETTE = {
        QPalette.Window: QColor(33, 33, 33),           # Darker background
        QPalette.WindowText: QColor(255, 255, 255),    # White text
        QPalette.Base: QColor(18, 18, 18),             # Even darker for input fields
        QPalette.AlternateBase: QColor(45, 45, 45),    # Slightly lighter for alternating rows
        QPalette.ToolTipBase: QColor(33, 33, 33),      # Dark tooltip background
        QPalette.ToolTipText: QColor(255, 255, 255),   # White tooltip text
        QPalette.Text: QColor(255, 255, 255),          # White text
        QPalette.Button: QColor(45, 45, 45),           # Slightly lighter for buttons
        QPalette.ButtonText: QColor(255, 255, 255),    # White button text
        QPalette.BrightText: QColor(255, 128, 128),    # Light red for bright text
        QPalette.Link: QColor(66, 165, 245),           # Lighter blue for links
        QPalette.Highlight: QColor(33, 150, 243),      # Blue highlight
        QPalette.HighlightedText: QColor(255, 255, 255), # White text on highlight
        QPalette.Disabled: {                           # Disabled state colors
            QPalette.WindowText: QColor(128, 128, 128),
            QPalette.Text: QColor(128, 128, 128),
            QPalette.ButtonText: QColor(128, 128, 128),
            QPalette.Highlight: QColor(80, 80, 80),
            QPalette.HighlightedText: QColor(180, 180, 180)
        }
    }
    
    # Material Design color schemes
    MATERIAL_LIGHT = {
        "primary": QColor(33, 150, 243),  # Blue 500
        "primary_light": QColor(100, 181, 246),  # Blue 300
        "primary_dark": QColor(25, 118, 210),  # Blue 700
        "accent": QColor(255, 64, 129),  # Pink A400
        "text_primary": QColor(33, 33, 33),  # Grey 900
        "text_secondary": QColor(117, 117, 117),  # Grey 600
        "divider": QColor(189, 189, 189),  # Grey 400
        "background": QColor(250, 250, 250),  # Grey 50
        "card": QColor(255, 255, 255),  # White
        "error": QColor(244, 67, 54),  # Red 500
    }
    
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
    
    def __init__(self, theme=Theme.SYSTEM):
        """
        Initialize the theme manager.
        
        Args:
            theme (Theme): Initial theme to use
        """
        self.current_theme = theme
        self.material_colors = self.MATERIAL_LIGHT
        
        # Apply the initial theme
        self.apply_theme(theme)
    
    def apply_theme(self, theme):
        """
        Apply a theme to the application.
        
        Args:
            theme (Theme): Theme to apply
        """
        self.current_theme = theme
        app = QApplication.instance()
        
        if not app:
            logger.error("No QApplication instance found")
            return
        
        palette = QPalette()
        
        if theme == Theme.LIGHT:
            # Apply light theme
            for role, color in self.LIGHT_PALETTE.items():
                if role != QPalette.Disabled:
                    palette.setColor(role, color)
            self.material_colors = self.MATERIAL_LIGHT
            logger.info("Applied light theme")
        elif theme == Theme.DARK:
            # Apply dark theme
            for role, color in self.DARK_PALETTE.items():
                if role != QPalette.Disabled:
                    palette.setColor(role, color)
                    
            # Handle disabled state separately
            if QPalette.Disabled in self.DARK_PALETTE:
                disabled_colors = self.DARK_PALETTE[QPalette.Disabled]
                for role, color in disabled_colors.items():
                    palette.setColor(QPalette.Disabled, role, color)
                    
            self.material_colors = self.MATERIAL_DARK
            logger.info("Applied dark theme")
        elif theme == Theme.SYSTEM:
            # Use system theme (default Qt palette)
            # This is a simplified approach; in a real app, you might want to
            # detect the system theme and apply light or dark accordingly
            palette = app.style().standardPalette()
            
            # Determine if the system theme is dark or light
            bg_color = palette.color(QPalette.Window)
            is_dark = bg_color.lightness() < 128
            
            if is_dark:
                self.material_colors = self.MATERIAL_DARK
                logger.info("Applied system theme (detected as dark)")
            else:
                self.material_colors = self.MATERIAL_LIGHT
                logger.info("Applied system theme (detected as light)")
        
        app.setPalette(palette)
    
    def get_color(self, color_name):
        """
        Get a color from the current material design color scheme.
        
        Args:
            color_name (str): Name of the color to get
            
        Returns:
            QColor: The requested color or primary color if not found
        """
        return self.material_colors.get(color_name, self.material_colors["primary"])
    
    def get_stylesheet(self):
        """
        Get a stylesheet for the current theme.
        
        Returns:
            str: CSS stylesheet for the current theme
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
        
        QScrollBar {{
            background-color: {colors['background']};
            width: 12px;
            height: 12px;
        }}
        
        QScrollBar::handle {{
            background-color: {colors['divider']};
            border-radius: 6px;
        }}
        
        QScrollBar::handle:hover {{
            background-color: {colors.get('hover', 'rgb(55, 55, 55)')};
        }}
        
        QScrollBar::add-line, QScrollBar::sub-line {{
            background: none;
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
        """
        
        return stylesheet 