#!/usr/bin/env python
"""
Weather & Alarm Application Runner
--------------------------------
This script runs the Weather & Alarm application.
"""
import sys
import os
import logging

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main module
from src.main import main

if __name__ == "__main__":
    try:
        # Run the application
        main()
    except Exception as e:
        # Log any uncaught exceptions
        logging.exception(f"Uncaught exception: {str(e)}")
        sys.exit(1) 