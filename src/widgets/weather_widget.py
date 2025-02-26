"""
Weather Widget Module
------------------
This module provides the WeatherWidget class for displaying weather information in the Weather & Alarm application.
"""
import logging
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QFrame, QGridLayout, QScrollArea, QSizePolicy, QComboBox
)
from PyQt5.QtCore import QTimer, pyqtSignal, Qt, QSize
from PyQt5.QtGui import QPixmap, QFont

from ..services.weather_service import WeatherService
from ..utils.svg_handler import get_weather_icon_pixmap

# Configure logging
logger = logging.getLogger(__name__)

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
        
        # Create a scroll area for the content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Create a widget to hold the scrollable content
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(16, 16, 16, 16)
        scroll_layout.setSpacing(16)
        
        # Add title
        title_label = QLabel("Weather")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        scroll_layout.addWidget(title_label)
        
        # Add search bar
        search_layout = QHBoxLayout()
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Enter city name")
        self.city_input.returnPressed.connect(self.search_weather)  # Add Enter key handling
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_weather)
        search_layout.addWidget(self.city_input)
        search_layout.addWidget(search_button)
        scroll_layout.addLayout(search_layout)
        
        # Add weather display frame
        self.weather_frame = QFrame()
        self.weather_frame.setFrameShape(QFrame.StyledPanel)
        self.weather_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #ccc;
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.8);
            }
        """)
        
        weather_layout = QVBoxLayout(self.weather_frame)
        
        # Current weather header
        self.location_label = QLabel("No location selected")
        self.location_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        weather_layout.addWidget(self.location_label)
        
        # Current weather details
        current_layout = QHBoxLayout()
        
        # Weather icon
        self.weather_icon_label = QLabel()
        self.weather_icon_label.setFixedSize(100, 100)
        self.weather_icon_label.setScaledContents(True)
        current_layout.addWidget(self.weather_icon_label)
        
        # Temperature and description
        temp_layout = QVBoxLayout()
        self.temperature_label = QLabel("--°C")
        self.temperature_label.setStyleSheet("font-size: 32px; font-weight: bold;")
        self.description_label = QLabel("--")
        self.description_label.setStyleSheet("font-size: 14px;")
        temp_layout.addWidget(self.temperature_label)
        temp_layout.addWidget(self.description_label)
        temp_layout.addStretch()
        current_layout.addLayout(temp_layout)
        
        current_layout.addStretch()
        weather_layout.addLayout(current_layout)
        
        # Weather details grid
        details_grid = QGridLayout()
        details_grid.setColumnStretch(1, 1)
        details_grid.setColumnStretch(3, 1)
        
        # Feels like
        details_grid.addWidget(QLabel("Feels like:"), 0, 0)
        self.feels_like_label = QLabel("--°C")
        details_grid.addWidget(self.feels_like_label, 0, 1)
        
        # Humidity
        details_grid.addWidget(QLabel("Humidity:"), 0, 2)
        self.humidity_label = QLabel("--%")
        details_grid.addWidget(self.humidity_label, 0, 3)
        
        # Wind
        details_grid.addWidget(QLabel("Wind:"), 1, 0)
        self.wind_label = QLabel("-- m/s")
        details_grid.addWidget(self.wind_label, 1, 1)
        
        # Pressure
        details_grid.addWidget(QLabel("Pressure:"), 1, 2)
        self.pressure_label = QLabel("-- hPa")
        details_grid.addWidget(self.pressure_label, 1, 3)
        
        # Sunrise
        details_grid.addWidget(QLabel("Sunrise:"), 2, 0)
        self.sunrise_label = QLabel("--:--")
        details_grid.addWidget(self.sunrise_label, 2, 1)
        
        # Sunset
        details_grid.addWidget(QLabel("Sunset:"), 2, 2)
        self.sunset_label = QLabel("--:--")
        details_grid.addWidget(self.sunset_label, 2, 3)
        
        weather_layout.addLayout(details_grid)
        
        # Last updated
        self.updated_label = QLabel("Last updated: Never")
        self.updated_label.setStyleSheet("font-size: 10px; color: #666;")
        weather_layout.addWidget(self.updated_label, alignment=Qt.AlignRight)
        
        scroll_layout.addWidget(self.weather_frame)
        
        # Add forecast section (placeholder for now)
        forecast_label = QLabel("Forecast")
        forecast_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        scroll_layout.addWidget(forecast_label)
        
        self.forecast_frame = QFrame()
        self.forecast_frame.setFrameShape(QFrame.StyledPanel)
        self.forecast_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #ccc;
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.8);
            }
        """)
        
        forecast_layout = QHBoxLayout(self.forecast_frame)
        forecast_layout.setSpacing(16)
        
        # Placeholder for forecast items
        self.forecast_labels = []
        for i in range(5):
            forecast_item = QWidget()
            item_layout = QVBoxLayout(forecast_item)
            
            day_label = QLabel(f"Day {i+1}")
            day_label.setAlignment(Qt.AlignCenter)
            
            icon_label = QLabel()
            icon_label.setFixedSize(50, 50)
            icon_label.setScaledContents(True)
            
            temp_label = QLabel("--°C")
            temp_label.setAlignment(Qt.AlignCenter)
            
            item_layout.addWidget(day_label)
            item_layout.addWidget(icon_label, alignment=Qt.AlignCenter)
            item_layout.addWidget(temp_label)
            
            forecast_layout.addWidget(forecast_item)
            
            self.forecast_labels.append((day_label, icon_label, temp_label))
        
        scroll_layout.addWidget(self.forecast_frame)
        
        # Add refresh button
        refresh_button = QPushButton("Refresh Weather")
        refresh_button.clicked.connect(self.refresh_weather)
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
            pixmap = get_weather_icon_pixmap(icon_code, QSize(100, 100))
            if pixmap:
                self.weather_icon_label.setPixmap(pixmap)
        
        # Update details
        self.feels_like_label.setText(f"{self.weather_data.get('feels_like', 0):.1f}°C")
        self.humidity_label.setText(f"{self.weather_data.get('humidity', 0)}%")
        self.wind_label.setText(f"{self.weather_data.get('wind_speed', 0):.1f} m/s")
        self.pressure_label.setText(f"{self.weather_data.get('pressure', 0)} hPa")
        
        # Update sunrise/sunset
        sunrise = self.weather_data.get('sunrise')
        if sunrise:
            self.sunrise_label.setText(sunrise.strftime("%H:%M"))
        
        sunset = self.weather_data.get('sunset')
        if sunset:
            self.sunset_label.setText(sunset.strftime("%H:%M"))
        
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
        for i, (day_label, icon_label, temp_label) in enumerate(self.forecast_labels):
            if i < len(daily_data):
                day_data = daily_data[i]
                
                # Get day name
                timestamp = day_data.get('dt', 0)
                date = datetime.fromtimestamp(timestamp)
                day_name = date.strftime("%a")
                day_label.setText(day_name)
                
                # Get icon
                icon_code = day_data.get('weather', [{}])[0].get('icon', '')
                if icon_code:
                    pixmap = get_weather_icon_pixmap(icon_code, QSize(50, 50))
                    if pixmap:
                        icon_label.setPixmap(pixmap)
                
                # Get temperature
                temp_max = day_data.get('temp', {}).get('max', 0)
                temp_min = day_data.get('temp', {}).get('min', 0)
                temp_label.setText(f"{temp_min:.1f}°C / {temp_max:.1f}°C")
    
    def set_city(self, city):
        """
        Set the city and search for weather.
        
        Args:
            city (str): City name
        """
        self.city_input.setText(city)
        self.search_weather() 