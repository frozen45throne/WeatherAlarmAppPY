"""
Alarm Manager Module
----------------
This module provides the AlarmManager class for managing alarms in the Weather & Alarm application.
"""
import logging
import json
import os
import uuid
from datetime import datetime, timedelta
from PyQt6.QtCore import QObject, QTimer, pyqtSignal, QTime

from ..config import DEFAULT_ALARM_DURATION

# Configure logging
logger = logging.getLogger(__name__)

class Alarm:
    """Class representing an alarm."""
    
    def __init__(self, time, auto_dismiss=True, duration=DEFAULT_ALARM_DURATION, enabled=True, label=""):
        """
        Initialize an alarm.
        
        Args:
            time (QTime): Time for the alarm
            auto_dismiss (bool): Whether to auto-dismiss the alarm
            duration (int): Duration in seconds before auto-dismiss
            enabled (bool): Whether the alarm is enabled
            label (str): Optional label for the alarm
        """
        self.time = time
        self.auto_dismiss = auto_dismiss
        self.duration = duration
        self.enabled = enabled
        self.label = label
        self.id = f"{time.toString('HH:mm')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def __eq__(self, other):
        """Check if two alarms are equal based on their time."""
        if not isinstance(other, Alarm):
            return False
        return self.time.hour() == other.time.hour() and self.time.minute() == other.time.minute()
    
    def to_dict(self):
        """Convert alarm to dictionary for serialization."""
        return {
            'id': self.id,
            'time': self.time.toString('HH:mm'),
            'auto_dismiss': self.auto_dismiss,
            'duration': self.duration,
            'enabled': self.enabled,
            'label': self.label
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create an alarm from a dictionary."""
        time_parts = data['time'].split(':')
        time = QTime(int(time_parts[0]), int(time_parts[1]))
        alarm = cls(
            time=time,
            auto_dismiss=data.get('auto_dismiss', True),
            duration=data.get('duration', DEFAULT_ALARM_DURATION),
            enabled=data.get('enabled', True),
            label=data.get('label', "")
        )
        alarm.id = data.get('id', alarm.id)
        return alarm
    
    def __str__(self):
        """String representation of the alarm."""
        return f"Alarm({self.time.toString('HH:mm')}, enabled={self.enabled}, label={self.label})"


class AlarmManager(QObject):
    """Manager for handling alarms."""
    
    # Signal emitted when an alarm is triggered
    alarm_triggered = pyqtSignal(Alarm)
    
    # Signal emitted when alarms are updated
    alarms_updated = pyqtSignal(list)
    
    def __init__(self, alarms_file=None):
        """
        Initialize the alarm manager.
        
        Args:
            alarms_file (str, optional): Path to the file for storing alarms
        """
        super().__init__()
        
        self.alarms = []
        self.active_alarms = {}  # Dictionary of active alarm timers
        self.alarms_file = alarms_file or os.path.expanduser("~/.wacapp_alarms.json")
        
        # Timer for checking alarms
        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.check_alarms)
        self.check_timer.start(10000)  # Check every 10 seconds
        
        # Load saved alarms
        self.load_alarms()
    
    def add_alarm(self, alarm):
        """
        Add an alarm.
        
        Args:
            alarm (Alarm): The alarm to add
            
        Returns:
            bool: True if the alarm was added, False if it already exists
        """
        # Check if alarm with same time already exists
        for existing_alarm in self.alarms:
            if existing_alarm == alarm:
                logger.warning(f"Alarm at {alarm.time.toString('HH:mm')} already exists")
                return False
        
        self.alarms.append(alarm)
        logger.info(f"Added alarm: {alarm}")
        self.save_alarms()
        self.alarms_updated.emit(self.alarms)
        return True
    
    def remove_alarm(self, alarm_id):
        """
        Remove an alarm by ID.
        
        Args:
            alarm_id (str): ID of the alarm to remove
            
        Returns:
            bool: True if the alarm was removed, False if not found
        """
        for i, alarm in enumerate(self.alarms):
            if alarm.id == alarm_id:
                removed = self.alarms.pop(i)
                logger.info(f"Removed alarm: {removed}")
                self.save_alarms()
                self.alarms_updated.emit(self.alarms)
                return True
        
        logger.warning(f"Alarm with ID {alarm_id} not found")
        return False
    
    def toggle_alarm(self, alarm_id):
        """
        Toggle an alarm's enabled state.
        
        Args:
            alarm_id (str): ID of the alarm to toggle
            
        Returns:
            bool: True if the alarm was toggled, False if not found
        """
        for alarm in self.alarms:
            if alarm.id == alarm_id:
                alarm.enabled = not alarm.enabled
                logger.info(f"Toggled alarm {alarm.id} to {alarm.enabled}")
                self.save_alarms()
                self.alarms_updated.emit(self.alarms)
                return True
        
        logger.warning(f"Alarm with ID {alarm_id} not found")
        return False
    
    def check_alarms(self):
        """Check if any alarms should be triggered."""
        current_time = QTime.currentTime()
        
        for alarm in self.alarms:
            if not alarm.enabled:
                continue
            
            alarm_time = alarm.time
            
            # Check if the alarm should be triggered
            if (current_time.hour() == alarm_time.hour() and 
                current_time.minute() == alarm_time.minute() and
                alarm.id not in self.active_alarms):
                
                logger.info(f"Triggering alarm: {alarm}")
                self.trigger_alarm(alarm)
    
    def trigger_alarm(self, alarm):
        """
        Trigger an alarm.
        
        Args:
            alarm (Alarm): The alarm to trigger
        """
        # Emit signal to notify listeners
        self.alarm_triggered.emit(alarm)
        
        # Set up auto-dismiss timer if enabled
        if alarm.auto_dismiss:
            dismiss_timer = QTimer(self)
            dismiss_timer.setSingleShot(True)
            dismiss_timer.timeout.connect(lambda: self.dismiss_alarm(alarm.id))
            dismiss_timer.start(alarm.duration * 1000)
            
            # Store the timer
            self.active_alarms[alarm.id] = dismiss_timer
    
    def dismiss_alarm(self, alarm_id):
        """
        Dismiss an active alarm.
        
        Args:
            alarm_id (str): ID of the alarm to dismiss
        """
        if alarm_id in self.active_alarms:
            # Stop and remove the timer
            timer = self.active_alarms.pop(alarm_id)
            timer.stop()
            logger.info(f"Dismissed alarm: {alarm_id}")
    
    def save_alarms(self):
        """Save alarms to file."""
        try:
            with open(self.alarms_file, 'w') as f:
                json.dump([alarm.to_dict() for alarm in self.alarms], f)
            logger.debug(f"Saved {len(self.alarms)} alarms to {self.alarms_file}")
        except Exception as e:
            logger.error(f"Error saving alarms: {str(e)}")
    
    def load_alarms(self):
        """Load alarms from file."""
        if not os.path.exists(self.alarms_file):
            logger.debug(f"Alarms file {self.alarms_file} does not exist")
            return
        
        try:
            with open(self.alarms_file, 'r') as f:
                alarm_data = json.load(f)
            
            self.alarms = [Alarm.from_dict(data) for data in alarm_data]
            logger.debug(f"Loaded {len(self.alarms)} alarms from {self.alarms_file}")
            self.alarms_updated.emit(self.alarms)
        except Exception as e:
            logger.error(f"Error loading alarms: {str(e)}")
    
    def get_alarms(self):
        """Get all alarms."""
        return self.alarms
    
    def get_alarm_by_id(self, alarm_id):
        """Get an alarm by ID."""
        for alarm in self.alarms:
            if alarm.id == alarm_id:
                return alarm
        return None 