"""
Note Widget Module
-----------------
This module provides the NoteWidget class for managing notes in the Weather & Alarm application.
"""
import logging
import json
import os
import uuid
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QListWidget, QListWidgetItem, QMessageBox, QMenu,
    QInputDialog, QSplitter, QDialog, QDialogButtonBox, QFormLayout, QLineEdit,
    QFrame, QScrollArea, QComboBox, QAbstractItemView, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QAction, QFont, QColor

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

class Note:
    """Class representing a note."""
    
    def __init__(self, title="", content="", category="General", created=None, id=None):
        """
        Initialize a note.
        
        Args:
            title (str): Note title
            content (str): Note content
            category (str): Note category
            created (datetime, optional): Creation timestamp
            id (str, optional): Unique identifier
        """
        self.title = title
        self.content = content
        self.category = category
        self.created = created or datetime.now()
        self.id = id or f"{int(self.created.timestamp())}"
    
    def to_dict(self):
        """Convert note to dictionary for serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'created': self.created.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create note from dictionary."""
        return cls(
            title=data.get('title', ''),
            content=data.get('content', ''),
            category=data.get('category', 'General'),
            created=datetime.fromisoformat(data.get('created', datetime.now().isoformat())),
            id=data.get('id')
        )


class NoteDialog(QDialog):
    """Dialog for creating or editing a note."""
    
    def __init__(self, parent=None, note=None):
        """
        Initialize the note dialog.
        
        Args:
            parent (QWidget, optional): Parent widget
            note (Note, optional): Note to edit, or None for a new note
        """
        super().__init__(parent)
        self.note = note or Note()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Edit Note" if self.note.id else "New Note")
        self.setMinimumWidth(500)
        self.setStyleSheet("""
            QDialog {
                background-color: #2c2c2c;
                color: white;
            }
        """)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Create form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # Title field
        self.title_edit = QLineEdit(self.note.title)
        self.title_edit.setMinimumHeight(36)
        self.title_edit.setStyleSheet("""
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
        """)
        form_layout.addRow("Title:", self.title_edit)
        
        # Category selector with modern styling
        category_layout = QHBoxLayout()
        category_layout.setSpacing(16)
        
        category_label = QLabel("Category:")
        category_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9);
            font-size: 15px;
        """)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(["General", "Work", "Personal", "Shopping", "Ideas", "Other"])
        self.category_combo.setMinimumSize(QSize(150, 36))
        
        # Get the absolute path to the chevron-down.svg icon
        chevron_down_icon = get_icon_path("chevron-down.svg", None)
        
        self.category_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: rgba(50, 50, 60, 0.7);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 15px;
            }}
            QComboBox:focus {{
                background-color: rgba(60, 60, 70, 0.7);
                border: 1px solid #64B5F6;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox::down-arrow {{
                image: url({chevron_down_icon});
                width: 12px;
                height: 12px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #2c2c2c;
                color: white;
                selection-background-color: #64B5F6;
                selection-color: white;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
        """)
        
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_combo)
        category_layout.addStretch()
        
        form_layout.addLayout(category_layout)
        
        # Content field
        self.content_edit = QTextEdit(self.note.content)
        self.content_edit.setMinimumHeight(200)
        self.content_edit.setStyleSheet("""
            QTextEdit {
                background-color: rgba(50, 50, 60, 0.7);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 12px;
                font-size: 15px;
                selection-background-color: #64B5F6;
                selection-color: white;
            }
            QTextEdit:focus {
                background-color: rgba(60, 60, 70, 0.7);
                border: 1px solid #64B5F6;
            }
        """)
        form_layout.addRow("Content:", self.content_edit)
        
        layout.addLayout(form_layout)
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 15px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #42A5F5;
            }
            QPushButton:pressed {
                background-color: #1E88E5;
            }
            QPushButton[text="Cancel"] {
                background-color: rgba(50, 50, 60, 0.7);
            }
            QPushButton[text="Cancel"]:hover {
                background-color: rgba(60, 60, 70, 0.7);
            }
        """)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def accept(self):
        """Handle dialog acceptance."""
        # Update note with form values
        self.note.title = self.title_edit.text()
        self.note.content = self.content_edit.toPlainText()
        self.note.category = self.category_combo.currentText()
        
        # Validate
        if not self.note.title:
            QMessageBox.warning(self, "Validation Error", "Title cannot be empty.")
            return
        
        super().accept()
    
    def get_note(self):
        """Get the edited note."""
        return self.note


class NoteWidget(QWidget):
    """Widget for managing notes."""
    
    def __init__(self, parent=None):
        """
        Initialize the note widget.
        
        Args:
            parent (QWidget, optional): Parent widget
        """
        super().__init__(parent)
        self.notes = []
        self.notes_file = os.path.join(os.path.expanduser("~"), ".wacapp_notes.json")
        self.load_notes()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Get the absolute path to the chevron-down.svg icon
        chevron_down_icon = get_icon_path("chevron-down.svg", None)
        
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
        
        # Header with modern styling
        header_layout = QHBoxLayout()
        header_label = QLabel("My Notes")
        header_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #90CAF9;
            margin-bottom: 16px;
            padding-left: 4px;
        """)
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        content_layout.addLayout(header_layout)
        
        # Filter section with modern styling
        filter_frame = RoundedFrame(bg_color="rgba(40, 40, 50, 0.7)")
        filter_layout = QVBoxLayout(filter_frame)
        filter_layout.setSpacing(16)
        
        filter_label = QLabel("Filter:")
        filter_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9);
            font-size: 15px;
        """)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "General", "Work", "Personal", "Shopping", "Ideas", "Other"])
        self.filter_combo.setMinimumSize(QSize(150, 36))
        self.filter_combo.currentIndexChanged.connect(self.filter_notes)
        self.filter_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: rgba(50, 50, 60, 0.7);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 15px;
            }}
            QComboBox:focus {{
                background-color: rgba(60, 60, 70, 0.7);
                border: 1px solid #64B5F6;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox::down-arrow {{
                image: url({chevron_down_icon});
                width: 12px;
                height: 12px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #2c2c2c;
                color: white;
                selection-background-color: #64B5F6;
                selection-color: white;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
        """)
        
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addStretch()
        
        content_layout.addLayout(filter_layout)
        
        # Notes list with modern styling
        notes_frame = RoundedFrame(bg_color="rgba(40, 40, 50, 0.7)")
        notes_layout = QVBoxLayout(notes_frame)
        notes_layout.setSpacing(16)
        
        self.notes_list = QListWidget()
        self.notes_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.notes_list.setStyleSheet("""
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
        """)
        self.notes_list.itemDoubleClicked.connect(self.on_edit_note)
        notes_layout.addWidget(self.notes_list)
        
        # Buttons with modern styling
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)
        
        button_style = """
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 15px;
                font-weight: bold;
                min-width: 100px;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: #42A5F5;
            }
            QPushButton:pressed {
                background-color: #1E88E5;
            }
        """
        
        # Add note button
        add_button = QPushButton("New Note")
        add_button.clicked.connect(self.on_add_note)
        add_button.setStyleSheet(button_style)
        buttons_layout.addWidget(add_button)
        
        # Edit note button
        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(self.on_edit_note)
        edit_button.setStyleSheet(button_style.replace("#2196F3", "rgba(50, 50, 60, 0.7)"))
        buttons_layout.addWidget(edit_button)
        
        # Delete note button
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.on_delete_note)
        delete_button.setStyleSheet(button_style.replace("#2196F3", "#EF5350").replace("#42A5F5", "#E57373").replace("#1E88E5", "#F44336"))
        buttons_layout.addWidget(delete_button)
        
        # Add category button
        add_category_button = QPushButton("Add Category")
        add_category_button.clicked.connect(self.on_add_category)
        add_category_button.setStyleSheet(button_style.replace("#2196F3", "rgba(50, 50, 60, 0.7)"))
        buttons_layout.addWidget(add_category_button)
        
        notes_layout.addLayout(buttons_layout)
        content_layout.addWidget(notes_frame)
        
        # Set the content widget as the scroll area's widget
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
        # Populate notes list
        self.update_notes_list()
    
    def load_notes(self):
        """Load notes from file."""
        try:
            if os.path.exists(self.notes_file):
                with open(self.notes_file, 'r') as f:
                    notes_data = json.load(f)
                    self.notes = [Note.from_dict(note_data) for note_data in notes_data]
                    logger.info(f"Loaded {len(self.notes)} notes from {self.notes_file}")
            else:
                logger.info(f"Notes file {self.notes_file} does not exist, starting with empty notes")
        except Exception as e:
            logger.error(f"Error loading notes: {e}")
            QMessageBox.warning(
                self, 
                "Error Loading Notes", 
                f"Could not load notes from {self.notes_file}: {str(e)}"
            )
    
    def save_notes(self):
        """Save notes to file."""
        try:
            notes_data = [note.to_dict() for note in self.notes]
            with open(self.notes_file, 'w') as f:
                json.dump(notes_data, f, indent=2)
            logger.info(f"Saved {len(self.notes)} notes to {self.notes_file}")
        except Exception as e:
            logger.error(f"Error saving notes: {e}")
            QMessageBox.warning(
                self, 
                "Error Saving Notes", 
                f"Could not save notes to {self.notes_file}: {str(e)}"
            )
    
    def update_notes_list(self):
        """Update the notes list."""
        # Clear the list
        self.notes_list.clear()
        
        # Filter notes
        filtered_notes = self.filter_notes()
        
        # Add notes to the list
        for note in filtered_notes:
            # Create list item
            item = QListWidgetItem(note.title)
            
            # Set data
            item.setData(Qt.ItemDataRole.UserRole, note.id)
            
            # Add to list
            self.notes_list.addItem(item)
    
    def filter_notes(self):
        """Filter notes based on search text and category."""
        search_text = ""
        selected_category = self.filter_combo.currentText()
        
        filtered = []
        for note in self.notes:
            # Check if note matches search text
            text_match = (not search_text or 
                         search_text in note.title.lower() or 
                         search_text in note.content.lower())
            
            # Check if note matches category filter
            category_match = (selected_category == "All" or 
                             selected_category == note.category)
            
            if text_match and category_match:
                filtered.append(note)
        
        return filtered
    
    def get_selected_note(self):
        """
        Get the selected note.
        
        Returns:
            Note: Selected note or None if no note is selected
        """
        # Get selected items
        selected_items = self.notes_list.selectedItems()
        if not selected_items:
            return None
        
        # Get note ID
        note_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        # Find note by ID
        for note in self.notes:
            if note.id == note_id:
                return note
        
        return None
    
    def on_add_note(self):
        """Add a new note."""
        # Create dialog
        dialog = NoteDialog(self)
        
        # Show dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Get note
            note = dialog.get_note()
            
            # Add note to list
            self.notes.append(note)
            
            # Save notes
            self.save_notes()
            
            # Update notes list
            self.update_notes_list()
    
    def on_edit_note(self):
        """Edit the selected note."""
        # Get selected note
        note = self.get_selected_note()
        if not note:
            return
        
        # Create dialog
        dialog = NoteDialog(self, note)
        
        # Show dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Get updated note
            updated_note = dialog.get_note()
            
            # Update note in list
            for i, n in enumerate(self.notes):
                if n.id == note.id:
                    self.notes[i] = updated_note
                    break
            
            # Save notes
            self.save_notes()
            
            # Update notes list
            self.update_notes_list()
    
    def on_delete_note(self):
        """Delete the selected note."""
        # Get selected note
        note = self.get_selected_note()
        if not note:
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the note '{note.title}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove note from list
            self.notes = [n for n in self.notes if n.id != note.id]
            
            # Save notes
            self.save_notes()
            
            # Update notes list
            self.update_notes_list()
    
    def on_add_category(self):
        """Handle adding a new category."""
        category, ok = QInputDialog.getText(
            self,
            "Add Category",
            "Enter new category name:"
        )
        
        if ok and category:
            # Add the category to the filter
            if self.filter_combo.findText(category) == -1:
                self.filter_combo.addItem(category)
                self.filter_combo.setCurrentText(category)
                logger.info(f"Added new category: {category}") 