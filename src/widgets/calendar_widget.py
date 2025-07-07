"""
Calendar Widget Module
------------------
This module provides the CalendarWidget class for managing calendar events in the Weather & Alarm application.
"""
import logging
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QCalendarWidget, QListWidget, QListWidgetItem, QMessageBox,
    QDialog, QTimeEdit, QLineEdit, QFormLayout, QDialogButtonBox,
    QFrame, QTextEdit, QScrollArea
)
from PyQt6.QtCore import QDate, QTime, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QColor

# Configure logging
logger = logging.getLogger(__name__)

class RoundedFrame(QFrame):
    """A custom frame with rounded corners and optional background color."""
    
    def __init__(self, parent=None, bg_color=None, border_radius=8):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)
        
        # Set background color and border radius
        style = f"""
            QFrame {{
                background-color: {bg_color if bg_color else 'rgba(35, 35, 40, 200)'};
                border-radius: {border_radius}px;
                padding: 12px;
            }}
        """
        self.setStyleSheet(style)

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
        
        # Apply modern dark theme styling
        self.setStyleSheet("""
            QDialog {
                background-color: rgba(30, 30, 40, 200);
                color: white;
            }
            QLabel {
                color: white;
                font-weight: bold;
            }
            QLineEdit, QTextEdit {
                background-color: rgba(45, 45, 55, 180);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
            }
            QLineEdit:focus, QTextEdit:focus {
                background-color: rgba(55, 55, 65, 180);
                border: 1px solid #64B5F6;
            }
            QCalendarWidget {
                background-color: rgba(35, 35, 40, 200);
                color: white;
            }
            QCalendarWidget QWidget {
                alternate-background-color: rgba(45, 45, 55, 180);
            }
            QCalendarWidget QAbstractItemView:enabled {
                background-color: rgba(35, 35, 40, 200);
                color: white;
                selection-background-color: #64B5F6;
                selection-color: white;
            }
            QTimeEdit {
                background-color: rgba(45, 45, 55, 180);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
            }
            QTimeEdit:focus {
                background-color: rgba(55, 55, 65, 180);
                border: 1px solid #64B5F6;
            }
            QPushButton {
                background-color: #64B5F6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #42A5F5;
            }
            QPushButton:pressed {
                background-color: #2196F3;
            }
            QPushButton#deleteButton {
                background-color: #EF5350;
            }
            QPushButton#deleteButton:hover {
                background-color: #E53935;
            }
            QPushButton#deleteButton:pressed {
                background-color: #D32F2F;
            }
        """)
        
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
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Create form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # Title field
        title_label = QLabel("Title")
        title_label.setStyleSheet("color: #90CAF9; font-size: 14px;")
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter event title")
        form_layout.addRow(title_label, self.title_edit)
        
        # Date field
        date_label = QLabel("Date")
        date_label.setStyleSheet("color: #90CAF9; font-size: 14px;")
        self.date_edit = QCalendarWidget()
        self.date_edit.setSelectedDate(QDate.currentDate())
        form_layout.addRow(date_label, self.date_edit)
        
        # Time field
        time_label = QLabel("Time")
        time_label.setStyleSheet("color: #90CAF9; font-size: 14px;")
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.currentTime())
        form_layout.addRow(time_label, self.time_edit)
        
        # Description field
        desc_label = QLabel("Description")
        desc_label.setStyleSheet("color: #90CAF9; font-size: 14px;")
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Enter event description")
        self.description_edit.setMaximumHeight(100)
        form_layout.addRow(desc_label, self.description_edit)
        
        layout.addLayout(form_layout)
        
        # Add buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
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
        
        # Update events list
        self.update_events_list()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Create content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(20)
        
        # Add title
        title_label = QLabel("Calendar")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #64B5F6; margin-bottom: 10px;")
        content_layout.addWidget(title_label)
        
        # Create calendar frame
        calendar_frame = RoundedFrame(bg_color="rgba(30, 30, 40, 200)")
        calendar_layout = QVBoxLayout(calendar_frame)
        calendar_layout.setContentsMargins(16, 16, 16, 16)
        calendar_layout.setSpacing(16)
        
        # Create calendar widget
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.on_date_clicked)
        self.calendar.selectionChanged.connect(self.update_events_list)
        
        # Style the calendar
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: transparent;
            }
            QCalendarWidget QWidget {
                alternate-background-color: rgba(45, 45, 55, 180);
            }
            QCalendarWidget QAbstractItemView:enabled {
                background-color: transparent;
                color: white;
                selection-background-color: #64B5F6;
                selection-color: white;
                outline: none;
                border: none;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: rgba(255, 255, 255, 0.3);
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: rgba(40, 40, 50, 150);
                border-radius: 4px;
                border: none;
            }
            QCalendarWidget QToolButton {
                color: white;
                background-color: transparent;
                padding: 6px;
                border-radius: 4px;
                border: none;
                margin: 2px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QCalendarWidget QToolButton:pressed {
                background-color: rgba(100, 181, 246, 0.2);
            }
            QCalendarWidget QSpinBox {
                background-color: rgba(45, 45, 55, 180);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px;
                margin: 0;
            }
            QCalendarWidget QMenu {
                background-color: rgba(40, 40, 50, 200);
                border: none;
                border-radius: 4px;
                padding: 4px;
                color: white;
            }
            QCalendarWidget QMenu::item {
                padding: 4px 8px;
                border-radius: 2px;
            }
            QCalendarWidget QMenu::item:selected {
                background-color: rgba(100, 181, 246, 0.2);
            }
            /* Remove grid lines */
            QCalendarWidget QTableView {
                outline: none;
                selection-background-color: rgba(100, 181, 246, 0.2);
            }
            QCalendarWidget QTableView::item:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QCalendarWidget QTableView::item:selected {
                background-color: #64B5F6;
            }
            /* Style the headers */
            QCalendarWidget QHeaderView {
                background-color: transparent;
            }
            QCalendarWidget QHeaderView::section {
                color: #90CAF9;
                background-color: transparent;
                border: none;
                padding: 6px;
                font-weight: bold;
            }
            /* Week numbers */
            QCalendarWidget QHeaderView::section:vertical {
                color: rgba(255, 255, 255, 0.5);
            }
        """)
        
        # Set calendar format
        format = self.calendar.weekdayTextFormat(Qt.DayOfWeek.Saturday)
        format.setForeground(QColor("#EF5350"))  # Material Design red
        self.calendar.setWeekdayTextFormat(Qt.DayOfWeek.Saturday, format)
        self.calendar.setWeekdayTextFormat(Qt.DayOfWeek.Sunday, format)
        
        # Set vertical header format (week numbers)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.ISOWeekNumbers)
        self.calendar.setGridVisible(False)  # Remove the grid lines
        
        calendar_layout.addWidget(self.calendar)
        content_layout.addWidget(calendar_frame)
        
        # Create events frame
        events_frame = RoundedFrame(bg_color="rgba(30, 30, 40, 200)")
        events_layout = QVBoxLayout(events_frame)
        events_layout.setContentsMargins(16, 16, 16, 16)
        events_layout.setSpacing(16)
        
        # Events for selected date label
        header_layout = QHBoxLayout()
        
        self.events_label = QLabel("Events for Selected Date")
        self.events_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #90CAF9;")
        header_layout.addWidget(self.events_label)
        
        # Add event button
        add_button = QPushButton("Add Event")
        add_button.clicked.connect(self.add_event)
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #64B5F6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #42A5F5;
            }
            QPushButton:pressed {
                background-color: #2196F3;
            }
        """)
        header_layout.addWidget(add_button)
        
        events_layout.addLayout(header_layout)
        
        # Events list
        self.events_list = QListWidget()
        self.events_list.setMaximumHeight(200)
        self.events_list.itemDoubleClicked.connect(self.edit_event)
        self.events_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(40, 40, 50, 150);
                border: none;
                border-radius: 4px;
                padding: 4px;
                color: white;
            }
            QListWidget::item {
                background-color: rgba(45, 45, 55, 180);
                border-radius: 4px;
                margin: 2px 0;
                padding: 8px;
            }
            QListWidget::item:selected {
                background-color: rgba(100, 181, 246, 100);
                color: white;
            }
            QListWidget::item:hover {
                background-color: rgba(45, 45, 60, 200);
                border: 1px solid rgba(100, 181, 246, 100);
            }
        """)
        events_layout.addWidget(self.events_list)
        
        # Add buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        # Edit event button
        edit_button = QPushButton("Edit Event")
        edit_button.clicked.connect(lambda: self.edit_event(self.events_list.currentItem()))
        
        # Remove event button
        remove_button = QPushButton("Remove Event")
        remove_button.clicked.connect(self.remove_event)
        remove_button.setObjectName("deleteButton")  # For specific styling
        remove_button.setStyleSheet("""
            QPushButton {
                background-color: #EF5350;
            }
            QPushButton:hover {
                background-color: #E53935;
            }
            QPushButton:pressed {
                background-color: #D32F2F;
            }
        """)
        
        button_layout.addWidget(edit_button)
        button_layout.addWidget(remove_button)
        
        events_layout.addLayout(button_layout)
        
        content_layout.addWidget(events_frame)
        
        # Add stretch to push everything to the top
        content_layout.addStretch()
        
        # Set the scroll content
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
    
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
        
        # Get selected date
        selected_date = self.calendar.selectedDate()
        date_str = selected_date.toString(Qt.DateFormat.ISODate)
        
        # Get events for the selected date
        events = self.get_events_for_date(selected_date)
        
        # Add events to the list
        for event in events:
            # Create list item
            item = QListWidgetItem()
            
            # Set text
            time_str = event['time'].toString('hh:mm')
            item.setText(f"{time_str} - {event['title']}")
            
            # Set data
            item.setData(Qt.ItemDataRole.UserRole, event)
            
            # Add to list
            self.events_list.addItem(item)
    
    def add_event(self):
        """Add a new event."""
        # Get the selected date
        selected_date = self.calendar.selectedDate()
        
        # Create event dialog
        dialog = EventDialog(self)
        dialog.date_edit.setSelectedDate(selected_date)
        
        # Show dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Get event data
            event_data = dialog.get_event_data()
            date_str = event_data['date'].toString(Qt.DateFormat.ISODate)
            if date_str not in self.events:
                self.events[date_str] = []
            # Add event to the correct date list
            self.events[date_str].append(event_data)
            # Update events list
            self.update_events_list()
            # Emit signal
            self.event_updated.emit(event_data)
            logger.info(f"Added event: {event_data}")
    
    def edit_event(self, item):
        """
        Edit an event.
        
        Args:
            item (QListWidgetItem): List item to edit
        """
        if not item:
            return
        
        # Get event index
        index = self.events_list.row(item)
        if index < 0 or index >= len(self.events):
            return
        
        # Get event data
        event_data = self.events[index]
        
        # Create event dialog
        dialog = EventDialog(self, event_data)
        
        # Show dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Get updated event data
            updated_data = dialog.get_event_data()
            
            # Update event
            self.events[index] = updated_data
            
            # Update events list
            self.update_events_list()
            
            # Emit signal
            self.event_updated.emit(updated_data)
            
            logger.info(f"Updated event: {updated_data}")
    
    def remove_event(self):
        """Remove the selected event."""
        # Get selected item
        selected_items = self.events_list.selectedItems()
        if not selected_items:
            return
        
        # Get event data
        item = selected_items[0]
        event_data = item.data(Qt.ItemDataRole.UserRole)
        
        # Confirm deletion
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the event '{event_data['title']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            # Remove event from the dictionary
            date_str = event_data['date'].toString(Qt.DateFormat.ISODate)
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
            list: List of events
        """
        date_str = date.toString(Qt.DateFormat.ISODate)
        return self.events.get(date_str, [])
    
    def get_all_events(self):
        """
        Get all events.
        
        Returns:
            dict: Dictionary of events
        """
        return self.events
    
    def apply_theme(self):
        """Apply the current theme to the calendar widget."""
        # This method is no longer needed as we're using RoundedFrame and modern styling
        pass