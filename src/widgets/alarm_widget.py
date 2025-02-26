"""
Alarm Widget Module
-----------------
This module provides the AlarmWidget class for managing alarms in the Weather & Alarm application.
"""
import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTimeEdit, QCheckBox, QListWidget, QListWidgetItem, 
    QMessageBox, QScrollArea, QFrame, QSpinBox, QLineEdit
)
from PyQt5.QtCore import QTime, pyqtSignal, Qt
from PyQt5.QtGui import QIcon

from ..utils.alarm_manager import Alarm

# Configure logging
logger = logging.getLogger(__name__)

class AlarmWidget(QWidget):
    """Widget for managing alarms."""
    
    # Signal emitted when an alarm is added
    alarm_added = pyqtSignal(Alarm)
    
    # Signal emitted when an alarm is deleted
    alarm_deleted = pyqtSignal(str)  # Alarm ID
    
    def __init__(self, parent=None):
        """
        Initialize the alarm widget.
        
        Args:
            parent (QWidget, optional): Parent widget
        """
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create a scroll area for the content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Create a widget to hold the scrollable content
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(16, 16, 16, 16)
        scroll_layout.setSpacing(16)
        
        # Add title
        title_label = QLabel("Alarms")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        scroll_layout.addWidget(title_label)
        
        # Add alarm time input
        time_layout = QHBoxLayout()
        time_label = QLabel("Set alarm time:")
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        self.time_edit.setTime(QTime.currentTime())
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_edit)
        scroll_layout.addLayout(time_layout)
        
        # Add auto-dismiss options
        dismiss_layout = QHBoxLayout()
        self.auto_dismiss_checkbox = QCheckBox("Auto-dismiss after")
        self.auto_dismiss_checkbox.setChecked(True)
        self.duration_spinbox = QSpinBox()
        self.duration_spinbox.setRange(10, 300)
        self.duration_spinbox.setValue(60)
        self.duration_spinbox.setSuffix(" seconds")
        dismiss_layout.addWidget(self.auto_dismiss_checkbox)
        dismiss_layout.addWidget(self.duration_spinbox)
        dismiss_layout.addStretch()
        scroll_layout.addLayout(dismiss_layout)
        
        # Add alarm label input
        label_layout = QHBoxLayout()
        label_label = QLabel("Alarm label (optional):")
        self.label_edit = QLineEdit()
        self.label_edit.setPlaceholderText("Enter a label for this alarm")
        label_layout.addWidget(label_label)
        label_layout.addWidget(self.label_edit)
        scroll_layout.addLayout(label_layout)
        
        # Add button
        add_button = QPushButton("Add Alarm")
        add_button.clicked.connect(self.on_add_alarm)
        scroll_layout.addWidget(add_button)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        scroll_layout.addWidget(separator)
        
        # Add alarms list
        alarms_label = QLabel("Active Alarms")
        alarms_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        scroll_layout.addWidget(alarms_label)
        
        self.alarms_list = QListWidget()
        self.alarms_list.setSelectionMode(QListWidget.SingleSelection)
        self.alarms_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px;
            }
            QListWidget::item {
                border-bottom: 1px solid #eee;
                padding: 8px;
            }
            QListWidget::item:selected {
                background-color: #e0e0e0;
                color: #000;
            }
        """)
        scroll_layout.addWidget(self.alarms_list)
        
        # Add delete button
        delete_button = QPushButton("Delete Selected Alarm")
        delete_button.clicked.connect(self.on_delete_alarm)
        scroll_layout.addWidget(delete_button)
        
        # Add stretch to push everything to the top
        scroll_layout.addStretch()
        
        # Set the scroll content
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
    
    def on_add_alarm(self):
        """Handle adding a new alarm."""
        # Get the alarm time
        alarm_time = self.time_edit.time()
        
        # Create a new alarm
        alarm = Alarm(
            time=alarm_time,
            auto_dismiss=self.auto_dismiss_checkbox.isChecked(),
            duration=self.duration_spinbox.value(),
            label=self.label_edit.text()
        )
        
        # Check if an alarm with the same time already exists
        for i in range(self.alarms_list.count()):
            item = self.alarms_list.item(i)
            if item.data(Qt.UserRole) == alarm:
                QMessageBox.warning(
                    self,
                    "Duplicate Alarm",
                    f"An alarm at {alarm_time.toString('HH:mm')} already exists."
                )
                return
        
        # Add the alarm to the list
        self._add_alarm_to_list(alarm)
        
        # Emit the signal
        self.alarm_added.emit(alarm)
        
        # Reset the form
        self.time_edit.setTime(QTime.currentTime())
        self.label_edit.clear()
        
        logger.info(f"Added alarm: {alarm}")
    
    def on_delete_alarm(self):
        """Handle deleting an alarm."""
        # Get the selected item
        selected_items = self.alarms_list.selectedItems()
        if not selected_items:
            QMessageBox.information(
                self,
                "No Selection",
                "Please select an alarm to delete."
            )
            return
        
        # Get the alarm
        item = selected_items[0]
        alarm = item.data(Qt.UserRole)
        
        # Confirm deletion
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the alarm at {alarm.time.toString('HH:mm')}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            # Remove the item from the list
            row = self.alarms_list.row(item)
            self.alarms_list.takeItem(row)
            
            # Emit the signal
            self.alarm_deleted.emit(alarm.id)
            
            logger.info(f"Deleted alarm: {alarm}")
    
    def _add_alarm_to_list(self, alarm):
        """
        Add an alarm to the list widget.
        
        Args:
            alarm (Alarm): The alarm to add
        """
        # Create a list item
        item = QListWidgetItem()
        
        # Set the text
        time_str = alarm.time.toString("HH:mm")
        label_str = f" - {alarm.label}" if alarm.label else ""
        auto_dismiss_str = " (Auto-dismiss)" if alarm.auto_dismiss else ""
        item.setText(f"{time_str}{label_str}{auto_dismiss_str}")
        
        # Store the alarm as item data
        item.setData(Qt.UserRole, alarm)
        
        # Add the item to the list
        self.alarms_list.addItem(item)
    
    def update_alarms(self, alarms):
        """
        Update the alarms list.
        
        Args:
            alarms (list): List of Alarm objects
        """
        # Clear the list
        self.alarms_list.clear()
        
        # Add each alarm
        for alarm in alarms:
            self._add_alarm_to_list(alarm)
        
        logger.debug(f"Updated alarms list with {len(alarms)} alarms")
    
    def get_alarms(self):
        """
        Get all alarms in the list.
        
        Returns:
            list: List of Alarm objects
        """
        alarms = []
        for i in range(self.alarms_list.count()):
            item = self.alarms_list.item(i)
            alarm = item.data(Qt.UserRole)
            alarms.append(alarm)
        return alarms 