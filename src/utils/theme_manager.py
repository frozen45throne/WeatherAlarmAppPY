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
        QPalette.Window: QColor(53, 53, 53),
        QPalette.WindowText: QColor(255, 255, 255),
        QPalette.Base: QColor(25, 25, 25),
        QPalette.AlternateBase: QColor(53, 53, 53),
        QPalette.ToolTipBase: QColor(53, 53, 53),
        QPalette.ToolTipText: QColor(255, 255, 255),
        QPalette.Text: QColor(255, 255, 255),
        QPalette.Button: QColor(53, 53, 53),
        QPalette.ButtonText: QColor(255, 255, 255),
        QPalette.BrightText: QColor(255, 0, 0),
        QPalette.Link: QColor(42, 130, 218),
        QPalette.Highlight: QColor(42, 130, 218),
        QPalette.HighlightedText: QColor(255, 255, 255),
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
        "primary": QColor(33, 150, 243),  # Blue 500
        "primary_light": QColor(100, 181, 246),  # Blue 300
        "primary_dark": QColor(25, 118, 210),  # Blue 700
        "accent": QColor(255, 64, 129),  # Pink A400
        "text_primary": QColor(255, 255, 255),  # White
        "text_secondary": QColor(189, 189, 189),  # Grey 400
        "divider": QColor(97, 97, 97),  # Grey 700
        "background": QColor(48, 48, 48),  # Grey 900
        "card": QColor(66, 66, 66),  # Grey 800
        "error": QColor(244, 67, 54),  # Red 500
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
                palette.setColor(role, color)
            self.material_colors = self.MATERIAL_LIGHT
            logger.info("Applied light theme")
        elif theme == Theme.DARK:
            # Apply dark theme
            for role, color in self.DARK_PALETTE.items():
                palette.setColor(role, color)
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
        colors = {name: f"rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha()/255})" 
                 for name, color in self.material_colors.items()}
        
        # Create a stylesheet with CSS variables
        stylesheet = f"""
        /* Material Design Theme Variables */
        QWidget {{
            --primary: {colors['primary']};
            --primary-light: {colors['primary_light']};
            --primary-dark: {colors['primary_dark']};
            --accent: {colors['accent']};
            --text-primary: {colors['text_primary']};
            --text-secondary: {colors['text_secondary']};
            --divider: {colors['divider']};
            --background: {colors['background']};
            --card: {colors['card']};
            --error: {colors['error']};
        }}
        
        /* Base Styles */
        QWidget {{
            background-color: var(--background);
            color: var(--text-primary);
        }}
        
        QFrame {{
            background-color: var(--card);
            border-radius: 4px;
        }}
        
        QPushButton {{
            background-color: var(--primary);
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: var(--primary-dark);
        }}
        
        QPushButton:pressed {{
            background-color: var(--primary-light);
        }}
        
        QLineEdit, QComboBox, QSpinBox, QTimeEdit {{
            border: 1px solid var(--divider);
            border-radius: 4px;
            padding: 8px;
            background-color: var(--card);
            color: var(--text-primary);
        }}
        
        QLabel {{
            color: var(--text-primary);
        }}
        
        QTabWidget::pane {{
            border: 1px solid var(--divider);
            border-radius: 4px;
        }}
        
        QTabBar::tab {{
            background-color: var(--background);
            color: var(--text-secondary);
            padding: 8px 16px;
            border-bottom: 2px solid transparent;
        }}
        
        QTabBar::tab:selected {{
            color: var(--primary);
            border-bottom: 2px solid var(--primary);
        }}
        
        QScrollBar {{
            background-color: var(--background);
            width: 12px;
            height: 12px;
        }}
        
        QScrollBar::handle {{
            background-color: var(--divider);
            border-radius: 6px;
        }}
        
        QScrollBar::add-line, QScrollBar::sub-line {{
            background: none;
        }}
        """
        
        return stylesheet 