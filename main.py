import sys
import json
import requests
from datetime import datetime
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                            QTimeEdit, QListWidget, QMessageBox, QTabWidget,
                            QGridLayout, QFrame)
from PyQt5.QtCore import Qt, QTimer, QTime, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QIcon

# Configuration
API_KEY = "API_KEY"  # Replace with your actual API key
WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"
WEATHER_REFRESH_INTERVAL = 1800000  # 30 minutes in milliseconds
TIME_REFRESH_INTERVAL = 1000  # 1 second in milliseconds
APP_ICON_PATH = "unnamed.ico"  # Icon file path

class AlarmThread(QThread):
    """Thread to handle alarm timing without blocking the main UI"""
    alarm_signal = pyqtSignal(str)
    
    def __init__(self, alarm_time):
        super().__init__()
        self.alarm_time = alarm_time
        self.is_running = True
        
    def run(self):
        while self.is_running:
            current_time = QTime.currentTime()
            if current_time.toString("HH:mm") == self.alarm_time.toString("HH:mm"):
                self.alarm_signal.emit(self.alarm_time.toString("HH:mm"))
                self.is_running = False
            time.sleep(1)
            
    def stop(self):
        self.is_running = False


class WeatherWidget(QWidget):
    """Widget for displaying weather information"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Current time display
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setFont(QFont("Arial", 24, QFont.Bold))
        layout.addWidget(self.time_label)
        
        # Location input
        location_layout = QHBoxLayout()
        location_label = QLabel("Location:")
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Enter city name")
        
        get_weather_btn = QPushButton("Get Weather")
        get_weather_btn.clicked.connect(self.on_get_weather)
        self.location_input.returnPressed.connect(self.on_get_weather)
        
        location_layout.addWidget(location_label)
        location_layout.addWidget(self.location_input)
        location_layout.addWidget(get_weather_btn)
        
        layout.addLayout(location_layout)
        
        # Weather display
        weather_frame = QFrame()
        weather_frame.setFrameShape(QFrame.StyledPanel)
        weather_frame.setStyleSheet("background-color: #f0f0f0; border-radius: 10px; padding: 10px;")
        
        weather_info_layout = QGridLayout(weather_frame)
        
        self.city_label = QLabel("City: ")
        self.temp_label = QLabel("Temperature: ")
        self.desc_label = QLabel("Description: ")
        self.humidity_label = QLabel("Humidity: ")
        self.wind_label = QLabel("Wind: ")
        
        weather_info_layout.addWidget(self.city_label, 0, 0)
        weather_info_layout.addWidget(self.temp_label, 1, 0)
        weather_info_layout.addWidget(self.desc_label, 2, 0)
        weather_info_layout.addWidget(self.humidity_label, 3, 0)
        weather_info_layout.addWidget(self.wind_label, 4, 0)
        
        layout.addWidget(weather_frame)
        
    def on_get_weather(self):
        """Handler for the get weather button click or enter key press"""
        city = self.location_input.text()
        if city:
            self.parent().get_weather(city)
        else:
            QMessageBox.warning(self, "Input Error", "Please enter a city name.")
            
    def update_time(self, current_time):
        """Update the time display"""
        time_text = current_time.toString("hh:mm:ss AP")
        self.time_label.setText(time_text)
        
    def update_weather_display(self, weather_data):
        """Update the weather information display"""
        self.city_label.setText(f"City: {weather_data['city']}")
        self.temp_label.setText(f"Temperature: {weather_data['temp']}°C")
        self.desc_label.setText(f"Description: {weather_data['description']}")
        self.humidity_label.setText(f"Humidity: {weather_data['humidity']}%")
        self.wind_label.setText(f"Wind: {weather_data['wind']} m/s")


class AlarmWidget(QWidget):
    """Widget for managing alarms"""
    alarm_added = pyqtSignal(QTime)
    alarm_deleted = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Alarm time input
        alarm_input_layout = QHBoxLayout()
        alarm_label = QLabel("Set Alarm:")
        self.alarm_input = QTimeEdit()
        self.alarm_input.setDisplayFormat("HH:mm")
        self.alarm_input.setTime(QTime.currentTime())
        
        add_alarm_btn = QPushButton("Add Alarm")
        add_alarm_btn.clicked.connect(self.on_add_alarm)
        
        alarm_input_layout.addWidget(alarm_label)
        alarm_input_layout.addWidget(self.alarm_input)
        alarm_input_layout.addWidget(add_alarm_btn)
        
        layout.addLayout(alarm_input_layout)
        
        # Alarms list
        self.alarms_list = QListWidget()
        layout.addWidget(QLabel("Active Alarms:"))
        layout.addWidget(self.alarms_list)
        
        # Delete alarm button
        delete_alarm_btn = QPushButton("Delete Selected Alarm")
        delete_alarm_btn.clicked.connect(self.on_delete_alarm)
        layout.addWidget(delete_alarm_btn)
        
    def on_add_alarm(self):
        """Handler for the add alarm button click"""
        alarm_time = self.alarm_input.time()
        alarm_text = alarm_time.toString("HH:mm")
        
        # Check if alarm already exists
        for i in range(self.alarms_list.count()):
            if self.alarms_list.item(i).text().startswith(alarm_text):
                QMessageBox.information(self, "Duplicate Alarm", "This alarm time already exists.")
                return
        
        # Add to list
        self.alarms_list.addItem(f"{alarm_text}")
        self.alarm_added.emit(alarm_time)
        
    def on_delete_alarm(self):
        """Handler for the delete alarm button click"""
        selected_items = self.alarms_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Selection Required", "Please select an alarm to delete.")
            return
            
        for item in selected_items:
            index = self.alarms_list.row(item)
            self.alarms_list.takeItem(index)
            self.alarm_deleted.emit(index)
            
    def remove_triggered_alarm(self, alarm_time):
        """Remove an alarm that has been triggered"""
        for i in range(self.alarms_list.count()):
            if self.alarms_list.item(i).text().startswith(alarm_time):
                self.alarms_list.takeItem(i)
                return i
        return -1


class WeatherAlarmApp(QMainWindow):
    """Main application class"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weather & Alarm App")
        self.setGeometry(100, 100, 800, 600)
        
        # Set application icon
        self.setWindowIcon(QIcon(APP_ICON_PATH))
        
        # Initialize UI
        self.init_ui()
        
        # Initialize variables
        self.alarm_threads = []
        self.alarms = []
        
        # Set up timers
        self.setup_timers()
        
    def init_ui(self):
        """Initialize the user interface"""
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Create tabs
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # Weather tab
        self.weather_widget = WeatherWidget(self)
        
        # Alarm tab
        self.alarm_widget = AlarmWidget(self)
        self.alarm_widget.alarm_added.connect(self.add_alarm)
        self.alarm_widget.alarm_deleted.connect(self.delete_alarm)
        
        # Add tabs to tab widget
        tabs.addTab(self.weather_widget, "Weather")
        tabs.addTab(self.alarm_widget, "Alarm")
        
    def setup_timers(self):
        """Set up the application timers"""
        # Update time every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(TIME_REFRESH_INTERVAL)
        
        # Update weather periodically if a location is set
        self.weather_timer = QTimer(self)
        self.weather_timer.timeout.connect(self.refresh_weather)
        self.weather_timer.start(WEATHER_REFRESH_INTERVAL)
        
        # Update time initially
        self.update_time()
        
    def update_time(self):
        """Update the time display"""
        current_time = QTime.currentTime()
        self.weather_widget.update_time(current_time)
        
    def refresh_weather(self):
        """Refresh weather data if a location is set"""
        location = self.weather_widget.location_input.text()
        if location:
            self.get_weather(location)
            
    def get_weather(self, city):
        """Fetch and process weather data for the given city"""
        try:
            params = {
                'q': city,
                'appid': API_KEY,
                'units': 'metric'
            }
            
            response = requests.get(WEATHER_API_URL, params=params)
            data = response.json()
            
            if response.status_code == 200:
                # Extract and format weather information
                weather_data = {
                    'city': f"{data['name']}, {data['sys']['country']}",
                    'temp': data['main']['temp'],
                    'description': data['weather'][0]['description'].capitalize(),
                    'humidity': data['main']['humidity'],
                    'wind': data['wind']['speed']
                }
                
                # Update UI
                self.weather_widget.update_weather_display(weather_data)
            else:
                QMessageBox.warning(self, "Weather Error", f"Error: {data.get('message', 'Unknown error')}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            
    def add_alarm(self, alarm_time):
        """Add a new alarm"""
        self.alarms.append(alarm_time)
        
        # Create and start alarm thread
        alarm_thread = AlarmThread(alarm_time)
        alarm_thread.alarm_signal.connect(self.trigger_alarm)
        alarm_thread.start()
        
        self.alarm_threads.append(alarm_thread)
        
    def delete_alarm(self, index):
        """Delete an alarm at the given index"""
        if index < len(self.alarm_threads):
            self.alarm_threads[index].stop()
            self.alarm_threads.pop(index)
            self.alarms.pop(index)
                
    def trigger_alarm(self, alarm_time):
        """Handle a triggered alarm"""
        QMessageBox.information(self, "Alarm", f"Alarm time: {alarm_time}")
        
        # Remove the triggered alarm
        index = self.alarm_widget.remove_triggered_alarm(alarm_time)
        if index >= 0 and index < len(self.alarms):
            self.alarms.pop(index)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application icon
    app_icon = QIcon(APP_ICON_PATH)
    app.setWindowIcon(app_icon)
    
    window = WeatherAlarmApp()
    window.show()
    sys.exit(app.exec_()) 