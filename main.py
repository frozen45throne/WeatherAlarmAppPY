#!/usr/bin/env python3
"""
Weather & Alarm Application Launcher
-----------------------------------
This script launches the Weather & Alarm application.
"""
import sys
import os
import traceback

def main():
    """Main entry point for the application"""
    try:
        # Add the current directory to Python's module search path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Import required PyQt modules first to avoid import errors
        from PyQt5.QtWidgets import QApplication, QStyleFactory, QMessageBox
        from PyQt5.QtCore import Qt
        
        # Import application modules
        from src.utils.theme_utils import ThemeManager
        from src.utils.svg_utils import ensure_icon_exists, ensure_weather_icons_dir, ensure_all_weather_svg_files
        from src.app.weather_alarm_app import WeatherAlarmApp
        
        # Create QApplication instance
        app = QApplication(sys.argv)
        
        # Ensure resources exist
        ensure_icon_exists()
        ensure_weather_icons_dir()
        ensure_all_weather_svg_files()
        
        # Set application style
        app.setStyle(QStyleFactory.create("Fusion"))
        
        # Create and show the main window
        window = WeatherAlarmApp()
        window.show()
        
        # Start the application event loop
        sys.exit(app.exec_())
        
    except ImportError as e:
        # Handle import errors specifically
        error_msg = f"Import Error: {str(e)}\n\n"
        error_msg += "This is likely due to a missing dependency or incorrect import path.\n"
        error_msg += "Please ensure you have installed all required packages:\n"
        error_msg += "  - PyQt5\n  - qt-material\n  - requests\n\n"
        error_msg += "Detailed error information:\n"
        error_msg += traceback.format_exc()
        
        print(error_msg)
        
        # Try to show a GUI error message if possible
        try:
            from PyQt5.QtWidgets import QApplication, QMessageBox
            app = QApplication(sys.argv)
            QMessageBox.critical(None, "Application Error", error_msg)
        except:
            # If GUI error display fails, just print to console
            pass
            
        return 1
        
    except Exception as e:
        # Handle other exceptions
        error_msg = f"Error: {str(e)}\n\n"
        error_msg += "An unexpected error occurred while starting the application.\n\n"
        error_msg += "Detailed error information:\n"
        error_msg += traceback.format_exc()
        
        print(error_msg)
        
        # Try to show a GUI error message if possible
        try:
            from PyQt5.QtWidgets import QApplication, QMessageBox
            app = QApplication(sys.argv)
            QMessageBox.critical(None, "Application Error", error_msg)
        except:
            # If GUI error display fails, just print to console
            pass
            
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 