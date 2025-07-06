"""
Notification Widget Module
------------------
This module provides the NotificationWidget class for displaying and managing notifications in the Weather & Alarm application.
"""
import logging
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QScrollArea, QListWidget, QListWidgetItem, QMenu,
    QTabWidget, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QColor, QAction, QPalette

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

class NotificationItem(RoundedFrame):
    """Widget for displaying a notification item."""
    
    # Signal emitted when the notification is clicked
    clicked = pyqtSignal(object)
    
    # Signal emitted when the notification is marked as read
    marked_as_read = pyqtSignal(object)
    
    # Signal emitted when the notification is removed
    removed = pyqtSignal(object)
    
    def __init__(self, notification, parent=None):
        """
        Initialize the notification item.
        
        Args:
            notification (Notification): Notification object
            parent (QWidget, optional): Parent widget
        """
        super().__init__(parent, bg_color="rgba(40, 40, 50, 0.7)")
        
        # Store notification
        self.notification = notification
        
        # Initialize UI
        self.init_ui()
        
        # Update read status
        self.update_read_status()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(8)
        
        # Header layout
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        # Title label
        self.title_label = QLabel(self.notification.title)
        self.title_label.setStyleSheet("""
            font-weight: bold;
            font-size: 16px;
            color: white;
        """)
        header_layout.addWidget(self.title_label)
        
        # Spacer
        header_layout.addStretch()
        
        # Time label
        time_str = self.notification.timestamp.strftime("%H:%M")
        self.time_label = QLabel(time_str)
        self.time_label.setStyleSheet("""
            font-size: 13px;
            color: rgba(255, 255, 255, 0.7);
        """)
        header_layout.addWidget(self.time_label)
        
        main_layout.addLayout(header_layout)
        
        # Message label
        self.message_label = QLabel(self.notification.message)
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet("""
            font-size: 14px;
            color: rgba(255, 255, 255, 0.9);
            margin: 4px 0;
        """)
        main_layout.addWidget(self.message_label)
        
        # Footer layout
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(12)
        
        # Category label
        category_str = self.notification.category.capitalize()
        self.category_label = QLabel(category_str)
        self.category_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.6);
            font-size: 13px;
        """)
        footer_layout.addWidget(self.category_label)
        
        # Spacer
        footer_layout.addStretch()
        
        button_style = """
            QPushButton {
                background-color: rgba(50, 50, 60, 0.7);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 6px 16px;
                font-size: 13px;
                min-width: 80px;
                min-height: 28px;
            }
            QPushButton:hover {
                background-color: rgba(60, 60, 70, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            QPushButton:pressed {
                background-color: rgba(45, 45, 55, 0.7);
            }
            QPushButton:disabled {
                background-color: rgba(40, 40, 50, 0.4);
                color: rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.05);
            }
        """
        
        # Mark as read button
        self.read_button = QPushButton("Mark as Read")
        self.read_button.setStyleSheet(button_style)
        self.read_button.clicked.connect(self.on_mark_as_read)
        footer_layout.addWidget(self.read_button)
        
        # Remove button
        self.remove_button = QPushButton("Remove")
        self.remove_button.setStyleSheet(button_style.replace(
            "rgba(50, 50, 60, 0.7)",
            "#EF5350"
        ).replace(
            "rgba(60, 60, 70, 0.7)",
            "#E57373"
        ).replace(
            "rgba(45, 45, 55, 0.7)",
            "#F44336"
        ))
        self.remove_button.clicked.connect(self.on_remove)
        footer_layout.addWidget(self.remove_button)
        
        main_layout.addLayout(footer_layout)
        
        # Connect signals
        self.mousePressEvent = self.on_click
    
    def update_read_status(self):
        """Update the read status of the notification."""
        if self.notification.read:
            self.read_button.setText("Read")
            self.read_button.setEnabled(False)
            self.setStyleSheet("""
                QFrame {
                    background-color: rgba(35, 35, 40, 0.4);
                    border-radius: 10px;
                    padding: 16px;
                    border: 1px solid rgba(255, 255, 255, 0.05);
                    margin: 2px;
                }
                QFrame:hover {
                    background-color: rgba(40, 40, 45, 0.4);
                }
            """)
        else:
            self.read_button.setText("Mark as Read")
            self.read_button.setEnabled(True)
            self.setStyleSheet("""
                QFrame {
                    background-color: rgba(40, 40, 50, 0.7);
                    border-radius: 10px;
                    padding: 16px;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    margin: 2px;
                }
                QFrame:hover {
                    background-color: rgba(45, 45, 55, 0.7);
                    border: 1px solid rgba(255, 255, 255, 0.15);
                }
            """)
    
    def on_click(self, event):
        """
        Handle click event.
        
        Args:
            event (QMouseEvent): Mouse event
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.notification)
            super().mousePressEvent(event)
    
    def on_mark_as_read(self):
        """Handle mark as read button click."""
        self.notification.mark_as_read()
        self.update_read_status()
        self.marked_as_read.emit(self.notification)
    
    def on_remove(self):
        """Handle remove button click."""
        self.removed.emit(self.notification)

class NotificationWidget(QWidget):
    """Widget for displaying and managing notifications."""
    
    # Signal emitted when a notification is clicked
    notification_clicked = pyqtSignal(object)
    
    # Signal emitted when a notification is marked as read
    notification_marked_as_read = pyqtSignal(object)
    
    # Signal emitted when a notification is removed
    notification_removed = pyqtSignal(object)
    
    def __init__(self, notification_manager=None, parent=None):
        """
        Initialize the notification widget.
        
        Args:
            notification_manager (NotificationManager, optional): Notification manager
            parent (QWidget, optional): Parent widget
        """
        super().__init__(parent)
        
        # Store notification manager
        self.notification_manager = notification_manager
        
        # Initialize UI
        self.init_ui()
        
        # Connect signals if manager is provided
        if notification_manager:
            try:
                notification_manager.notification_added.connect(self.on_notification_added)
                notification_manager.notification_removed.connect(self.on_notification_removed)
                notification_manager.notifications_updated.connect(self.update_notifications)
                
                # Initialize with existing notifications
                self.update_notifications(notification_manager.get_notifications())
            except Exception as e:
                logger.error(f"Error connecting notification signals: {str(e)}")
    
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
        title_label = QLabel("Notifications")
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #90CAF9;
            margin-bottom: 16px;
            padding-left: 4px;
        """)
        content_layout.addWidget(title_label)
        
        # Add tab widget with modern styling
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: rgba(40, 40, 50, 0.7);
                color: rgba(255, 255, 255, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                min-width: 100px;
            }
            QTabBar::tab:selected {
                background: rgba(50, 50, 60, 0.7);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-bottom: none;
            }
            QTabBar::tab:hover:!selected {
                background: rgba(45, 45, 55, 0.7);
                color: rgba(255, 255, 255, 0.8);
            }
        """)
        
        # Create all notifications tab
        self.all_tab = QWidget()
        all_layout = QVBoxLayout(self.all_tab)
        all_layout.setContentsMargins(0, 16, 0, 0)
        all_layout.setSpacing(8)
        
        # Create scroll area for all notifications
        all_scroll = QScrollArea()
        all_scroll.setWidgetResizable(True)
        all_scroll.setFrameShape(QFrame.Shape.NoFrame)
        all_scroll.setStyleSheet("""
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
        
        # Create widget to hold all notifications
        self.all_notifications_widget = QWidget()
        self.all_notifications_layout = QVBoxLayout(self.all_notifications_widget)
        self.all_notifications_layout.setContentsMargins(0, 0, 0, 0)
        self.all_notifications_layout.setSpacing(12)
        self.all_notifications_layout.addStretch()
        
        all_scroll.setWidget(self.all_notifications_widget)
        all_layout.addWidget(all_scroll)
        
        # Create unread notifications tab
        self.unread_tab = QWidget()
        unread_layout = QVBoxLayout(self.unread_tab)
        unread_layout.setContentsMargins(0, 16, 0, 0)
        unread_layout.setSpacing(8)
        
        # Create scroll area for unread notifications
        unread_scroll = QScrollArea()
        unread_scroll.setWidgetResizable(True)
        unread_scroll.setFrameShape(QFrame.Shape.NoFrame)
        unread_scroll.setStyleSheet(all_scroll.styleSheet())
        
        # Create widget to hold unread notifications
        self.unread_notifications_widget = QWidget()
        self.unread_notifications_layout = QVBoxLayout(self.unread_notifications_widget)
        self.unread_notifications_layout.setContentsMargins(0, 0, 0, 0)
        self.unread_notifications_layout.setSpacing(12)
        self.unread_notifications_layout.addStretch()
        
        unread_scroll.setWidget(self.unread_notifications_widget)
        unread_layout.addWidget(unread_scroll)
        
        # Add tabs
        self.tab_widget.addTab(self.all_tab, "All")
        self.tab_widget.addTab(self.unread_tab, "Unread")
        
        # Add buttons with modern styling
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)
        
        button_style = """
            QPushButton {
                background-color: rgba(50, 50, 60, 0.7);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: rgba(60, 60, 70, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            QPushButton:pressed {
                background-color: rgba(45, 45, 55, 0.7);
            }
        """
        
        # Mark all as read button
        mark_all_button = QPushButton("Mark All as Read")
        mark_all_button.clicked.connect(self.on_mark_all_as_read)
        mark_all_button.setStyleSheet(button_style)
        buttons_layout.addWidget(mark_all_button)
        
        # Clear all button
        clear_all_button = QPushButton("Clear All")
        clear_all_button.clicked.connect(self.on_clear_all)
        clear_all_button.setStyleSheet(button_style.replace(
            "rgba(50, 50, 60, 0.7)",
            "#EF5350"
        ).replace(
            "rgba(60, 60, 70, 0.7)",
            "#E57373"
        ).replace(
            "rgba(45, 45, 55, 0.7)",
            "#F44336"
        ))
        buttons_layout.addWidget(clear_all_button)
        
        buttons_layout.addStretch()
        
        # Add widgets to main layout
        content_layout.addWidget(self.tab_widget)
        content_layout.addLayout(buttons_layout)
        
        # Set the content widget as the scroll area's widget
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
        # Store notification items
        self.notification_items = {}
        
        # Add a placeholder message when there are no notifications
        self.no_notifications_label = QLabel("No notifications to display")
        self.no_notifications_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_notifications_label.setStyleSheet("color: #888; margin: 20px;")
        self.all_notifications_layout.insertWidget(0, self.no_notifications_label)
    
    def set_notification_manager(self, notification_manager):
        """
        Set the notification manager.
        
        Args:
            notification_manager (NotificationManager): Notification manager
        """
        self.notification_manager = notification_manager
        
        try:
            # Connect signals
            notification_manager.notification_added.connect(self.on_notification_added)
            notification_manager.notification_removed.connect(self.on_notification_removed)
            notification_manager.notifications_updated.connect(self.update_notifications)
            
            # Update notifications
            self.update_notifications(notification_manager.get_notifications())
        except Exception as e:
            logger.error(f"Error connecting notification signals: {str(e)}")
    
    def update_notifications(self, notifications=None):
        """
        Update the notifications display.
        
        Args:
            notifications (list, optional): List of notifications
        """
        try:
            # Clear existing notifications
            self.clear_notification_layouts()
            
            # Get notifications if not provided
            if notifications is None and self.notification_manager:
                notifications = self.notification_manager.get_notifications()
            
            if not notifications or len(notifications) == 0:
                # Show the placeholder message
                self.no_notifications_label.setVisible(True)
                self.tab_widget.setTabText(1, "Unread (0)")
                return
            
            # Hide the placeholder message
            self.no_notifications_label.setVisible(False)
            
            # Add notifications
            for notification in notifications:
                self.add_notification_item(notification)
            
            # Update unread count
            unread_count = sum(1 for n in notifications if not n.read)
            self.tab_widget.setTabText(1, f"Unread ({unread_count})")
        except Exception as e:
            logger.error(f"Error updating notifications: {str(e)}")
    
    def clear_notification_layouts(self):
        """Clear notification layouts."""
        try:
            # Clear all notifications layout
            while self.all_notifications_layout.count() > 1:
                item = self.all_notifications_layout.takeAt(0)
                if item.widget() and item.widget() != self.no_notifications_label:
                    item.widget().deleteLater()
            
            # Clear unread notifications layout
            while self.unread_notifications_layout.count() > 1:
                item = self.unread_notifications_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # Clear notification items
            self.notification_items = {}
        except Exception as e:
            logger.error(f"Error clearing notification layouts: {str(e)}")
    
    def add_notification_item(self, notification):
        """
        Add a notification item.
        
        Args:
            notification (Notification): Notification to add
        """
        try:
            # Create notification item
            item = NotificationItem(notification)
            
            # Connect signals
            item.clicked.connect(self.on_notification_clicked)
            item.marked_as_read.connect(self.on_notification_marked_as_read)
            item.removed.connect(self.on_notification_removed)
            
            # Store item
            self.notification_items[notification.id] = item
            
            # Add to all notifications layout
            self.all_notifications_layout.insertWidget(0, item)
            
            # Add to unread notifications layout if unread
            if not notification.read:
                self.unread_notifications_layout.insertWidget(0, item)
        except Exception as e:
            logger.error(f"Error adding notification item: {str(e)}")
    
    def on_notification_added(self, notification):
        """
        Handle notification added event.
        
        Args:
            notification (Notification): Added notification
        """
        try:
            # Hide the placeholder message
            self.no_notifications_label.setVisible(False)
            
            # Add the notification item
            self.add_notification_item(notification)
            
            # Update unread count
            if self.notification_manager:
                unread_count = len(self.notification_manager.get_notifications(unread_only=True))
                self.tab_widget.setTabText(1, f"Unread ({unread_count})")
        except Exception as e:
            logger.error(f"Error handling notification added: {str(e)}")
    
    def on_notification_clicked(self, notification):
        """
        Handle notification clicked event.
        
        Args:
            notification (Notification): Clicked notification
        """
        try:
            self.notification_clicked.emit(notification)
        except Exception as e:
            logger.error(f"Error handling notification clicked: {str(e)}")
    
    def on_notification_marked_as_read(self, notification):
        """
        Handle notification marked as read event.
        
        Args:
            notification (Notification): Marked notification
        """
        try:
            # Remove from unread layout
            item = self.notification_items.get(notification.id)
            if item:
                for i in range(self.unread_notifications_layout.count()):
                    widget = self.unread_notifications_layout.itemAt(i).widget()
                    if widget == item:
                        self.unread_notifications_layout.removeWidget(widget)
                        break
            
            # Update unread count
            if self.notification_manager:
                unread_count = len(self.notification_manager.get_notifications(unread_only=True))
                self.tab_widget.setTabText(1, f"Unread ({unread_count})")
            
            # Emit signal
            self.notification_marked_as_read.emit(notification)
        except Exception as e:
            logger.error(f"Error handling notification marked as read: {str(e)}")
    
    def on_notification_removed(self, notification):
        """
        Handle notification removed event.
        
        Args:
            notification (Notification): Removed notification or notification ID
        """
        try:
            # Get notification ID
            notification_id = notification.id if hasattr(notification, 'id') else notification
            
            # Get item
            item = self.notification_items.get(notification_id)
            if not item:
                return
            
            # Remove from layouts
            for layout in [self.all_notifications_layout, self.unread_notifications_layout]:
                for i in range(layout.count()):
                    widget = layout.itemAt(i).widget()
                    if widget == item:
                        layout.removeWidget(widget)
                        widget.deleteLater()
                        break
            
            # Remove from items
            del self.notification_items[notification_id]
            
            # Update unread count
            if self.notification_manager:
                unread_count = len(self.notification_manager.get_notifications(unread_only=True))
                self.tab_widget.setTabText(1, f"Unread ({unread_count})")
            
            # Show placeholder if no notifications
            if len(self.notification_items) == 0:
                self.no_notifications_label.setVisible(True)
            
            # Emit signal if notification object
            if hasattr(notification, 'id'):
                self.notification_removed.emit(notification)
        except Exception as e:
            logger.error(f"Error handling notification removed: {str(e)}")
    
    def on_mark_all_as_read(self):
        """Handle mark all as read button click."""
        try:
            if not self.notification_manager:
                return
            
            # Mark all as read
            self.notification_manager.mark_all_as_read()
            
            # Update unread count
            self.tab_widget.setTabText(1, "Unread (0)")
            
            # Clear unread layout
            while self.unread_notifications_layout.count() > 1:
                item = self.unread_notifications_layout.takeAt(0)
                if item.widget():
                    self.unread_notifications_layout.removeWidget(item.widget())
            
            # Update read status of all items
            for item in self.notification_items.values():
                item.update_read_status()
        except Exception as e:
            logger.error(f"Error marking all notifications as read: {str(e)}")
    
    def on_clear_all(self):
        """Handle clear all button click."""
        try:
            if not self.notification_manager:
                return
            
            # Clear all notifications
            self.notification_manager.clear_notifications()
            
            # Clear layouts
            self.clear_notification_layouts()
            
            # Update unread count
            self.tab_widget.setTabText(1, "Unread (0)")
            
            # Show placeholder
            self.no_notifications_label.setVisible(True)
        except Exception as e:
            logger.error(f"Error clearing all notifications: {str(e)}") 