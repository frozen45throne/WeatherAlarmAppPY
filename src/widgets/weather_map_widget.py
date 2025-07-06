"""
Weather Map Widget Module
------------------
This module provides a placeholder for the WeatherMapWidget while it's being redesigned.
"""
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont

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

class WeatherMapWidget(QWidget):
    """Placeholder widget for the weather map feature."""
    
    def __init__(self, parent=None):
        """Initialize the weather map widget placeholder."""
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface with a placeholder message."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(24)
        
        # Add title with modern styling
        title_label = QLabel("Weather Map")
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #90CAF9;
            margin-bottom: 16px;
            padding-left: 4px;
        """)
        main_layout.addWidget(title_label)
        
        # Create placeholder frame
        placeholder_frame = RoundedFrame(bg_color="rgba(40, 40, 50, 0.7)")
        placeholder_layout = QVBoxLayout(placeholder_frame)
        
        # Add placeholder message
        message_label = QLabel(
            "🔄 Weather Map Redesign in Progress\n\n"
            "We're working on making the weather map even better!\n"
            "The new version will feature improved performance,\n"
            "better visualization, and a more intuitive interface.\n\n"
            "Thank you for your patience."
        )
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9);
            font-size: 16px;
            line-height: 1.6;
        """)
        message_label.setWordWrap(True)
        
        # Set minimum size for the placeholder
        placeholder_frame.setMinimumHeight(300)
        
        placeholder_layout.addWidget(message_label)
        main_layout.addWidget(placeholder_frame)
        
        # Add coming soon label
        coming_soon_label = QLabel("Coming Soon!")
        coming_soon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        coming_soon_label.setStyleSheet("""
            color: #64B5F6;
            font-size: 18px;
            font-weight: bold;
            margin-top: 16px;
        """)
        main_layout.addWidget(coming_soon_label)
        
        # Add stretch to keep everything at the top
        main_layout.addStretch()
        
        logger.info("Weather map placeholder initialized")
    
    def set_location(self, lat, lon, city=None):
        """Placeholder for setting location."""
        pass
    
    def update_map(self):
        """Placeholder for map updates."""
        pass 