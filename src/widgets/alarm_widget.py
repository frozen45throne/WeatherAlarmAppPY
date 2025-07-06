"""
Alarm Widget Module
-----------------
This module provides the AlarmWidget class for managing alarms in the Weather & Alarm application.
"""
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTimeEdit, QCheckBox, QListWidget, QListWidgetItem, 
    QMessageBox, QScrollArea, QFrame, QSpinBox, QLineEdit,
    QAbstractItemView, QSizePolicy
)
from PyQt6.QtCore import QTime, pyqtSignal, Qt, QSize
from PyQt6.QtGui import QIcon, QPalette, QColor, QFont

from ..utils.alarm_manager import Alarm
from ..utils.path_utils import get_icon_path

# Configure logging
logger = logging.getLogger(__name__)

class RoundedFrame(QFrame):
    """A custom frame with rounded corners and optional background color."""
    
    def __init__(self, parent=None, bg_color=None, border_radius=10):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)
        
        # Set background color and border radius
        style = f"""
            QFrame {{
                background-color: {bg_color if bg_color else 'rgba(35, 35, 40, 0.7)'};
                border-radius: {border_radius}px;
                padding: 16px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
        """
        self.setStyleSheet(style)

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
        main_layout.setSpacing(0)
        
        # Create a scroll area with modern styling
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(255, 255, 255, 0.1);
                width: 8px;
                border-radius: 4px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.4);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Create content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(24)
        
        # Add title with modern styling
        title_label = QLabel("Alarms")
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #90CAF9;
            margin-bottom: 16px;
            padding-left: 4px;
        """)
        content_layout.addWidget(title_label)
        
        # Create new alarm section with enhanced styling
        new_alarm_frame = RoundedFrame(bg_color="rgba(40, 40, 50, 0.7)")
        new_alarm_layout = QVBoxLayout(new_alarm_frame)
        new_alarm_layout.setSpacing(20)
        
        # Add "New Alarm" label with updated styling
        new_alarm_label = QLabel("New Alarm")
        new_alarm_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #90CAF9;
            margin-bottom: 8px;
        """)
        new_alarm_layout.addWidget(new_alarm_label)
        
        # Create the alarm form
        form_layout = QVBoxLayout()
        form_layout.setSpacing(16)
        
        # Time input
        time_layout = QHBoxLayout()
        time_layout.setSpacing(16)
        
        time_label = QLabel("Time:")
        time_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9);
            font-size: 15px;
        """)
        
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("hh:mm")
        self.time_edit.setTime(QTime.currentTime())
        self.time_edit.setMinimumSize(QSize(120, 36))
        self.time_edit.setStyleSheet("""
            QTimeEdit {
                background-color: rgba(50, 50, 60, 0.7);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 15px;
            }
            QTimeEdit:focus {
                background-color: rgba(60, 60, 70, 0.7);
                border: 1px solid #64B5F6;
            }
            QTimeEdit::up-button, QTimeEdit::down-button {
                width: 20px;
                background-color: rgba(60, 60, 70, 0.7);
                border-radius: 4px;
            }
            QTimeEdit::up-button:hover, QTimeEdit::down-button:hover {
                background-color: rgba(70, 70, 80, 0.7);
            }
        """)
        
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_edit)
        time_layout.addStretch()
        
        form_layout.addLayout(time_layout)
        
        # Days of week
        days_layout = QHBoxLayout()
        days_layout.setSpacing(16)
        
        days_label = QLabel("Repeat:")
        days_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9);
            font-size: 15px;
        """)
        days_layout.addWidget(days_label)
        
        # Get the absolute path to the check.svg icon
        check_icon = get_icon_path("check.svg")
        
        self.day_checkboxes = []
        for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
            checkbox = QCheckBox(day)
            checkbox.setStyleSheet(f"""
                QCheckBox {{
                    color: rgba(255, 255, 255, 0.9);
                    font-size: 14px;
                    spacing: 4px;
                }}
                QCheckBox::indicator {{
                    width: 18px;
                    height: 18px;
                    border-radius: 4px;
                    background-color: rgba(50, 50, 60, 0.7);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }}
                QCheckBox::indicator:checked {{
                    background-color: #2196F3;
                    border: none;
                    image: url({check_icon});
                }}
                QCheckBox::indicator:hover {{
                    background-color: rgba(60, 60, 70, 0.7);
                }}
            """)
            self.day_checkboxes.append(checkbox)
            days_layout.addWidget(checkbox)
        
        form_layout.addLayout(days_layout)
        
        # Add auto-dismiss options with modern styling
        dismiss_layout = QHBoxLayout()
        dismiss_layout.setSpacing(12)
        
        self.auto_dismiss_checkbox = QCheckBox("Auto-dismiss after")
        self.auto_dismiss_checkbox.setChecked(True)
        self.auto_dismiss_checkbox.setStyleSheet("""
            QCheckBox {
                color: rgba(255, 255, 255, 0.9);
                font-size: 15px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 4px;
                background-color: rgba(50, 50, 60, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            QCheckBox::indicator:checked {
                background-color: #2196F3;
                border: none;
                image: url(D:/Coding/Python/WACAppPush/icons/check.svg);
            }
            QCheckBox::indicator:hover {
                background-color: rgba(60, 60, 70, 0.7);
            }
        """)
        
        self.duration_spinbox = QSpinBox()
        self.duration_spinbox.setRange(10, 300)
        self.duration_spinbox.setValue(60)
        self.duration_spinbox.setSuffix(" seconds")
        self.duration_spinbox.setMinimumSize(QSize(120, 36))
        self.duration_spinbox.setStyleSheet("""
            QSpinBox {
                background-color: rgba(50, 50, 60, 0.7);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 15px;
            }
            QSpinBox:focus {
                background-color: rgba(60, 60, 70, 0.7);
                border: 1px solid #64B5F6;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: transparent;
                border: none;
                width: 20px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 3px;
            }
        """)
        
        dismiss_layout.addWidget(self.auto_dismiss_checkbox)
        dismiss_layout.addWidget(self.duration_spinbox)
        dismiss_layout.addStretch()
        new_alarm_layout.addLayout(dismiss_layout)
        
        # Add alarm label input with enhanced styling
        label_layout = QHBoxLayout()
        label_layout.setSpacing(12)
        
        label_label = QLabel("Alarm label (optional):")
        label_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9);
            font-size: 15px;
        """)
        
        self.label_edit = QLineEdit()
        self.label_edit.setPlaceholderText("Enter a label for this alarm")
        self.label_edit.setMinimumSize(QSize(0, 36))
        self.label_edit.setStyleSheet("""
            QLineEdit {
                background-color: rgba(50, 50, 60, 0.7);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 15px;
            }
            QLineEdit:focus {
                background-color: rgba(60, 60, 70, 0.7);
                border: 1px solid #64B5F6;
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.5);
            }
        """)
        
        label_layout.addWidget(label_label)
        label_layout.addWidget(self.label_edit)
        new_alarm_layout.addLayout(label_layout)
        
        content_layout.addWidget(new_alarm_frame)
        
        # Create active alarms section with modern styling
        active_alarms_frame = RoundedFrame(bg_color="rgba(40, 40, 50, 0.7)")
        active_alarms_layout = QVBoxLayout(active_alarms_frame)
        active_alarms_layout.setSpacing(20)
        
        # Add "Active Alarms" label and delete button in a header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)
        
        active_alarms_label = QLabel("Active Alarms")
        active_alarms_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #90CAF9;
        """)
        header_layout.addWidget(active_alarms_label)
        
        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(self.on_delete_alarm)
        delete_button.setMinimumSize(QSize(120, 36))
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #EF5350;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E57373;
            }
            QPushButton:pressed {
                background-color: #F44336;
            }
        """)
        
        header_layout.addWidget(delete_button)
        active_alarms_layout.addLayout(header_layout)
        
        # Create alarm list
        self.alarm_list = QListWidget()
        self.alarm_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.alarm_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.alarm_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.alarm_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                border-radius: 6px;
                padding: 8px;
                color: white;
            }
            QListWidget::item {
                background-color: rgba(50, 50, 60, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                margin: 4px 0;
                padding: 12px;
                font-size: 15px;
            }
            QListWidget::item:selected {
                background-color: rgba(33, 150, 243, 0.3);
                border: 1px solid #2196F3;
                color: white;
            }
            QListWidget::item:hover {
                background-color: rgba(60, 60, 70, 0.7);
                border: 1px solid rgba(33, 150, 243, 0.5);
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(255, 255, 255, 0.1);
                width: 8px;
                border-radius: 4px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.4);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        active_alarms_layout.addWidget(self.alarm_list)
        content_layout.addWidget(active_alarms_frame)
        
        # Add stretch to push everything to the top
        content_layout.addStretch()
        
        # Set the scroll content
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
    
    def add_alarm(self):
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
        for i in range(self.alarm_list.count()):
            item = self.alarm_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == alarm:
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
        """Delete the selected alarm."""
        # Get selected items
        selected_items = self.alarm_list.selectedItems()
        if not selected_items:
            return
        
        # Get the alarms
        alarms = [item.data(Qt.ItemDataRole.UserRole) for item in selected_items]
        
        # Confirm deletion
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the selected alarms?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            # Remove from list
            for alarm in alarms:
                self.alarm_list.takeItem(self.alarm_list.row(self.alarm_list.findItems(f"{alarm.time.toString('HH:mm')} - {alarm.label}", Qt.MatchExactly)[0]))
            
            # Emit signals
            for alarm in alarms:
                self.alarm_deleted.emit(alarm.id)
            
            logger.info(f"Deleted alarms: {', '.join([alarm.id for alarm in alarms])}")
    
    def _add_alarm_to_list(self, alarm):
        """
        Add an alarm to the list widget.
        
        Args:
            alarm (Alarm): Alarm to add
        """
        # Create list item
        item = QListWidgetItem()
        
        # Set text
        time_str = alarm.time.toString("HH:mm")
        label_str = f" - {alarm.label}" if alarm.label else ""
        enabled_str = "" if alarm.enabled else " (Disabled)"
        item.setText(f"{time_str}{label_str}{enabled_str}")
        
        # Set data
        item.setData(Qt.ItemDataRole.UserRole, alarm)
        
        # Add to list
        self.alarm_list.addItem(item)
    
    def update_alarms(self, alarms):
        """
        Update the alarms list.
        
        Args:
            alarms (list): List of Alarm objects
        """
        # Clear the list
        self.alarm_list.clear()
        
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
        for i in range(self.alarm_list.count()):
            item = self.alarm_list.item(i)
            alarm = item.data(Qt.ItemDataRole.UserRole)
            alarms.append(alarm)
        return alarms 