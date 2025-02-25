# Weather and Alarm Application

A Python application that combines weather information and alarm functionality using PyQt5.

## Features

- **Weather Information**: Get current weather data for any city using OpenWeatherMap API
- **Alarm System**: Set and manage multiple alarms

## Installation

1. Clone this repository or download the files
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Get an API key from [OpenWeatherMap](https://openweathermap.org/api) (free tier is sufficient)
4. Replace `YOUR_API_KEY` in `main.py` with your actual API key

## Usage

Run the application:

```
python main.py
```

### Weather Tab

- Enter a city name in the input field
- Click "Get Weather" or press Enter to fetch current weather data
- Weather information will display below (temperature, description, humidity, wind speed)

### Alarm Tab

- Set the desired time using the time picker
- Click "Add Alarm" to create a new alarm
- Active alarms are displayed in the list
- Select an alarm and click "Delete Selected Alarm" to remove it

## Requirements

- Python 3.6+
- PyQt5
- Requests library
- Internet connection (for weather data)
