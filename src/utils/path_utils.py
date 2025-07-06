"""
Path Utilities Module
------------------
This module provides utility functions for handling file paths in the Weather & Alarm application.
"""
import os
import logging
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

def get_app_root_dir():
    """
    Get the absolute path to the application root directory.
    
    Returns:
        str: Absolute path to the application root directory
    """
    # Get the directory containing this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up two levels to get to the app root (from src/utils to app root)
    app_root = os.path.dirname(os.path.dirname(current_dir))
    return app_root

def get_icon_path(icon_name, subdirectory=None):
    """
    Get the absolute path to an icon file.
    
    Args:
        icon_name (str): Name of the icon file
        subdirectory (str, optional): Subdirectory within the icons directory
    
    Returns:
        str: Absolute path to the icon file, properly formatted for CSS URLs
    """
    app_root = get_app_root_dir()
    icons_dir = os.path.join(app_root, "icons")
    
    if subdirectory:
        icons_dir = os.path.join(icons_dir, subdirectory)
    
    icon_path = os.path.join(icons_dir, icon_name)
    
    if not os.path.exists(icon_path):
        logger.warning(f"Icon not found: {icon_path}")
    
    # Convert Windows path to forward slashes and escape spaces
    icon_path = str(Path(icon_path)).replace("\\", "/").replace(" ", "%20")
    return icon_path 