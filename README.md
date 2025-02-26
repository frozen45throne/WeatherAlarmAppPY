# Weather & Alarm Application

A desktop application that combines weather information and alarm functionality, built with PyQt5.

## Features

### Weather Information

- **Current Weather**:

  - Real-time weather data for any city worldwide
  - Temperature, feels like, humidity, pressure, and wind speed
  - Detailed weather description with matching icons
  - Sunrise and sunset times
  - Last updated timestamp
  - Support for metric units

- **5-Day Forecast**:

  - Daily temperature ranges (min/max)
  - Dynamic weather icons based on temperature trends
  - Weather descriptions for each day
  - Day-of-week display

- **User Interface**:
  - Clean, modern design with material styling
  - Responsive search with Enter key support
  - Location saving for quick access
  - Auto-refresh every 30 minutes
  - Manual refresh option
  - Scrollable interface for all weather information

### Alarm Management

- Set and manage multiple alarms
- Auto-dismiss options
- Visual alarm list
- Delete functionality for existing alarms

### System Integration

- System tray support for background operation
- Minimized operation support
- Automatic error handling and logging
- Graceful handling of API issues

## Requirements

- Python 3.6+
- PyQt5
- Requests

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/weather-alarm-app.git
   cd weather-alarm-app
   ```

2. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python run.py
   ```

## Configuration

### API Key Setup

The application uses OpenWeatherMap API for weather data. You can set your API key in three ways:

1. Environment variable: `OPENWEATHER_API_KEY`
2. Settings tab in the application
3. Direct configuration in config.py

### Weather Icons

The application supports both SVG and PNG weather icons, located in:

- `weather_icons/` directory
- `animation-ready/` directory

## Usage

### Weather Tab

1. Enter a city name in the search box
2. Press Enter or click "Search" to get weather data
3. View current weather details:
   - Temperature and feels like
   - Weather description with icon
   - Humidity, pressure, wind speed
   - Sunrise and sunset times
4. Check the 5-day forecast:
   - Daily temperature ranges
   - Weather icons specific to predicted conditions
   - Day names and descriptions

### Alarms Tab

1. Set alarm time using the time picker
2. Configure auto-dismiss options
3. Add optional alarm label
4. Manage alarms through the list interface

### Settings Tab

Configure:

- Theme preferences
- API key
- Default city
- Units (metric/imperial)
- Alarm settings

## Development Structure

```
WACAppPush/
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── weather_service.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── alarm_manager.py
│   │   ├── svg_handler.py
│   │   └── theme_manager.py
│   └── widgets/
│       ├── __init__.py
│       ├── alarm_widget.py
│       ├── settings_widget.py
│       └── weather_widget.py
├── weather_icons/
├── animation-ready/
├── run.py
├── requirements.txt
└── README.md
```

## Error Handling

The application includes comprehensive error handling for:

- Missing API keys
- Network connectivity issues
- Invalid city names
- Missing weather icons
- System tray integration

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Weather data provided by [OpenWeatherMap](https://openweathermap.org/)
- Icons from various open-source projects
- PyQt5 for the GUI framework
