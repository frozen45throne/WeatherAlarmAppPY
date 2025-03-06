#!/usr/bin/env python
"""
Weather & Alarm Application Runner
--------------------------------
This script runs the Weather & Alarm application.
"""
import sys
import os
import logging
import traceback

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

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import PyQt5
        # Import QtCore separately
        from PyQt5 import QtCore
        logger.info(f"PyQt5 version: {QtCore.QT_VERSION_STR}")
        
        # Check for PyQtWebEngine
        try:
            from PyQt5 import QtWebEngineWidgets
            logger.info("PyQtWebEngine is installed")
        except ImportError:
            logger.warning("PyQtWebEngine is not installed. Weather Map feature will not be available.")
            logger.warning("Install it using: pip install PyQtWebEngine>=5.15.0")
        
        # Check for requests
        try:
            import requests
            logger.info(f"Requests version: {requests.__version__}")
        except ImportError:
            logger.warning("Requests is not installed. Weather data fetching will not work.")
            logger.warning("Install it using: pip install requests>=2.25.0")
        
        # Check for dateutil
        try:
            import dateutil
            logger.info(f"Python-dateutil is installed")
        except ImportError:
            logger.warning("Python-dateutil is not installed. Some date handling features may not work correctly.")
            logger.warning("Install it using: pip install python-dateutil>=2.8.1")
        
        return True
    except ImportError as e:
        logger.error(f"Missing dependency: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        # Check dependencies
        if not check_dependencies():
            logger.error("Missing required dependencies. Please install them and try again.")
            sys.exit(1)
        
        # Import the main module
        from src.main import main
        
        # Run the application
        logger.info("Starting Weather & Alarm Application")
        main()
    except ImportError as e:
        # Handle import errors
        logger.error(f"Import error: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        # Log any uncaught exceptions
        logger.error(f"Uncaught exception: {str(e)}")
        traceback.print_exc()
        sys.exit(1) 