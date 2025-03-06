"""
Calendar Widget Module
------------------
This module provides the CalendarWidget class for displaying and managing calendar events in the Weather & Alarm application.
"""
import logging
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QCalendarWidget, QFrame, QDialog, QLineEdit, QTimeEdit,
    QFormLayout, QTextEdit, QMessageBox, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import QDate, QTime, Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

# Configure logging
logger = logging.getLogger(__name__)

class EventDialog(QDialog):
    """Dialog for creating and editing calendar events."""
    
    def __init__(self, parent=None, event_data=None):
        """
        Initialize the event dialog.
        
        Args:
            parent (QWidget, optional): Parent widget
            event_data (dict, optional): Event data for editing an existing event
        """
        super().__init__(parent)
        self.setWindowTitle("Add Event" if not event_data else "Edit Event")
        self.setMinimumWidth(400)
        
        # Store event data if editing
        self.event_data = event_data or {}
        
        # Initialize UI
        self.init_ui()
        
        # Fill fields if editing
        if event_data:
            self.title_edit.setText(event_data.get('title', ''))
            self.description_edit.setText(event_data.get('description', ''))
            
            if 'date' in event_data:
                self.date_edit.setSelectedDate(event_data['date'])
            
            if 'time' in event_data:
                self.time_edit.setTime(event_data['time'])
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Create form layout
        form_layout = QFormLayout()
        
        # Title field
        self.title_edit = QLineEdit()
        form_layout.addRow("Title:", self.title_edit)
        
        # Date field
        self.date_edit = QCalendarWidget()
        self.date_edit.setSelectedDate(QDate.currentDate())
        form_layout.addRow("Date:", self.date_edit)
        
        # Time field
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.currentTime())
        form_layout.addRow("Time:", self.time_edit)
        
        # Description field
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        form_layout.addRow("Description:", self.description_edit)
        
        layout.addLayout(form_layout)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        # Save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
    
    def get_event_data(self):
        """
        Get the event data from the dialog.
        
        Returns:
            dict: Event data
        """
        return {
            'title': self.title_edit.text(),
            'description': self.description_edit.toPlainText(),
            'date': self.date_edit.selectedDate(),
            'time': self.time_edit.time()
        }

class CalendarWidget(QWidget):
    """Widget for displaying and managing calendar events."""
    
    # Signal emitted when an event is added or updated
    event_updated = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        """
        Initialize the calendar widget.
        
        Args:
            parent (QWidget, optional): Parent widget
        """
        super().__init__(parent)
        
        # Initialize events dictionary
        # Key: QDate string representation, Value: list of event dictionaries
        self.events = {}
        
        # Initialize UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        
        # Add title
        title_label = QLabel("Calendar")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)
        
        # Create calendar widget
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.on_date_clicked)
        self.calendar.selectionChanged.connect(self.update_events_list)
        main_layout.addWidget(self.calendar)
        
        # Create events frame
        events_frame = QFrame()
        events_frame.setFrameShape(QFrame.StyledPanel)
        events_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #ccc;
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.8);
            }
        """)
        
        events_layout = QVBoxLayout(events_frame)
        
        # Events for selected date label
        self.events_label = QLabel("Events for Selected Date")
        self.events_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        events_layout.addWidget(self.events_label)
        
        # Events list
        self.events_list = QListWidget()
        self.events_list.setMaximumHeight(200)
        self.events_list.itemDoubleClicked.connect(self.edit_event)
        events_layout.addWidget(self.events_list)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        # Add event button
        add_button = QPushButton("Add Event")
        add_button.clicked.connect(self.add_event)
        
        # Remove event button
        remove_button = QPushButton("Remove Event")
        remove_button.clicked.connect(self.remove_event)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)
        
        events_layout.addLayout(button_layout)
        
        main_layout.addWidget(events_frame)
    
    def on_date_clicked(self, date):
        """
        Handle date clicked event.
        
        Args:
            date (QDate): Selected date
        """
        self.update_events_list()
    
    def update_events_list(self):
        """Update the events list for the selected date."""
        # Clear the list
        self.events_list.clear()
        
        # Get the selected date
        selected_date = self.calendar.selectedDate()
        
        # Update the label
        self.events_label.setText(f"Events for {selected_date.toString('MMMM d, yyyy')}")
        
        # Get events for the selected date
        date_str = selected_date.toString(Qt.ISODate)
        events = self.events.get(date_str, [])
        
        # Add events to the list
        for event in events:
            item_text = f"{event['time'].toString('hh:mm AP')} - {event['title']}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, event)
            self.events_list.addItem(item)
    
    def add_event(self):
        """Add a new event."""
        # Create event dialog
        dialog = EventDialog(self)
        
        # Show dialog
        if dialog.exec_() == QDialog.Accepted:
            # Get event data
            event_data = dialog.get_event_data()
            
            # Add event to the dictionary
            date_str = event_data['date'].toString(Qt.ISODate)
            if date_str not in self.events:
                self.events[date_str] = []
            
            self.events[date_str].append(event_data)
            
            # Update the events list
            self.update_events_list()
            
            # Emit event updated signal
            self.event_updated.emit(event_data)
            
            logger.info(f"Event added: {event_data['title']} on {date_str}")
    
    def edit_event(self, item):
        """
        Edit an existing event.
        
        Args:
            item (QListWidgetItem): Selected item
        """
        # Get event data
        event_data = item.data(Qt.UserRole)
        
        # Create event dialog
        dialog = EventDialog(self, event_data)
        
        # Show dialog
        if dialog.exec_() == QDialog.Accepted:
            # Get updated event data
            updated_data = dialog.get_event_data()
            
            # Remove old event
            old_date_str = event_data['date'].toString(Qt.ISODate)
            if old_date_str in self.events:
                self.events[old_date_str].remove(event_data)
                
                # Remove the date key if no events
                if not self.events[old_date_str]:
                    del self.events[old_date_str]
            
            # Add updated event
            new_date_str = updated_data['date'].toString(Qt.ISODate)
            if new_date_str not in self.events:
                self.events[new_date_str] = []
            
            self.events[new_date_str].append(updated_data)
            
            # Update the events list
            self.update_events_list()
            
            # Emit event updated signal
            self.event_updated.emit(updated_data)
            
            logger.info(f"Event updated: {updated_data['title']} on {new_date_str}")
    
    def remove_event(self):
        """Remove the selected event."""
        # Get the selected item
        selected_items = self.events_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select an event to remove.")
            return
        
        # Get the selected event
        item = selected_items[0]
        event_data = item.data(Qt.UserRole)
        
        # Confirm deletion
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to remove the event '{event_data['title']}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            # Remove event from the dictionary
            date_str = event_data['date'].toString(Qt.ISODate)
            if date_str in self.events:
                self.events[date_str].remove(event_data)
                
                # Remove the date key if no events
                if not self.events[date_str]:
                    del self.events[date_str]
            
            # Update the events list
            self.update_events_list()
            
            logger.info(f"Event removed: {event_data['title']} on {date_str}")
    
    def get_events_for_date(self, date):
        """
        Get events for a specific date.
        
        Args:
            date (QDate): Date to get events for
        
        Returns:
            list: List of event dictionaries
        """
        date_str = date.toString(Qt.ISODate)
        return self.events.get(date_str, [])
    
    def get_all_events(self):
        """
        Get all events.
        
        Returns:
            dict: Dictionary of events
        """
        return self.events 