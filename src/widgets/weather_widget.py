"""
Weather Widget Module
------------------
This module provides the WeatherWidget class for displaying weather information in the Weather & Alarm application.
"""
import logging
import json
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QComboBox, QFrame, QGridLayout, QScrollArea,
    QSizePolicy
)
from PyQt6.QtCore import QTimer, pyqtSignal, Qt, QSize, QMargins
from PyQt6.QtGui import QPixmap, QFont, QColor

import requests
from datetime import datetime

from ..utils.svg_handler import get_weather_icon_pixmap
from ..services.weather_service import WeatherService
from ..config import (
    API_KEY, 
    WEATHER_API_URL, 
    ONECALL_API_URL, 
    AIR_QUALITY_API_URL,
    WEATHER_REFRESH_INTERVAL,
    WEATHER_ICONS_DIR
)

# Configure logging
logger = logging.getLogger(__name__)

class RoundedFrame(QFrame):
    """A custom frame with rounded corners and optional background color."""
    
    def __init__(self, parent=None, bg_color=None, border_radius=8):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)
        
        # Set background color and border radius
        style = f"""
            QFrame {{
                background-color: {bg_color if bg_color else 'rgba(35, 35, 40, 200)'};
                border-radius: {border_radius}px;
                padding: 12px;
            }}
        """
        self.setStyleSheet(style)

class WeatherDataLabel(QLabel):
    """A custom label for displaying weather data with a title and value."""
    
    def __init__(self, title, value="--", parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.update_text()
        
    def update_text(self):
        self.setText(f"<span style='color: rgba(180,180,255,0.7);'>{self.title}</span><br>"
                    f"<span style='font-size: 15px; font-weight: bold; color: rgba(255,255,255,0.9);'>{self.value}</span>")
        
    def set_value(self, value):
        self.value = value
        self.update_text()

class ForecastItem(QFrame):
    """A widget for displaying a single day's forecast."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(40, 40, 50, 180);
                border-radius: 8px;
                padding: 8px;
            }
            QFrame:hover {
                background-color: rgba(45, 45, 60, 200);
                border: 1px solid rgba(100, 181, 246, 100);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 12, 8, 12)
        layout.setSpacing(8)
        
        self.day_label = QLabel("--")
        self.day_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.day_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #90CAF9;")
        
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(60, 60)
        self.icon_label.setScaledContents(True)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.temp_max_label = QLabel("--°C")
        self.temp_max_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.temp_max_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        
        self.temp_min_label = QLabel("--°C")
        self.temp_min_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.temp_min_label.setStyleSheet("font-size: 14px; color: rgba(180, 180, 255, 0.8);")
        
        self.condition_label = QLabel("--")
        self.condition_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.condition_label.setStyleSheet("font-size: 12px; color: #BBDEFB;")
        self.condition_label.setWordWrap(True)
        
        layout.addWidget(self.day_label)
        layout.addWidget(self.icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.temp_max_label)
        layout.addWidget(self.temp_min_label)
        layout.addWidget(self.condition_label)

class WeatherWidget(QWidget):
    """Widget for displaying weather information."""
    
    # Signal emitted when weather data is updated
    weather_updated = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        """
        Initialize the weather widget.
        
        Args:
            parent (QWidget, optional): Parent widget
        """
        super().__init__(parent)
        
        # Initialize the weather service
        self.weather_service = WeatherService()
        
        # Initialize weather data
        self.weather_data = None
        self.forecast_data = None
        
        # Initialize UI
        self.init_ui()
        
        # Set up refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_weather)
        self.refresh_timer.start(1800000)  # 30 minutes
    
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create a scroll area for the content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Create a widget to hold the scrollable content
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(16, 16, 16, 16)
        scroll_layout.setSpacing(20)
        
        # Add title
        title_label = QLabel("Weather")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #64B5F6; margin-bottom: 10px;")
        scroll_layout.addWidget(title_label)
        
        # Add search bar
        search_frame = RoundedFrame(bg_color="rgba(25, 25, 35, 200)")
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(12, 12, 12, 12)
        
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Enter city name")
        self.city_input.returnPressed.connect(self.search_weather)
        self.city_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(45, 45, 55, 180);
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                background-color: rgba(55, 55, 65, 180);
                border: 1px solid #64B5F6;
            }
        """)
        
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_weather)
        search_button.setStyleSheet("""
            QPushButton {
                background-color: #64B5F6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #42A5F5;
            }
            QPushButton:pressed {
                background-color: #2196F3;
            }
        """)
        
        search_layout.addWidget(self.city_input)
        search_layout.addWidget(search_button)
        scroll_layout.addWidget(search_frame)
        
        # Add current weather display
        self.weather_frame = RoundedFrame(bg_color="rgba(30, 30, 40, 200)")
        weather_layout = QVBoxLayout(self.weather_frame)
        weather_layout.setContentsMargins(16, 16, 16, 16)
        weather_layout.setSpacing(16)
        
        # Location and last updated
        header_layout = QHBoxLayout()
        
        self.location_label = QLabel("No location selected")
        self.location_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #90CAF9;")
        header_layout.addWidget(self.location_label)
        
        header_layout.addStretch()
        
        self.updated_label = QLabel("Last updated: Never")
        self.updated_label.setStyleSheet("font-size: 12px; color: rgba(180, 180, 255, 0.7);")
        header_layout.addWidget(self.updated_label)
        
        weather_layout.addLayout(header_layout)
        
        # Current weather details - improved layout
        current_weather_frame = RoundedFrame(bg_color="rgba(40, 40, 50, 150)")
        current_layout = QHBoxLayout(current_weather_frame)
        current_layout.setContentsMargins(16, 16, 16, 16)
        current_layout.setSpacing(20)
        
        # Weather icon - moved to left side
        self.weather_icon_label = QLabel()
        self.weather_icon_label.setFixedSize(140, 140)
        self.weather_icon_label.setScaledContents(True)
        self.weather_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Temperature and description - centered
        temp_layout = QVBoxLayout()
        temp_layout.setSpacing(8)
        temp_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.temperature_label = QLabel("--°C")
        self.temperature_label.setStyleSheet("font-size: 56px; font-weight: bold; color: white;")
        self.temperature_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.description_label = QLabel("--")
        self.description_label.setStyleSheet("font-size: 18px; color: #BBDEFB;")
        self.description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        temp_layout.addWidget(self.temperature_label)
        temp_layout.addWidget(self.description_label)
        
        # Add icon and temperature to layout
        current_layout.addWidget(self.weather_icon_label)
        current_layout.addLayout(temp_layout)
        
        weather_layout.addWidget(current_weather_frame)
        
        # Weather details in a separate frame
        details_frame = RoundedFrame(bg_color="rgba(40, 40, 50, 150)")
        details_layout = QGridLayout(details_frame)
        details_layout.setHorizontalSpacing(32)
        details_layout.setVerticalSpacing(16)
        
        # Create weather data labels
        self.feels_like_label = WeatherDataLabel("Feels like")
        self.humidity_label = WeatherDataLabel("Humidity")
        self.wind_label = WeatherDataLabel("Wind")
        self.pressure_label = WeatherDataLabel("Pressure")
        self.sunrise_label = WeatherDataLabel("Sunrise")
        self.sunset_label = WeatherDataLabel("Sunset")
        
        # Add to grid
        details_layout.addWidget(self.feels_like_label, 0, 0)
        details_layout.addWidget(self.humidity_label, 0, 1)
        details_layout.addWidget(self.wind_label, 1, 0)
        details_layout.addWidget(self.pressure_label, 1, 1)
        details_layout.addWidget(self.sunrise_label, 2, 0)
        details_layout.addWidget(self.sunset_label, 2, 1)
        
        weather_layout.addWidget(details_frame)
        
        scroll_layout.addWidget(self.weather_frame)
        
        # Add forecast section
        forecast_label = QLabel("5-Day Forecast")
        forecast_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #90CAF9; margin-top: 10px;")
        scroll_layout.addWidget(forecast_label)
        
        self.forecast_frame = RoundedFrame(bg_color="rgba(30, 30, 40, 200)")
        forecast_layout = QHBoxLayout(self.forecast_frame)
        forecast_layout.setContentsMargins(12, 16, 12, 16)
        forecast_layout.setSpacing(12)
        
        # Create forecast items
        self.forecast_items = []
        for i in range(5):
            forecast_item = ForecastItem()
            forecast_layout.addWidget(forecast_item)
            self.forecast_items.append(forecast_item)
        
        scroll_layout.addWidget(self.forecast_frame)
        
        # Add refresh button
        refresh_button = QPushButton("Refresh Weather")
        refresh_button.clicked.connect(self.refresh_weather)
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #64B5F6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #42A5F5;
            }
            QPushButton:pressed {
                background-color: #2196F3;
            }
        """)
        scroll_layout.addWidget(refresh_button)
        
        # Add stretch to push everything to the top
        scroll_layout.addStretch()
        
        # Set the scroll content
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
    
    def search_weather(self):
        """Search for weather data for the entered city."""
        city = self.city_input.text().strip()
        if not city:
            return
        
        logger.info(f"Searching weather for city: {city}")
        
        try:
            # Get current weather
            weather_data = self.weather_service.get_current_weather(city=city)
            if not weather_data:
                logger.error(f"Failed to get weather data for {city}")
                return
            
            # Parse the weather data
            self.weather_data = self.weather_service.parse_weather_data(weather_data)
            
            # Get coordinates for forecast
            if 'coord' in weather_data:
                lat = weather_data['coord']['lat']
                lon = weather_data['coord']['lon']
                
                # Get forecast data
                self.forecast_data = self.weather_service.get_forecast(lat, lon)
            
            # Update the UI
            self.update_weather_display()
            
            # Emit signal
            if self.weather_data:
                self.weather_updated.emit(self.weather_data)
        
        except Exception as e:
            logger.error(f"Error searching weather: {str(e)}")
    
    def refresh_weather(self):
        """Refresh the current weather data."""
        if not self.weather_data:
            return
        
        city = self.weather_data.get('city')
        if city:
            self.city_input.setText(city)
            self.search_weather()
    
    def update_weather_display(self):
        """Update the weather display with current data."""
        if not self.weather_data:
            return
        
        # Update location
        city = self.weather_data.get('city', 'Unknown')
        country = self.weather_data.get('country', '')
        location_text = f"{city}, {country}" if country else city
        self.location_label.setText(location_text)
        
        # Update temperature
        temp = self.weather_data.get('temperature', 0)
        self.temperature_label.setText(f"{temp:.1f}°C")
        
        # Update description
        description = self.weather_data.get('description', '--')
        self.description_label.setText(description.capitalize())
        
        # Update icon
        icon_code = self.weather_data.get('icon', '')
        if icon_code:
            pixmap = get_weather_icon_pixmap(icon_code, QSize(140, 140))
            if pixmap:
                self.weather_icon_label.setPixmap(pixmap)
        
        # Update details
        self.feels_like_label.set_value(f"{self.weather_data.get('feels_like', 0):.1f}°C")
        self.humidity_label.set_value(f"{self.weather_data.get('humidity', 0)}%")
        self.wind_label.set_value(f"{self.weather_data.get('wind_speed', 0):.1f} m/s")
        self.pressure_label.set_value(f"{self.weather_data.get('pressure', 0)} hPa")
        
        # Update sunrise/sunset
        sunrise = self.weather_data.get('sunrise')
        if sunrise:
            self.sunrise_label.set_value(sunrise.strftime("%H:%M"))
        
        sunset = self.weather_data.get('sunset')
        if sunset:
            self.sunset_label.set_value(sunset.strftime("%H:%M"))
        
        # Update last updated time
        now = datetime.now()
        self.updated_label.setText(f"Last updated: {now.strftime('%Y-%m-%d %H:%M')}")
        
        # Update forecast if available
        self.update_forecast_display()
    
    def update_forecast_display(self):
        """Update the forecast display with current data."""
        if not self.forecast_data or 'daily' not in self.forecast_data:
            return
        
        daily_data = self.forecast_data['daily']
        
        # Update each forecast day
        for i, forecast_item in enumerate(self.forecast_items):
            if i < len(daily_data):
                day_data = daily_data[i]
                
                # Get day name
                timestamp = day_data.get('dt', 0)
                date = datetime.fromtimestamp(timestamp)
                day_name = date.strftime("%a")
                forecast_item.day_label.setText(day_name)
                
                # Get icon
                icon_code = day_data.get('weather', [{}])[0].get('icon', '')
                if icon_code:
                    pixmap = get_weather_icon_pixmap(icon_code, QSize(60, 60))
                    if pixmap:
                        forecast_item.icon_label.setPixmap(pixmap)
                
                # Get temperature
                temp_max = day_data.get('temp', {}).get('max', 0)
                temp_min = day_data.get('temp', {}).get('min', 0)
                forecast_item.temp_max_label.setText(f"{temp_max:.1f}°C")
                forecast_item.temp_min_label.setText(f"{temp_min:.1f}°C")
                
                # Get weather condition
                condition = day_data.get('weather', [{}])[0].get('description', '--')
                forecast_item.condition_label.setText(condition.capitalize())
    
    def set_city(self, city):
        """
        Set the city and search for weather.
        
        Args:
            city (str): City name
        """
        self.city_input.setText(city)
        self.search_weather() 