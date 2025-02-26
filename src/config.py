"""
Weather & Alarm Application Configuration
----------------------------------------
This module contains configuration constants for the Weather & Alarm application.
"""
import os

# Get the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Directory for weather icons
WEATHER_ICONS_DIR = os.path.join(SCRIPT_DIR, "weather_icons")

# Path to the external weather SVG icons
EXTERNAL_WEATHER_ICONS_PATH = os.path.join(SCRIPT_DIR, "animation-ready")

# Application icon path
APP_ICON_PATH = os.path.join(SCRIPT_DIR, "icons", "app_icon.ico")

# API Configuration
# Try to get API key from environment variable first
API_KEY = os.environ.get("OPENWEATHER_API_KEY", "7be574ba31d45bd6fdeb6c36ef30ed70")  # Default API key if not set in environment
WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"
ONECALL_API_URL = "http://api.openweathermap.org/data/2.5/onecall"
AIR_QUALITY_API_URL = "http://api.openweathermap.org/data/2.5/air_pollution"

# Refresh intervals
WEATHER_REFRESH_INTERVAL = 1800000  # 30 minutes in milliseconds
TIME_REFRESH_INTERVAL = 1000  # 1 second in milliseconds

# Default alarm duration in seconds
DEFAULT_ALARM_DURATION = 60

# Add a list of potential animated SVG patterns to try
ANIMATED_SVG_PATTERNS = [
    "{name}-animated.svg",
    "{name}_animated.svg",
    "animated-{name}.svg",
    "animated_{name}.svg",
    "{name}-anim.svg",
    "{name}_anim.svg",
    "anim-{name}.svg",
    "anim_{name}.svg"
]

# Update the WEATHER_ICONS dictionary to map weather codes to SVG filenames
WEATHER_ICONS = {
    # Clear weather
    "01d": "clear-day.svg",          # clear sky day
    "01n": "clear-night.svg",        # clear sky night
    
    # Partly cloudy
    "02d": "partly-cloudy-day.svg",  # few clouds day
    "02n": "partly-cloudy-night.svg",# few clouds night
    
    # Cloudy
    "03d": "cloudy.svg",             # scattered clouds
    "03n": "cloudy.svg",             # scattered clouds
    "04d": "overcast-day.svg",       # broken clouds day
    "04n": "overcast-night.svg",     # broken clouds night
    
    # Rain
    "09d": "partly-cloudy-day-rain.svg",  # shower rain day
    "09n": "partly-cloudy-night-rain.svg", # shower rain night
    "10d": "rain.svg",                    # rain day
    "10n": "rain.svg",                    # rain night
    
    # Thunderstorms
    "11d": "thunderstorms-day.svg",      # thunderstorm day
    "11n": "thunderstorms-night.svg",    # thunderstorm night
    
    # Snow
    "13d": "snow.svg",               # snow
    "13n": "snow.svg",               # snow
    
    # Mist/Fog
    "50d": "mist.svg",               # mist day
    "50n": "mist.svg",               # mist night
}

# Add a default fallback SVG for unknown weather conditions
DEFAULT_WEATHER_ICON = "not-available.svg"

# Map for alternative SVG filenames if the exact ones aren't available
SVG_ALTERNATIVES = {
    "clear-day.svg": ["day.svg", "sunny.svg", "sun.svg"],
    "clear-night.svg": ["night.svg", "moon.svg", "moon-full.svg", "starry-night.svg"],
    "partly-cloudy-day.svg": ["cloudy-day.svg", "day-cloudy.svg"],
    "partly-cloudy-night.svg": ["cloudy-night.svg", "night-cloudy.svg"],
    "cloudy.svg": ["cloud.svg", "clouds.svg", "overcast.svg"],
    "overcast-day.svg": ["cloudy.svg", "cloud.svg"],
    "overcast-night.svg": ["cloudy.svg", "cloud.svg"],
    "partly-cloudy-day-rain.svg": ["rain.svg", "rainy.svg", "showers.svg"],
    "partly-cloudy-night-rain.svg": ["rain.svg", "rainy.svg", "showers.svg"],
    "rain.svg": ["rainy.svg", "showers.svg", "raindrops.svg"],
    "thunderstorms-day.svg": ["thunderstorms.svg", "storm.svg", "lightning.svg", "thunder.svg", "lightning-bolt.svg"],
    "thunderstorms-night.svg": ["thunderstorms.svg", "storm.svg", "lightning.svg", "thunder.svg", "lightning-bolt.svg"],
    "snow.svg": ["snowy.svg", "snowflake.svg", "sleet.svg"],
    "mist.svg": ["fog.svg", "haze.svg", "partly-cloudy-day-fog.svg", "partly-cloudy-night-fog.svg"],
    "not-available.svg": ["default.svg", "unknown.svg"]
} 