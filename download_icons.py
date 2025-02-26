"""
Download Weather Icons
--------------------
This script downloads weather icons for the Weather & Alarm application.
"""
import os
import requests
import shutil

# Base URL for weather icons
ICON_BASE_URL = "https://openweathermap.org/img/wn/"

# Weather conditions and their codes
WEATHER_CONDITIONS = [
    "01d", "01n",  # clear sky
    "02d", "02n",  # few clouds
    "03d", "03n",  # scattered clouds
    "04d", "04n",  # broken clouds
    "09d", "09n",  # shower rain
    "10d", "10n",  # rain
    "11d", "11n",  # thunderstorm
    "13d", "13n",  # snow
    "50d", "50n",  # mist
]

def download_icons():
    """Download weather icons from OpenWeatherMap."""
    # Create weather_icons directory if it doesn't exist
    icons_dir = os.path.join(os.path.dirname(__file__), "weather_icons")
    os.makedirs(icons_dir, exist_ok=True)
    
    print("Downloading weather icons...")
    
    # Download each icon
    for code in WEATHER_CONDITIONS:
        # Construct URL for 2x size icons
        url = f"{ICON_BASE_URL}{code}@2x.png"
        
        # Construct file path
        file_path = os.path.join(icons_dir, f"{code}.png")
        
        try:
            # Download the icon
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Save the icon
            with open(file_path, 'wb') as f:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, f)
            
            print(f"Downloaded {code}.png")
            
        except Exception as e:
            print(f"Error downloading {code}.png: {str(e)}")
    
    print("\nDownload complete!")

if __name__ == "__main__":
    download_icons() 