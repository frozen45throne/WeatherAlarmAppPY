"""
SVG Handler Utility
------------------
This module provides utilities for handling SVG files in the Weather & Alarm application.
"""
import os
import logging
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtCore import QSize, Qt

from ..config import (
    WEATHER_ICONS_DIR, 
    EXTERNAL_WEATHER_ICONS_PATH, 
    WEATHER_ICONS, 
    DEFAULT_WEATHER_ICON,
    SVG_ALTERNATIVES,
    ANIMATED_SVG_PATTERNS
)

# Configure logging
logger = logging.getLogger(__name__)

def find_svg_file(icon_code):
    """
    Find the appropriate SVG or PNG file for the given weather icon code.
    
    Args:
        icon_code (str): The weather icon code from OpenWeatherMap API
        
    Returns:
        str: Path to the SVG/PNG file or None if not found
    """
    # Get the SVG filename from the mapping
    svg_filename = WEATHER_ICONS.get(icon_code, DEFAULT_WEATHER_ICON)
    
    # First try the internal weather icons directory with PNG
    png_filename = f"{icon_code}.png"
    png_path = os.path.join(WEATHER_ICONS_DIR, png_filename)
    if os.path.exists(png_path):
        logger.debug(f"Found PNG at path: {png_path}")
        return png_path
    
    # Then try SVG in the internal weather icons directory
    svg_path = os.path.join(WEATHER_ICONS_DIR, svg_filename)
    if os.path.exists(svg_path):
        logger.debug(f"Found SVG at internal path: {svg_path}")
        return svg_path
    
    # If not found, try the external icons directory
    if EXTERNAL_WEATHER_ICONS_PATH and os.path.exists(EXTERNAL_WEATHER_ICONS_PATH):
        svg_path = os.path.join(EXTERNAL_WEATHER_ICONS_PATH, svg_filename)
        if os.path.exists(svg_path):
            logger.debug(f"Found SVG at external path: {svg_path}")
            return svg_path
        
        # Try alternative filenames
        base_name = os.path.splitext(svg_filename)[0]
        for pattern in ANIMATED_SVG_PATTERNS:
            alt_filename = pattern.format(name=base_name)
            alt_path = os.path.join(EXTERNAL_WEATHER_ICONS_PATH, alt_filename)
            if os.path.exists(alt_path):
                logger.debug(f"Found alternative SVG: {alt_path}")
                return alt_path
        
        # Try the alternatives list
        if svg_filename in SVG_ALTERNATIVES:
            for alt_filename in SVG_ALTERNATIVES[svg_filename]:
                alt_path = os.path.join(EXTERNAL_WEATHER_ICONS_PATH, alt_filename)
                if os.path.exists(alt_path):
                    logger.debug(f"Found alternative SVG from list: {alt_path}")
                    return alt_path
    
    # If still not found, log an error and return None
    logger.error(f"Could not find SVG/PNG file for icon code: {icon_code}")
    return None

def render_svg_to_pixmap(svg_path, size=QSize(64, 64)):
    """
    Render an SVG or PNG file to a QPixmap.
    
    Args:
        svg_path (str): Path to the SVG/PNG file
        size (QSize): Size of the resulting pixmap
        
    Returns:
        QPixmap: The rendered pixmap or None if rendering failed
    """
    if not svg_path or not os.path.exists(svg_path):
        logger.error(f"File does not exist: {svg_path}")
        return None
    
    try:
        # Check if it's a PNG file
        if svg_path.lower().endswith('.png'):
            pixmap = QPixmap(svg_path)
            if pixmap.isNull():
                logger.error(f"Invalid PNG file: {svg_path}")
                return None
            return pixmap.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        # Handle SVG file
        renderer = QSvgRenderer(svg_path)
        if not renderer.isValid():
            logger.error(f"Invalid SVG file: {svg_path}")
            return None
        
        pixmap = QPixmap(size)
        pixmap.fill(Qt.transparent)  # Transparent background
        
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        return pixmap
    except Exception as e:
        logger.error(f"Error rendering file {svg_path}: {str(e)}")
        return None

def get_weather_icon_pixmap(icon_code, size=QSize(64, 64)):
    """
    Get a QPixmap for the given weather icon code.
    
    Args:
        icon_code (str): The weather icon code from OpenWeatherMap API
        size (QSize): Size of the resulting pixmap
        
    Returns:
        QPixmap: The rendered weather icon pixmap or None if not available
    """
    svg_path = find_svg_file(icon_code)
    if svg_path:
        return render_svg_to_pixmap(svg_path, size)
    return None 