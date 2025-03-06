# Weather & Alarm Application

A desktop application that combines weather information, alarm functionality, and note-taking capabilities, built with PyQt5.

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

- **Weather Map**:

  - Interactive weather map visualization
  - Multiple map layers (clouds, precipitation, temperature, wind)
  - Zoom and pan functionality
  - Real-time updates with location changes

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

### Note-Taking

- Create, edit, and delete notes
- Organize notes by categories
- Filter notes by text search and category
- Sort notes by creation date (newest first)
- Persistent storage of notes between sessions
- Add custom categories for better organization
- Clean, intuitive interface for note management

### Calendar

- Add and manage calendar events
- Day, week, and month views
- Event reminders and notifications
- Color-coded event categories
- Recurring event support
- Event search functionality
- Integration with the notification system

### Notifications

- System-wide notifications for important events
- Weather forecast notifications
- Alarm notifications with sound
- Calendar event reminders
- Customizable notification settings
- Notification history and management
- Mark as read/unread functionality
- Clear all or individual notifications

### System Integration

- System tray support for background operation
- Minimized operation support
- Automatic error handling and logging
- Graceful handling of API issues

### Theming

- Light and dark theme support
- System theme detection
- Material Design color schemes
- Consistent styling across all widgets
- Dynamic theme switching without application restart

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

### Theme Configuration

The application supports three theme modes:

1. **Light Theme**: A clean, light-colored interface
2. **Dark Theme**: A modern dark interface that reduces eye strain
3. **System Theme**: Automatically follows your system's theme settings

You can change the theme in the Settings tab. Theme changes are applied immediately and saved for future sessions.

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

### Weather Map Tab

1. Navigate to the Weather Map tab
2. View the interactive weather map for your current location
3. Change map layers using the dropdown menu:
   - Clouds
   - Precipitation
   - Temperature
   - Wind
4. Zoom in/out and pan to explore different regions
5. The map automatically updates when you search for a new location

### Alarms Tab

1. Set alarm time using the time picker
2. Configure auto-dismiss options
3. Add optional alarm label
4. Manage alarms through the list interface

### Notes Tab

1. Create new notes with the "New Note" button
2. Enter a title, content, and select a category
3. View all notes in the list, sorted by creation date
4. Filter notes by:
   - Text search (searches in titles and content)
   - Category selection
5. Edit notes by double-clicking or selecting and clicking "Edit"
6. Delete notes with the "Delete" button
7. Add custom categories with the "Add Category" button

### Calendar Tab

1. Navigate to the Calendar tab
2. Choose between day, week, or month views
3. Add new events by clicking on a date/time slot
4. Configure event details:
   - Title and description
   - Start and end times
   - Category/color
   - Reminder settings
5. Edit events by double-clicking on them
6. Delete events using the context menu
7. Search for events using the search bar

### Notifications Tab

1. View all notifications in the Notifications tab
2. Filter notifications by type:
   - All
   - Weather
   - Alarms
   - Calendar
   - System
3. Mark notifications as read/unread
4. Clear individual notifications or all at once
5. Click on a notification to navigate to the relevant section

### Settings Tab

Configure:

- Theme preferences (Light, Dark, or System)
- API key
- Default city
- Units (metric/imperial)
- Alarm settings
- Notification preferences
- Calendar display options

## Development Structure

```
WACAppPush/
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── weather_service.py
│   │   └── calendar_service.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── alarm_manager.py
│   │   ├── svg_handler.py
│   │   ├── theme_manager.py
│   │   └── notification_manager.py
│   └── widgets/
│       ├── __init__.py
│       ├── alarm_widget.py
│       ├── note_widget.py
│       ├── settings_widget.py
│       ├── weather_widget.py
│       ├── weather_map_widget.py
│       ├── calendar_widget.py
│       └── notification_widget.py
├── weather_icons/
├── animation-ready/
├── run.py
├── requirements.txt
└── README.md
```

## Recent Updates

### New Features

The application has been enhanced with several new features:

- **Interactive Weather Map**: View weather patterns on an interactive map with multiple layer options
- **Calendar Integration**: Manage events and appointments with day, week, and month views
- **Notification System**: Stay informed with a comprehensive notification system for weather, alarms, and calendar events

### Dark Theme Improvements

The application has been updated with the following improvements to the dark theme:

- Fixed inconsistent background colors in weather displays
- Removed hardcoded light background colors from UI components
- Enhanced container widget styling for better theme consistency
- Improved text contrast in dark mode
- Added transparent backgrounds for scrollable areas
- Updated hover effects to work well in both light and dark themes
- Ensured proper theme application across all widgets

These changes ensure a consistent and visually appealing dark theme experience throughout the application.

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
