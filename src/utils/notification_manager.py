"""
Notification Manager Module
-----------------------
This module provides the NotificationManager class for handling system notifications in the Weather & Alarm application.
"""
import logging
import os
from datetime import datetime, timedelta
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtWidgets import QSystemTrayIcon

# Configure logging
logger = logging.getLogger(__name__)

class Notification:
    """Class representing a notification."""
    
    def __init__(self, title, message, icon=None, timestamp=None, category="general", data=None):
        """
        Initialize a notification.
        
        Args:
            title (str): Notification title
            message (str): Notification message
            icon (QIcon, optional): Notification icon
            timestamp (datetime, optional): Notification timestamp
            category (str, optional): Notification category
            data (dict, optional): Additional data
        """
        self.title = title
        self.message = message
        self.icon = icon
        self.timestamp = timestamp or datetime.now()
        self.category = category
        self.data = data or {}
        self.read = False
        self.id = f"{self.timestamp.strftime('%Y%m%d%H%M%S')}-{id(self)}"
    
    def mark_as_read(self):
        """Mark the notification as read."""
        self.read = True
    
    def __str__(self):
        """Return a string representation of the notification."""
        return f"{self.title}: {self.message} ({self.timestamp.strftime('%Y-%m-%d %H:%M:%S')})"

class NotificationManager(QObject):
    """Manager for handling system notifications."""
    
    # Signal emitted when a notification is added
    notification_added = pyqtSignal(Notification)
    
    # Signal emitted when a notification is removed
    notification_removed = pyqtSignal(str)
    
    # Signal emitted when notifications are updated
    notifications_updated = pyqtSignal(list)
    
    def __init__(self, tray_icon=None):
        """
        Initialize the notification manager.
        
        Args:
            tray_icon (QSystemTrayIcon, optional): System tray icon
        """
        super().__init__()
        
        # Store the tray icon
        self.tray_icon = tray_icon
        
        # Initialize notifications list
        self.notifications = []
        
        # Initialize scheduled notifications
        self.scheduled_notifications = []
        
        # Set up timer for scheduled notifications
        self.schedule_timer = QTimer(self)
        self.schedule_timer.timeout.connect(self.check_scheduled_notifications)
        self.schedule_timer.start(60000)  # Check every minute
        
        logger.info("Notification manager initialized")
    
    def set_tray_icon(self, tray_icon):
        """
        Set the system tray icon.
        
        Args:
            tray_icon (QSystemTrayIcon): System tray icon
        """
        self.tray_icon = tray_icon
    
    def add_notification(self, title, message, icon=None, category="general", data=None, show=True):
        """
        Add a notification.
        
        Args:
            title (str): Notification title
            message (str): Notification message
            icon (QIcon, optional): Notification icon
            category (str, optional): Notification category
            data (dict, optional): Additional data
            show (bool, optional): Whether to show the notification
        
        Returns:
            Notification: The created notification
        """
        # Create notification
        notification = Notification(title, message, icon, datetime.now(), category, data)
        
        # Add to list
        self.notifications.append(notification)
        
        # Show notification if requested
        if show and self.tray_icon:
            self.show_notification(notification)
        
        # Emit signals
        self.notification_added.emit(notification)
        self.notifications_updated.emit(self.notifications)
        
        logger.info(f"Notification added: {notification}")
        
        return notification
    
    def remove_notification(self, notification_id):
        """
        Remove a notification.
        
        Args:
            notification_id (str): Notification ID
        
        Returns:
            bool: True if the notification was removed, False otherwise
        """
        # Find the notification
        for i, notification in enumerate(self.notifications):
            if notification.id == notification_id:
                # Remove from list
                removed = self.notifications.pop(i)
                
                # Emit signals
                self.notification_removed.emit(notification_id)
                self.notifications_updated.emit(self.notifications)
                
                logger.info(f"Notification removed: {removed}")
                
                return True
        
        return False
    
    def clear_notifications(self, category=None):
        """
        Clear notifications.
        
        Args:
            category (str, optional): Category to clear
        """
        if category:
            # Remove notifications of the specified category
            self.notifications = [n for n in self.notifications if n.category != category]
        else:
            # Clear all notifications
            self.notifications = []
        
        # Emit signal
        self.notifications_updated.emit(self.notifications)
        
        logger.info(f"Notifications cleared{f' for category {category}' if category else ''}")
    
    def get_notifications(self, category=None, unread_only=False):
        """
        Get notifications.
        
        Args:
            category (str, optional): Category to filter by
            unread_only (bool, optional): Whether to only return unread notifications
        
        Returns:
            list: List of notifications
        """
        # Filter notifications
        filtered = self.notifications
        
        if category:
            filtered = [n for n in filtered if n.category == category]
        
        if unread_only:
            filtered = [n for n in filtered if not n.read]
        
        return filtered
    
    def mark_all_as_read(self, category=None):
        """
        Mark all notifications as read.
        
        Args:
            category (str, optional): Category to mark as read
        """
        # Mark notifications as read
        for notification in self.notifications:
            if not category or notification.category == category:
                notification.mark_as_read()
        
        # Emit signal
        self.notifications_updated.emit(self.notifications)
        
        logger.info(f"Notifications marked as read{f' for category {category}' if category else ''}")
    
    def show_notification(self, notification):
        """
        Show a notification.
        
        Args:
            notification (Notification): Notification to show
        """
        if self.tray_icon:
            # Determine icon
            icon = notification.icon or QSystemTrayIcon.Information
            
            # Show notification
            self.tray_icon.showMessage(
                notification.title,
                notification.message,
                icon,
                5000  # Show for 5 seconds
            )
            
            logger.info(f"Notification shown: {notification}")
    
    def schedule_notification(self, title, message, when, icon=None, category="general", data=None):
        """
        Schedule a notification.
        
        Args:
            title (str): Notification title
            message (str): Notification message
            when (datetime): When to show the notification
            icon (QIcon, optional): Notification icon
            category (str, optional): Notification category
            data (dict, optional): Additional data
        
        Returns:
            dict: Scheduled notification data
        """
        # Generate a unique ID first
        unique_id = id(object())
        
        # Create scheduled notification
        scheduled = {
            'title': title,
            'message': message,
            'when': when,
            'icon': icon,
            'category': category,
            'data': data or {},
            'id': f"{when.strftime('%Y%m%d%H%M%S')}-{unique_id}"
        }
        
        # Add to list
        self.scheduled_notifications.append(scheduled)
        
        logger.info(f"Notification scheduled: {title} at {when}")
        
        return scheduled
    
    def cancel_scheduled_notification(self, notification_id):
        """
        Cancel a scheduled notification.
        
        Args:
            notification_id (str): Notification ID
        
        Returns:
            bool: True if the notification was cancelled, False otherwise
        """
        # Find the notification
        for i, notification in enumerate(self.scheduled_notifications):
            if notification['id'] == notification_id:
                # Remove from list
                removed = self.scheduled_notifications.pop(i)
                
                logger.info(f"Scheduled notification cancelled: {removed['title']}")
                
                return True
        
        return False
    
    def check_scheduled_notifications(self):
        """Check for scheduled notifications that need to be shown."""
        now = datetime.now()
        to_remove = []
        
        # Check each scheduled notification
        for scheduled in self.scheduled_notifications:
            if scheduled['when'] <= now:
                # Show the notification
                self.add_notification(
                    scheduled['title'],
                    scheduled['message'],
                    scheduled['icon'],
                    scheduled['category'],
                    scheduled['data']
                )
                
                # Mark for removal
                to_remove.append(scheduled)
        
        # Remove shown notifications
        for scheduled in to_remove:
            self.scheduled_notifications.remove(scheduled)
    
    def schedule_weather_notification(self, weather_data, when=None):
        """
        Schedule a weather notification.
        
        Args:
            weather_data (dict): Weather data
            when (datetime, optional): When to show the notification
        
        Returns:
            dict: Scheduled notification data
        """
        # Default to tomorrow morning if not specified
        if not when:
            tomorrow = datetime.now() + timedelta(days=1)
            when = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 7, 0, 0)
        
        # Extract weather information
        city = weather_data.get('city', 'Unknown')
        country = weather_data.get('country', '')
        temperature = weather_data.get('temperature', 0)
        description = weather_data.get('description', 'Unknown')
        
        # Create title and message
        title = f"Weather Forecast for {city}"
        message = f"Tomorrow's weather: {description}, {temperature}°C"
        
        # Schedule the notification
        return self.schedule_notification(
            title,
            message,
            when,
            category="weather",
            data={'weather_data': weather_data}
        )
    
    def schedule_calendar_notification(self, event_data, minutes_before=15):
        """
        Schedule a calendar event notification.
        
        Args:
            event_data (dict): Event data
            minutes_before (int, optional): Minutes before the event to show the notification
        
        Returns:
            dict: Scheduled notification data
        """
        # Extract event information
        title = event_data.get('title', 'Untitled Event')
        date = event_data.get('date')
        time = event_data.get('time')
        
        if not date or not time:
            logger.error("Cannot schedule calendar notification without date and time")
            return None
        
        # Create event datetime
        event_datetime = datetime(
            date.year(),
            date.month(),
            date.day(),
            time.hour(),
            time.minute(),
            0
        )
        
        # Calculate notification time
        notification_time = event_datetime - timedelta(minutes=minutes_before)
        
        # Don't schedule if it's in the past
        if notification_time < datetime.now():
            logger.warning(f"Not scheduling notification for past event: {title}")
            return None
        
        # Create title and message
        notification_title = f"Upcoming Event: {title}"
        notification_message = f"Event starts in {minutes_before} minutes"
        
        # Schedule the notification
        return self.schedule_notification(
            notification_title,
            notification_message,
            notification_time,
            category="calendar",
            data={'event_data': event_data}
        ) 