# Weather & Alarm Application

A modern desktop application that combines weather information, alarm management, note-taking, calendar, and notifications, built with PyQt6. The app features a fully modernized UI, borderless window, and advanced system integration.

## What's New (2025)

- **Modern borderless window** with custom title bar and window controls
- **Card-based layouts** for weather and forecast, with improved readability
- **Enhanced alarm management**: modern time picker, improved alarm list
- **Comprehensive note-taking** and **calendar** features
- **Notification center**: cards, history, mark as read/unread, clear all
- **System tray support** and background operation
- **Improved error handling** and logging
- **Refined dark theme** with semi-transparent elements and better contrast

## Features

### Modern UI Design & Experience

- **Consistent Design Language**:

  - Dark theme with semi-transparent backgrounds
  - Rounded corners and modern containers
  - Blue accent color scheme (#2196F3, #90CAF9)
  - Consistent spacing and padding across all widgets
  - Improved visual hierarchy and typography
  - **New**: Borderless window mode with custom title bar and custom window controls for a sleek, modern appearance

- **Enhanced Interactive Elements**:

  - Modern buttons with hover/pressed states
  - Improved input controls with placeholder text
  - Custom scrollbars with modern styling
  - Smooth transitions and hover effects
  - Focus states with blue accent borders
  - **New**: Custom window controls (minimize, maximize, close) with hover effects and intuitive color feedback

- **Layout Improvements**:
  - Zero-margin main layouts with scroll areas
  - 20px content padding for better readability
  - 24px spacing between sections
  - Consistent rounded frames with 10px radius
  - Better organization of information
  - **New**: Subtle window shadow effect for depth and modern aesthetics
  - **New**: Rounded window corners for a modern look

### Weather Information

- **Current Weather**:

  - Real-time weather data for any city worldwide
  - Temperature, feels like, humidity, pressure, and wind speed
  - Detailed weather description with matching icons
  - Sunrise and sunset times
  - Last updated timestamp
  - Support for metric units
  - **New**: Modern card-based layout with improved readability and visual feedback

- **5-Day Forecast**:

  - Daily temperature ranges (min/max)
  - Dynamic weather icons based on temperature trends
  - Weather descriptions for each day
  - Day-of-week display
  - **New**: Enhanced forecast cards with better visual separation and dynamic icons

- **Weather Map**: _(Feature currently disabled)_

  - The interactive weather map feature is temporarily unavailable in this version.
  - Map-related controls and layers are disabled.
  - This section will be updated when the feature is re-enabled in a future release.

- **User Interface**:
  - Clean, modern design with material styling
  - Responsive search with Enter key support
  - Location saving for quick access
  - Auto-refresh every 30 minutes
  - Manual refresh option
  - Scrollable interface for all weather information
  - **New**: Enhanced visual feedback for user interactions and scrollable interface

### Alarm Management

- Set and manage multiple alarms
- Auto-dismiss options
- Visual alarm list with improved styling
- Delete functionality for existing alarms
- **New**: Modern time picker, enhanced alarm list, and visual feedback

### Note-Taking

- Create, edit, and delete notes
- Organize notes by categories
- Filter notes by text search and category
- Sort notes by creation date (newest first)
- Persistent storage of notes between sessions
- Add custom categories for better organization
- Clean, intuitive interface for note management
- **New**: Enhanced note cards, improved dialog styling, and better filtering

### Calendar

- Add and manage calendar events
- Day, week, and month views
- Event reminders and notifications
- Color-coded event categories
- Recurring event support
- Event search functionality
- Integration with the notification system
- **New**: Modern calendar styling, improved date selection, and event display

### Notifications

- System-wide notifications for important events
- Weather forecast notifications
- Alarm notifications with sound
- Calendar event reminders
- Customizable notification settings
- Notification history and management
- Mark as read/unread functionality
- Clear all or individual notifications
- **New**: Enhanced notification cards, improved visual hierarchy, notification center, and persistent history

### System Integration & Error Handling

- System tray support for background operation
- Minimized operation support
- Automatic error handling and logging
- Graceful handling of API issues
- Improved error messages for missing API keys, network issues, and invalid input

### Theming & Visual Feedback

- Modern dark theme throughout the application
- Material Design color schemes
- Consistent styling across all widgets
- **New**: Enhanced dark theme with semi-transparent elements, improved contrast, and visual feedback for all interactions

## Requirements

- Python 3.6+
- PyQt6
- PyQt6-WebEngine
- Requests
- python-dateutil

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/frozen45throne/WeatherAlarmAppPY.git
   cd WeatherAlarmAppPY
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

The application features a modern dark theme with:

- Semi-transparent backgrounds
- Blue accent colors
- Consistent rounded corners
- Improved typography and spacing

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
│       ├── calendar_widget.py
│       ├── note_widget.py
│       ├── notification_widget.py
│       ├── settings_widget.py
│       ├── weather_map_widget.py
│       └── weather_widget.py
```

## UI Improvements

The application has undergone a comprehensive UI modernization with the following key improvements:

1. **Consistent Component Design**

   - Added `RoundedFrame` component across all widgets for consistent container styling
   - Standardized button styling with hover and pressed states
   - Unified input field styling with consistent padding and borders
   - Improved scrollbar styling for a modern look
   - **New**: Borderless window with custom title bar and window controls

2. **Enhanced Visual Hierarchy**

   - Larger, bolder titles (28px) with accent color (#90CAF9)
   - Consistent section headings and spacing
   - Better content organization with proper padding and margins
   - Improved contrast for better readability
   - **New**: Window shadow effect for depth perception

3. **Modern Color Scheme**

   - Dark theme with semi-transparent backgrounds
   - Blue accent colors (#2196F3, #90CAF9)
   - Subtle borders with rgba(255, 255, 255, 0.1)
   - Consistent hover and focus states
   - **New**: Custom window controls with intuitive color feedback

4. **Improved Layouts**

   - Zero-margin main layouts with scroll areas
   - 20px content padding
   - 24px spacing between sections
   - Consistent rounded frames with 10px radius
   - **New**: Rounded window corners for a modern look

5. **Interactive Elements**
   - Hover effects on all clickable elements
   - Focus states with blue borders
   - Improved button styling with visual feedback
   - Enhanced form controls with better styling
   - **New**: Window dragging functionality via title bar

These improvements create a cohesive, modern user experience across all widgets in the application.

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
- PyQt6 for the GUI framework
