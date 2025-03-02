"""
Note Widget Module
-----------------
This module provides the NoteWidget class for managing notes in the Weather & Alarm application.
"""
import logging
import json
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QListWidget, QListWidgetItem, QMessageBox, 
    QScrollArea, QFrame, QLineEdit, QComboBox, QDialog,
    QDialogButtonBox, QFormLayout, QInputDialog
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

# Configure logging
logger = logging.getLogger(__name__)

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
        self.setMinimumWidth(400)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create form layout
        form_layout = QFormLayout()
        
        # Title field
        self.title_edit = QLineEdit(self.note.title)
        form_layout.addRow("Title:", self.title_edit)
        
        # Category field
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.addItems(["General", "Work", "Personal", "Ideas", "To-Do"])
        self.category_combo.setCurrentText(self.note.category)
        form_layout.addRow("Category:", self.category_combo)
        
        # Content field
        self.content_edit = QTextEdit(self.note.content)
        form_layout.addRow("Content:", self.content_edit)
        
        layout.addLayout(form_layout)
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
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
        
        # Create a scroll area for the content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Create a widget to hold the scrollable content
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("My Notes")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        content_layout.addLayout(header_layout)
        
        # Filter section
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter:"))
        
        # Search box
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search notes...")
        self.search_edit.textChanged.connect(self.filter_notes)
        filter_layout.addWidget(self.search_edit)
        
        # Category filter
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        self.update_categories()
        self.category_filter.currentTextChanged.connect(self.filter_notes)
        filter_layout.addWidget(self.category_filter)
        
        content_layout.addLayout(filter_layout)
        
        # Notes list
        self.notes_list = QListWidget()
        self.notes_list.setSelectionMode(QListWidget.SingleSelection)
        self.notes_list.itemDoubleClicked.connect(self.on_edit_note)
        content_layout.addWidget(self.notes_list)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        # Add note button
        add_button = QPushButton("New Note")
        add_button.clicked.connect(self.on_add_note)
        buttons_layout.addWidget(add_button)
        
        # Edit note button
        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(self.on_edit_note)
        buttons_layout.addWidget(edit_button)
        
        # Delete note button
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.on_delete_note)
        buttons_layout.addWidget(delete_button)
        
        # Add category button
        add_category_button = QPushButton("Add Category")
        add_category_button.clicked.connect(self.on_add_category)
        buttons_layout.addWidget(add_category_button)
        
        content_layout.addLayout(buttons_layout)
        
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
        """Update the notes list widget with current notes."""
        self.notes_list.clear()
        
        # Get filter values
        search_text = self.search_edit.text().lower()
        category = self.category_filter.currentText()
        if category == "All Categories":
            category = None
        
        # Filter and sort notes
        filtered_notes = self.notes
        if search_text:
            filtered_notes = [
                note for note in filtered_notes 
                if search_text in note.title.lower() or search_text in note.content.lower()
            ]
        if category:
            filtered_notes = [note for note in filtered_notes if note.category == category]
        
        # Sort by creation date (newest first)
        filtered_notes = sorted(filtered_notes, key=lambda note: note.created, reverse=True)
        
        # Add to list widget
        for note in filtered_notes:
            item = QListWidgetItem(f"{note.title} ({note.category})")
            item.setData(Qt.UserRole, note.id)
            self.notes_list.addItem(item)
    
    def update_categories(self):
        """Update the category filter with current categories."""
        current_text = self.category_filter.currentText()
        
        # Get unique categories
        categories = sorted(set(note.category for note in self.notes))
        
        # Update combobox
        self.category_filter.clear()
        self.category_filter.addItem("All Categories")
        self.category_filter.addItems(categories)
        
        # Restore selection if possible
        index = self.category_filter.findText(current_text)
        if index >= 0:
            self.category_filter.setCurrentIndex(index)
    
    def filter_notes(self):
        """Filter notes based on search text and category."""
        self.update_notes_list()
    
    def get_selected_note(self):
        """Get the currently selected note."""
        selected_items = self.notes_list.selectedItems()
        if not selected_items:
            return None
        
        note_id = selected_items[0].data(Qt.UserRole)
        for note in self.notes:
            if note.id == note_id:
                return note
        
        return None
    
    def on_add_note(self):
        """Handle adding a new note."""
        dialog = NoteDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            new_note = dialog.get_note()
            self.notes.append(new_note)
            self.save_notes()
            self.update_categories()
            self.update_notes_list()
            logger.info(f"Added new note: {new_note.title}")
    
    def on_edit_note(self):
        """Handle editing a note."""
        note = self.get_selected_note()
        if not note:
            QMessageBox.information(self, "No Selection", "Please select a note to edit.")
            return
        
        dialog = NoteDialog(self, note)
        if dialog.exec_() == QDialog.Accepted:
            self.save_notes()
            self.update_categories()
            self.update_notes_list()
            logger.info(f"Edited note: {note.title}")
    
    def on_delete_note(self):
        """Handle deleting a note."""
        note = self.get_selected_note()
        if not note:
            QMessageBox.information(self, "No Selection", "Please select a note to delete.")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the note '{note.title}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.notes.remove(note)
            self.save_notes()
            self.update_categories()
            self.update_notes_list()
            logger.info(f"Deleted note: {note.title}")
    
    def on_add_category(self):
        """Handle adding a new category."""
        category, ok = QInputDialog.getText(
            self,
            "Add Category",
            "Enter new category name:"
        )
        
        if ok and category:
            # Add the category to the filter
            if self.category_filter.findText(category) == -1:
                self.category_filter.addItem(category)
                self.category_filter.setCurrentText(category)
                logger.info(f"Added new category: {category}") 