import sys
import os
from datetime import datetime
from django.utils import timezone

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beyond_hunger.settings')
import django
django.setup()

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel, QLineEdit, QDialog,
    QFormLayout, QMessageBox, QDateTimeEdit, QGroupBox, QDialogButtonBox,
    QComboBox, QListWidget, QListWidgetItem, QRadioButton, QHeaderView, QFrame,
    QSplitter, QGridLayout, QScrollArea
)
from PyQt6.QtCore import Qt, QDateTime, QDate, QTime, QSize, QTimer
from PyQt6.QtGui import QPalette, QColor, QBrush, QIcon, QFont, QLinearGradient, QPixmap

# Import Django models
from food_donation.models import FoodDonation, DeliveryAssignment, Volunteer, UserProfile
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth


class StatCard(QFrame):
    """A custom widget for displaying statistics in a card format"""
    def __init__(self, title, value, subtitle=None, icon=None, color="#388e3c"):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"""
            StatCard {{
                background-color: {color};
                color: white;
                border-radius: 10px;
                padding: 15px;
                min-height: 120px;
                border: 1px solid #555555;
            }}
        """)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        # Value
        value_label = QLabel(str(value))
        value_label.setStyleSheet("font-size: 32px; font-weight: bold; margin-top: 10px;")
        
        # Add to layout
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        # Optional subtitle
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("font-size: 12px;")
            layout.addWidget(subtitle_label)
            
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)


class StatusUpdateDialog(QDialog):
    """Dialog for updating status of donations or assignments"""
    def __init__(self, parent=None, item=None, status_choices=None, item_type="donation"):
        super().__init__(parent)
        self.item = item
        self.item_type = item_type
        self.setWindowTitle(f"Update {item_type.capitalize()} Status")
        self.setMinimumWidth(400)
        
        # Apply dark theme to dialog
        self.setStyleSheet("""
            QDialog {
                background-color: #121212;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QGroupBox {
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 1ex;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QComboBox {
                background-color: #333333;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton {
                background-color: #388e3c;
                color: white;
                border-radius: 3px;
                padding: 8px 15px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2d7d32;
            }
            QPushButton:pressed {
                background-color: #1b5e20;
            }
        """)
        
        # Set up the layout
        layout = QVBoxLayout()
        
        # Item details group
        details_group = QGroupBox("Details")
        details_layout = QFormLayout()
        
        if item_type == "donation":
            details_layout.addRow("ID:", QLabel(str(item.id)))
            details_layout.addRow("Donor:", QLabel(item.donor.username))
            details_layout.addRow("Food Type:", QLabel(item.food_type))
            details_layout.addRow("Quantity:", QLabel(item.quantity))
            details_layout.addRow("Current Status:", QLabel(item.get_status_display()))
        else:  # assignment
            details_layout.addRow("ID:", QLabel(str(item.id)))
            details_layout.addRow("Donation:", QLabel(f"{item.donation.food_type} (ID: {item.donation.id})"))
            details_layout.addRow("Volunteer:", QLabel(item.volunteer.user.username))
            details_layout.addRow("Current Status:", QLabel(item.get_status_display()))
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        # Status update group
        status_group = QGroupBox("Update Status")
        status_layout = QFormLayout()
        
        self.status_combo = QComboBox()
        for value, display in status_choices:
            self.status_combo.addItem(display, value)
            if item_type == "donation" and value == item.status:
                self.status_combo.setCurrentText(display)
            elif item_type == "assignment" and value == item.status:
                self.status_combo.setCurrentText(display)
        
        status_layout.addRow("New Status:", self.status_combo)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                           QDialogButtonBox.StandardButton.Cancel)
        
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        
        self.setLayout(layout)
    
    def get_selected_status(self):
        return self.status_combo.currentData()


class AssignDeliveryDialog(QDialog):
    """Dialog for assigning a volunteer to a donation"""
    def __init__(self, parent=None, donation=None):
        super().__init__(parent)
        self.donation = donation
        self.selected_volunteer = None
        self.manual_name = None  # For manually entered name
        self.setWindowTitle("Assign Delivery Partner")
        self.setMinimumWidth(500)
        
        # Apply dark theme to dialog
        self.setStyleSheet("""
            QDialog {
                background-color: #121212;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QGroupBox {
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 1ex;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QComboBox, QLineEdit, QDateTimeEdit {
                background-color: #333333;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton {
                background-color: #388e3c;
                color: white;
                border-radius: 3px;
                padding: 8px 15px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2d7d32;
            }
            QPushButton:pressed {
                background-color: #1b5e20;
            }
            QListWidget {
                background-color: #1e1e1e;
                alternate-background-color: #262626;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #333333;
            }
            QListWidget::item:selected {
                background-color: #2d7d32;
                color: white;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                border-radius: 5px;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #cccccc;
                padding: 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #388e3c;
                color: white;
                font-weight: bold;
            }
            QTabBar::tab:hover:!selected {
                background-color: #3d3d3d;
            }
        """)
        
        # Set up the layout
        layout = QVBoxLayout()
        
        # Donation details group
        donation_group = QGroupBox("Donation Details")
        donation_layout = QFormLayout()
        
        donation_layout.addRow("ID:", QLabel(str(donation.id)))
        donation_layout.addRow("Donor:", QLabel(donation.donor.username))
        donation_layout.addRow("Food Type:", QLabel(donation.food_type))
        donation_layout.addRow("Quantity:", QLabel(donation.quantity))
        donation_layout.addRow("Pickup Address:", QLabel(donation.pickup_address))
        donation_layout.addRow("Status:", QLabel(donation.get_status_display()))
        
        donation_group.setLayout(donation_layout)
        layout.addWidget(donation_group)
        
        # Create tab widget for selection methods
        tab_widget = QTabWidget()
        
        # Tab 1: DB Selection
        db_selection_tab = QWidget()
        db_selection_layout = QVBoxLayout(db_selection_tab)
        
        # Volunteer search group
        volunteer_group = QGroupBox("Search Volunteer From Database")
        volunteer_layout = QVBoxLayout()
        
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter volunteer name from database...")
        self.search_input.textChanged.connect(self.search_volunteers)
        
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_volunteers)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        
        volunteer_layout.addLayout(search_layout)
        
        # Volunteer list
        self.volunteer_list = QListWidget()
        self.volunteer_list.itemClicked.connect(self.select_volunteer)
        volunteer_layout.addWidget(self.volunteer_list)
        
        volunteer_group.setLayout(volunteer_layout)
        db_selection_layout.addWidget(volunteer_group)
        
        # Tab 2: Manual Entry
        manual_entry_tab = QWidget()
        manual_entry_layout = QVBoxLayout(manual_entry_tab)
        
        manual_group = QGroupBox("Enter Volunteer Name Manually")
        manual_form = QFormLayout()
        
        self.manual_name_input = QLineEdit()
        self.manual_name_input.setPlaceholderText("Enter delivery partner name...")
        self.manual_name_input.textChanged.connect(self.update_manual_name)
        
        self.manual_phone_input = QLineEdit()
        self.manual_phone_input.setPlaceholderText("Enter phone number (optional)...")
        
        manual_form.addRow("Name:", self.manual_name_input)
        manual_form.addRow("Phone:", self.manual_phone_input)
        
        manual_group.setLayout(manual_form)
        manual_entry_layout.addWidget(manual_group)
        manual_entry_layout.addStretch()
        
        # Add tabs to widget
        tab_widget.addTab(db_selection_tab, "Select From Database")
        tab_widget.addTab(manual_entry_tab, "Manual Entry")
        
        layout.addWidget(tab_widget)
        
        # Assignment details group
        assignment_group = QGroupBox("Assignment Details")
        assignment_layout = QFormLayout()
        
        # Pickup time
        self.pickup_time = QDateTimeEdit()
        self.pickup_time.setDateTime(QDateTime.currentDateTime().addSecs(3600))  # Default 1 hour from now
        self.pickup_time.setCalendarPopup(True)
        assignment_layout.addRow("Pickup Time:", self.pickup_time)
        
        # Notes
        self.notes = QLineEdit()
        self.notes.setPlaceholderText("Optional notes...")
        assignment_layout.addRow("Notes:", self.notes)
        
        assignment_group.setLayout(assignment_layout)
        layout.addWidget(assignment_group)
        
        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                           QDialogButtonBox.StandardButton.Cancel)
        
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)  # Disable until volunteer selected or name entered
        layout.addWidget(self.button_box)
        
        self.setLayout(layout)
        
        # Connect tab change signals
        tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # Store reference to tabs
        self.tab_widget = tab_widget
        
        # Populate volunteers initially
        self.search_volunteers()
    
    def on_tab_changed(self, index):
        """Handle tab changes"""
        if index == 0:  # Database selection
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(self.selected_volunteer is not None)
        else:  # Manual entry
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(bool(self.manual_name))
    
    def update_manual_name(self, text):
        """Update manual name and enable/disable OK button"""
        self.manual_name = text.strip() if text.strip() else None
        
        # Only enable OK if on manual tab and name is not empty
        if self.tab_widget.currentIndex() == 1:  # Manual entry tab
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(bool(self.manual_name))
    
    def search_volunteers(self):
        """Search for volunteers by name"""
        search_text = self.search_input.text().lower()
        self.volunteer_list.clear()
        
        # Get all volunteers that are available
        volunteers = Volunteer.objects.filter(availability=True)
        
        # Filter by name if search text is provided
        filtered_volunteers = []
        for volunteer in volunteers:
            username = volunteer.user.username.lower()
            first_name = volunteer.user.first_name.lower()
            last_name = volunteer.user.last_name.lower()
            
            if (search_text in username or 
                search_text in first_name or 
                search_text in last_name or
                not search_text):  # Show all if no search text
                filtered_volunteers.append(volunteer)
        
        # Add to list widget
        for volunteer in filtered_volunteers:
            user = volunteer.user
            name = f"{user.first_name} {user.last_name}" if user.first_name and user.last_name else user.username
            item = QListWidgetItem(f"{name} ({user.username})")
            item.setData(Qt.ItemDataRole.UserRole, volunteer.id)
            self.volunteer_list.addItem(item)
    
    def select_volunteer(self, item):
        """Handle volunteer selection"""
        volunteer_id = item.data(Qt.ItemDataRole.UserRole)
        self.selected_volunteer = Volunteer.objects.get(id=volunteer_id)
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
    
    def get_pickup_time(self):
        """Get the selected pickup time"""
        try:
            # Use the proper method based on PyQt version
            if hasattr(self.pickup_time.dateTime(), 'toPyDateTime'):
                return self.pickup_time.dateTime().toPyDateTime()
            elif hasattr(self.pickup_time.dateTime(), 'toPython'):
                return self.pickup_time.dateTime().toPython()
            else:
                # Manual conversion as fallback
                from datetime import datetime
                date = self.pickup_time.date()
                time = self.pickup_time.time()
                return datetime(
                    date.year(), date.month(), date.day(),
                    time.hour(), time.minute(), time.second()
                )
        except Exception as e:
            # If all else fails, return current datetime
            from django.utils import timezone
            print(f"Error getting pickup time: {e}")
            return timezone.now()
    
    def get_notes(self):
        """Get assignment notes"""
        return self.notes.text()
    
    def get_manual_phone(self):
        """Get manually entered phone number"""
        return self.manual_phone_input.text()


class FounderCard(QFrame):
    """A custom widget for displaying founder information"""
    def __init__(self, name, role, photo_path, quote):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            FounderCard {
                background-color: #1e1e1e;
                color: white;
                border-radius: 10px;
                padding: 15px;
                min-height: 300px;
                min-width: 300px;
                border: 1px solid #555555;
                margin: 10px;
            }
            FounderCard:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 20px rgba(0,0,0,0.4);
                transition: all 0.3s ease;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Photo
        photo_label = QLabel()
        try:
            # Try to load the photo from the path
            pixmap = QPixmap(photo_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                photo_label.setPixmap(pixmap)
                photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            else:
                # If photo can't be loaded, create an avatar with initials
                photo_label.setText(name[0])
                photo_label.setStyleSheet("""
                    background-color: #388e3c; 
                    color: white; 
                    font-size: 72px; 
                    font-weight: bold;
                    border-radius: 100px;
                    min-width: 200px;
                    min-height: 200px;
                    max-width: 200px;
                    max-height: 200px;
                    text-align: center;
                    line-height: 200px;
                """)
                photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        except Exception as e:
            print(f"Error loading photo: {e}")
            # Fallback to text avatar
            photo_label.setText(name[0])
            photo_label.setStyleSheet("""
                background-color: #388e3c; 
                color: white; 
                font-size: 72px; 
                font-weight: bold;
                border-radius: 100px;
                min-width: 200px;
                min-height: 200px;
                max-width: 200px;
                max-height: 200px;
                text-align: center;
                line-height: 200px;
            """)
            photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Name
        name_label = QLabel(name)
        name_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-top: 10px;")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Role
        role_label = QLabel(role)
        role_label.setStyleSheet("font-size: 16px; color: #4caf50; margin-top: 5px;")
        role_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Quote - Fix the unclosed parenthesis by using different quote symbols
        quote_label = QLabel(f'"{quote}"')
        quote_label.setStyleSheet("font-size: 14px; font-style: italic; margin-top: 15px; color: #cccccc;")
        quote_label.setWordWrap(True)
        quote_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add to layout
        layout.addWidget(photo_label)
        layout.addWidget(name_label)
        layout.addWidget(role_label)
        layout.addWidget(quote_label)
        
        self.setLayout(layout)


class HorizontalScrollCard(QFrame):
    """A custom card for horizontal scrolling items"""
    def __init__(self, title, photo_path, subtitle, description):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            HorizontalScrollCard {
                background-color: #1e1e1e;
                color: white;
                border-radius: 10px;
                padding: 10px;
                min-height: 200px;
                min-width: 250px;
                max-width: 250px;
                border: 1px solid #555555;
                margin: 5px;
            }
            HorizontalScrollCard:hover {
                transform: translateY(-5px);
                background-color: #2d2d2d;
                box-shadow: 0 8px 15px rgba(0,0,0,0.3);
                transition: all 0.3s ease;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Photo/Avatar
        photo_label = QLabel()
        try:
            # Try to load the photo from the path
            pixmap = QPixmap(photo_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                photo_label.setPixmap(pixmap)
                photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            else:
                # If photo can't be loaded, create an avatar with initials
                photo_label.setText(title[0] if title else "?")
                photo_label.setStyleSheet("""
                    background-color: #388e3c; 
                    color: white; 
                    font-size: 36px; 
                    font-weight: bold;
                    border-radius: 40px;
                    min-width: 80px;
                    min-height: 80px;
                    max-width: 80px;
                    max-height: 80px;
                    text-align: center;
                    line-height: 80px;
                """)
                photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        except Exception as e:
            print(f"Error loading photo: {e}")
            # Fallback to text avatar
            photo_label.setText(title[0] if title else "?")
            photo_label.setStyleSheet("""
                background-color: #388e3c; 
                color: white; 
                font-size: 36px; 
                font-weight: bold;
                border-radius: 40px;
                min-width: 80px;
                min-height: 80px;
                max-width: 80px;
                max-height: 80px;
                text-align: center;
                line-height: 80px;
            """)
            photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 10px;")
        
        # Subtitle
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("font-size: 14px; color: #4caf50;")
        
        # Description
        description_label = QLabel(description)
        description_label.setStyleSheet("font-size: 12px; margin-top: 5px; color: #aaaaaa;")
        description_label.setWordWrap(True)
        
        # Add to layout
        layout.addWidget(photo_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addWidget(description_label)
        
        self.setLayout(layout)


class AdminApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Beyond Hunger Admin Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        
        # Set to full screen
        self.showFullScreen()
        
        # Dark theme stylesheet
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #121212;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                border-radius: 5px;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #cccccc;
                padding: 10px 15px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #388e3c;
                color: white;
                font-weight: bold;
            }
            QTabBar::tab:hover:!selected {
                background-color: #3d3d3d;
            }
            QTableWidget {
                background-color: #1e1e1e;
                alternate-background-color: #262626;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 5px;
                gridline-color: #555555;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #2d7d32;
                color: white;
            }
            QHeaderView::section {
                background-color: #388e3c;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QPushButton {
                background-color: #388e3c;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2d7d32;
            }
            QPushButton:pressed {
                background-color: #1b5e20;
            }
            QLabel {
                color: #ffffff;
            }
            QComboBox {
                background-color: #333333;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QComboBox:focus {
                border: 1px solid #388e3c;
            }
            QGroupBox {
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 1ex;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QScrollBar:vertical {
                background-color: #1e1e1e;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                background-color: #1e1e1e;
                height: 12px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background-color: #555555;
                min-width: 20px;
                border-radius: 6px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)
        
        # Add exit full screen button
        self.exit_fs_button = QPushButton("Exit Full Screen [ESC]")
        self.exit_fs_button.setStyleSheet("""
            background-color: #d32f2f;
            font-weight: bold;
            padding: 8px 15px;
        """)
        self.exit_fs_button.clicked.connect(self.toggle_fullscreen)
        
        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Header with title and exit button
        header_layout = QHBoxLayout()
        
        # Header
        self.header = QLabel("Beyond Hunger Admin Dashboard")
        self.header.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #4caf50;
            padding: 10px;
            margin-bottom: 15px;
            border-bottom: 2px solid #388e3c;
        """)
        header_layout.addWidget(self.header)
        header_layout.addStretch()
        header_layout.addWidget(self.exit_fs_button)
        
        self.main_layout.addLayout(header_layout)
        
        # Stats area
        self.stats_widget = QWidget()
        self.stats_layout = QHBoxLayout(self.stats_widget)
        
        # Will be populated in refresh_data
        self.users_card = None
        self.donations_card = None
        self.active_card = None
        self.cancelled_card = None
        
        self.main_layout.addWidget(self.stats_widget)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        # Create tabs
        self.donations_tab = QWidget()
        self.assignments_tab = QWidget()
        self.users_tab = QWidget()
        self.volunteers_tab = QWidget()
        self.about_tab = QWidget()  # New About tab
        
        self.tabs.addTab(self.donations_tab, "Donations")
        self.tabs.addTab(self.assignments_tab, "Delivery Assignments")
        self.tabs.addTab(self.users_tab, "Users")
        self.tabs.addTab(self.volunteers_tab, "Volunteers")
        self.tabs.addTab(self.about_tab, "About")  # Add the new tab
        
        # Set up each tab
        self.setup_donations_tab()
        self.setup_assignments_tab()
        self.setup_users_tab()
        self.setup_volunteers_tab()
        self.setup_about_tab()  # Set up the new About tab
        
        # Refresh button and auto-refresh
        self.refresh_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh Data")
        self.refresh_button.clicked.connect(self.refresh_data)
        self.refresh_layout.addStretch()
        self.refresh_layout.addWidget(self.refresh_button)
        self.main_layout.addLayout(self.refresh_layout)
        
        # Setup auto-refresh timer (refresh every 30 seconds)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(30000)  # 30 seconds
        
        # Load initial data
        self.refresh_data()
    
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.exit_fs_button.setText("Enter Full Screen")
        else:
            self.showFullScreen()
            self.exit_fs_button.setText("Exit Full Screen [ESC]")
    
    # Override keyPressEvent to handle Escape key
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape and self.isFullScreen():
            self.showNormal()
            self.exit_fs_button.setText("Enter Full Screen")
        else:
            super().keyPressEvent(event)
    
    def setup_donations_tab(self):
        layout = QVBoxLayout(self.donations_tab)
        
        # Table for donations
        self.donations_table = QTableWidget()
        self.donations_table.setColumnCount(9)
        self.donations_table.setHorizontalHeaderLabels([
            "ID", "Donor", "Food Type", "Quantity", "Pickup Date", 
            "Status", "Payment Status", "Created", "Actions"
        ])
        self.donations_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.donations_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.donations_table)
    
    def setup_assignments_tab(self):
        layout = QVBoxLayout(self.assignments_tab)
        
        # Add horizontal scrolling area for delivery partners
        scroll_label = QLabel("Delivery Partners")
        scroll_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            margin-top: 10px;
            margin-bottom: 5px;
        """)
        layout.addWidget(scroll_label)
        
        # Create scroll area and widget
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setMaximumHeight(250)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:horizontal {
                background: #1e1e1e;
                height: 10px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #388e3c;
                min-width: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)
        
        scroll_content = QWidget()
        scroll_layout = QHBoxLayout(scroll_content)
        
        # Will be populated in refresh_data
        self.delivery_cards_layout = scroll_layout
        
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        # Table for assignments (existing code)
        layout.addWidget(QLabel("Delivery Assignment Details"))
        
        # Assignments table (existing)
        self.assignments_table = QTableWidget()
        self.assignments_table.setColumnCount(8)
        self.assignments_table.setHorizontalHeaderLabels([
            "ID", "Donation", "Volunteer", "Status", 
            "Pickup Time", "Delivery Time", "Created", "Actions"
        ])
        self.assignments_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.assignments_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.assignments_table)
    
    def setup_users_tab(self):
        layout = QVBoxLayout(self.users_tab)
        
        # Table for users
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(8)
        self.users_table.setHorizontalHeaderLabels([
            "ID", "Username", "Email", "Name", 
            "Phone", "Address", "Roles", "Joined"
        ])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.users_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.users_table)
    
    def setup_volunteers_tab(self):
        layout = QVBoxLayout(self.volunteers_tab)
        
        # Add horizontal scrolling area for volunteer profiles
        scroll_label = QLabel("Volunteer Profiles")
        scroll_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            margin-top: 10px;
            margin-bottom: 5px;
        """)
        layout.addWidget(scroll_label)
        
        # Create scroll area and widget
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setMaximumHeight(250)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:horizontal {
                background: #1e1e1e;
                height: 10px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #388e3c;
                min-width: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)
        
        scroll_content = QWidget()
        scroll_layout = QHBoxLayout(scroll_content)
        
        # Will be populated in refresh_data
        self.volunteer_cards_layout = scroll_layout
        
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        # Table for volunteers (existing code)
        layout.addWidget(QLabel("Volunteer Details"))
        
        # Volunteer table (existing)
        self.volunteers_table = QTableWidget()
        self.volunteers_table.setColumnCount(8)
        self.volunteers_table.setHorizontalHeaderLabels([
            "ID", "Volunteer", "Phone", "Availability", 
            "Vehicle Type", "Service Area", "Active Assignments", "Joined"
        ])
        self.volunteers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.volunteers_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.volunteers_table)
    
    def setup_about_tab(self):
        """Setup the About tab with founder information"""
        layout = QVBoxLayout(self.about_tab)
        
        # Header
        header = QLabel("Meet Our Team")
        header.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #4caf50;
            margin-bottom: 20px;
            text-align: center;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Founders section
        founders_layout = QHBoxLayout()
        
        # Founder 
        founder = FounderCard(
            "Neal Jain", 
            "Founder & CEO", 
            "static/images/founder.jpg",
            "Our mission at Beyond Hunger is to create a sustainable food ecosystem where surplus meets scarcity, ensuring no one goes to bed hungry while eliminating food waste."
        )
        
        # Co-founder 1
        cofounder1 = FounderCard(
            "Shreyasi", 
            "Co-founder & COO", 
            "static/images/co-founder.jpeg",
            "Beyond Hunger represents our commitment to building lasting community connections through food redistribution, making every meal matter."
        )
        
        # Co-founder 2
        cofounder2 = FounderCard(
            "Manali", 
            "Co-founder & CTO", 
            "static/images/co-founder2.jpeg",
            "Technology empowers us to bridge food gaps efficiently. At Beyond Hunger, we're using innovation to solve one of humanity's oldest challenges."
        )
        
        founders_layout.addWidget(founder)
        founders_layout.addWidget(cofounder1)
        founders_layout.addWidget(cofounder2)
        
        layout.addLayout(founders_layout)
        
        # Mission Statement
        mission_group = QGroupBox("Our Mission")
        mission_group.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                margin-top: 30px;
            }
        """)
        mission_layout = QVBoxLayout()
        
        mission_text = QLabel(
            "Beyond Hunger is dedicated to reducing food waste and alleviating hunger "
            "by connecting food donors with volunteers who deliver to those in need. "
            "We believe in creating sustainable communities where everyone has access to nutritious food. "
            "Our innovative platform makes it easy for restaurants, catering services, and individuals "
            "to donate surplus food and for volunteers to deliver it to shelters and families in need."
        )
        mission_text.setWordWrap(True)
        mission_text.setStyleSheet("font-size: 16px; line-height: 1.5;")
        
        mission_layout.addWidget(mission_text)
        mission_group.setLayout(mission_layout)
        
        layout.addWidget(mission_group)
        
        # Add stretch to push everything to the top
        layout.addStretch()
    
    def refresh_data(self):
        """Refresh all data from the database"""
        # Get data
        users = User.objects.all().order_by('-date_joined')
        user_profiles = UserProfile.objects.all().order_by('-created_at')
        donations = FoodDonation.objects.all().order_by('-created_at')
        volunteers = Volunteer.objects.all().order_by('-created_at')
        assignments = DeliveryAssignment.objects.all().order_by('-created_at')
        
        # Stats
        total_users = users.count()
        total_donors = UserProfile.objects.filter(is_donor=True).count()
        total_volunteers = UserProfile.objects.filter(is_volunteer=True).count()
        total_donations = donations.count()
        pending_donations = donations.filter(status='pending').count()
        completed_donations = donations.filter(status='delivered').count()
        cancelled_donations = donations.filter(status='cancelled').count()
        active_assignments = assignments.filter(status__in=['assigned', 'picked_up']).count()
        
        # Update stats cards
        # First clear existing stats widget
        for i in reversed(range(self.stats_layout.count())): 
            self.stats_layout.itemAt(i).widget().setParent(None)
        
        # Create new stat cards with dark theme colors
        self.users_card = StatCard("Users", total_users, f"{total_donors} Donors / {total_volunteers} Volunteers", color="#388e3c")
        self.donations_card = StatCard("Donations", total_donations, f"{pending_donations} Pending / {completed_donations} Completed", color="#1976d2")
        self.active_card = StatCard("Active Deliveries", active_assignments, "Assignments in progress", color="#7b1fa2")
        self.cancelled_card = StatCard("Cancelled", cancelled_donations, "Cancelled donations", color="#e64a19")
        
        self.stats_layout.addWidget(self.users_card)
        self.stats_layout.addWidget(self.donations_card)
        self.stats_layout.addWidget(self.active_card)
        self.stats_layout.addWidget(self.cancelled_card)
        
        # Clear horizontal scroll areas
        self.clear_horizontal_scroll_areas()
        
        # Update volunteer cards in horizontal scroll
        self.update_volunteer_cards(volunteers)
        
        # Update delivery partner cards in horizontal scroll
        self.update_delivery_cards(assignments)
        
        # Update donations table
        self.update_donations_table(donations)
        
        # Update assignments table
        self.update_assignments_table(assignments)
        
        # Update users table
        self.update_users_table(user_profiles)
        
        # Update volunteers table
        self.update_volunteers_table(volunteers, assignments)
    
    def clear_horizontal_scroll_areas(self):
        """Clear the horizontal scrolling areas for volunteers and delivery partners"""
        # Clear volunteer cards
        for i in reversed(range(self.volunteer_cards_layout.count())):
            widget = self.volunteer_cards_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Clear delivery partner cards
        for i in reversed(range(self.delivery_cards_layout.count())):
            widget = self.delivery_cards_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
    
    def update_volunteer_cards(self, volunteers):
        """Update the volunteer cards in the horizontal scroll area"""
        # Create cards for each volunteer
        for volunteer in volunteers:
            user = volunteer.user
            full_name = f"{user.first_name} {user.last_name}".strip()
            if not full_name:
                full_name = user.username
            
            # Create description
            if volunteer.availability:
                availability = "Available"
            else:
                availability = "Not Available"
            
            description = f"Vehicle: {volunteer.vehicle_type or 'Not specified'}\nArea: {volunteer.service_area}"
            
            # Create card
            card = HorizontalScrollCard(
                full_name,
                "",  # No photo path - will use initial avatar
                availability,
                description
            )
            
            self.volunteer_cards_layout.addWidget(card)
        
        # Add stretch to ensure cards are aligned to the left
        self.volunteer_cards_layout.addStretch()
    
    def update_delivery_cards(self, assignments):
        """Update the delivery partner cards in the horizontal scroll area"""
        # Create a unique set of delivery partners
        delivery_partners = {}
        manual_partners = {}
        
        for assignment in assignments:
            if assignment.status in ['assigned', 'picked_up']:
                # Check if notes contain manual delivery partner info
                if "Manual delivery partner:" in assignment.notes:
                    try:
                        partner_name = assignment.notes.split("Manual delivery partner:")[1].split(",")[0].strip()
                        if partner_name not in manual_partners:
                            manual_partners[partner_name] = {
                                'name': partner_name,
                                'count': 1,
                                'is_manual': True
                            }
                        else:
                            manual_partners[partner_name]['count'] += 1
                    except:
                        pass  # If parsing fails, ignore
                else:
                    # Database volunteer
                    vol_id = assignment.volunteer.id
                    if vol_id not in delivery_partners:
                        user = assignment.volunteer.user
                        full_name = f"{user.first_name} {user.last_name}".strip()
                        if not full_name:
                            full_name = user.username
                        
                        delivery_partners[vol_id] = {
                            'name': full_name,
                            'count': 1,
                            'is_manual': False,
                            'volunteer': assignment.volunteer
                        }
                    else:
                        delivery_partners[vol_id]['count'] += 1
        
        # Create cards for database volunteers
        for vol_id, info in delivery_partners.items():
            subtitle = f"Active Deliveries: {info['count']}"
            description = f"Vehicle: {info['volunteer'].vehicle_type or 'Not specified'}\nArea: {info['volunteer'].service_area}"
            
            card = HorizontalScrollCard(
                info['name'],
                "",  # No photo path - will use initial avatar
                subtitle,
                description
            )
            
            self.delivery_cards_layout.addWidget(card)
        
        # Create cards for manual partners
        for name, info in manual_partners.items():
            subtitle = f"Active Deliveries: {info['count']}"
            description = "Manually assigned delivery partner"
            
            card = HorizontalScrollCard(
                info['name'],
                "",  # No photo path - will use initial avatar
                subtitle,
                description
            )
            
            # Use a different style for manual partners
            card.setStyleSheet("""
                HorizontalScrollCard {
                    background-color: #1e1e1e;
                    color: white;
                    border-radius: 10px;
                    padding: 10px;
                    min-height: 200px;
                    min-width: 250px;
                    max-width: 250px;
                    border: 1px solid #7b1fa2;
                    margin: 5px;
                }
                HorizontalScrollCard:hover {
                    transform: translateY(-5px);
                    background-color: #2d2d2d;
                    box-shadow: 0 8px 15px rgba(0,0,0,0.3);
                    transition: all 0.3s ease;
                }
            """)
            
            self.delivery_cards_layout.addWidget(card)
        
        # Add stretch to ensure cards are aligned to the left
        self.delivery_cards_layout.addStretch()
    
    def update_donations_table(self, donations):
        self.donations_table.setRowCount(0)  # Clear table
        
        for row, donation in enumerate(donations):
            self.donations_table.insertRow(row)
            
            # ID
            id_item = QTableWidgetItem(str(donation.id))
            id_item.setData(Qt.ItemDataRole.UserRole, donation.id)
            self.donations_table.setItem(row, 0, id_item)
            
            # Donor
            self.donations_table.setItem(row, 1, QTableWidgetItem(donation.donor.username))
            
            # Food Type
            self.donations_table.setItem(row, 2, QTableWidgetItem(donation.food_type))
            
            # Quantity
            self.donations_table.setItem(row, 3, QTableWidgetItem(donation.quantity))
            
            # Pickup Date
            pickup_date = donation.pickup_date.strftime("%b %d, %Y")
            self.donations_table.setItem(row, 4, QTableWidgetItem(pickup_date))
            
            # Status
            status_item = QTableWidgetItem(donation.get_status_display())
            if donation.status == 'pending':
                status_item.setBackground(QBrush(QColor('#8B4500')))  # dark orange
            elif donation.status == 'delivered':
                status_item.setBackground(QBrush(QColor('#006400')))  # dark green
            elif donation.status == 'cancelled':
                status_item.setBackground(QBrush(QColor('#8B0000')))  # dark red
            self.donations_table.setItem(row, 5, status_item)
            
            # Payment Status
            if donation.payment_method:
                payment_item = QTableWidgetItem(donation.get_payment_status_display())
                if donation.payment_status == 'completed':
                    payment_item.setBackground(QBrush(QColor('#006400')))  # dark green
                elif donation.payment_status == 'pending':
                    payment_item.setBackground(QBrush(QColor('#8B4500')))  # dark orange
                else:
                    payment_item.setBackground(QBrush(QColor('#8B0000')))  # dark red
            else:
                payment_item = QTableWidgetItem("None")
            self.donations_table.setItem(row, 6, payment_item)
            
            # Created
            created_at = donation.created_at.strftime("%b %d, %Y %H:%M")
            self.donations_table.setItem(row, 7, QTableWidgetItem(created_at))
            
            # Actions - Now with three buttons in a layout
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)  # Small margins to save space
            
            # Update button
            update_button = QPushButton("Update")
            update_button.clicked.connect(lambda checked, d=donation: self.update_donation_status(d))
            
            # Assign delivery button
            has_delivery = DeliveryAssignment.objects.filter(donation=donation).exists()
            assign_button = QPushButton("Re-assign" if has_delivery else "Assign")
            
            # Change button color based on whether it's assigned
            if has_delivery:
                assign_button.setStyleSheet("""
                    background-color: #9C27B0;
                    color: white;
                    border-radius: 3px;
                    padding: 8px 15px;
                    border: none;
                """)
            
            assign_button.clicked.connect(lambda checked, d=donation: self.assign_delivery_partner(d))
            
            # Discard button (only show if not already cancelled)
            if donation.status != 'cancelled':
                discard_button = QPushButton("Discard")
                discard_button.setStyleSheet("""
                    background-color: #d32f2f;
                    color: white;
                    border-radius: 3px;
                    padding: 8px 15px;
                    border: none;
                """)
                discard_button.clicked.connect(lambda checked, d=donation: self.discard_donation(d))
                actions_layout.addWidget(discard_button)
            
            actions_layout.addWidget(update_button)
            actions_layout.addWidget(assign_button)
            
            self.donations_table.setCellWidget(row, 8, actions_widget)
    
    def update_assignments_table(self, assignments):
        self.assignments_table.setRowCount(0)  # Clear table
        
        for row, assignment in enumerate(assignments):
            self.assignments_table.insertRow(row)
            
            # ID
            id_item = QTableWidgetItem(str(assignment.id))
            id_item.setData(Qt.ItemDataRole.UserRole, assignment.id)
            self.assignments_table.setItem(row, 0, id_item)
            
            # Donation
            donation_text = f"{assignment.donation.food_type} (ID: {assignment.donation.id})"
            self.assignments_table.setItem(row, 1, QTableWidgetItem(donation_text))
            
            # Volunteer/Partner
            partner_text = assignment.volunteer.user.username
            
            # Check if notes contain manual delivery partner info
            if "Manual delivery partner:" in assignment.notes:
                try:
                    partner_name = assignment.notes.split("Manual delivery partner:")[1].split(",")[0].strip()
                    partner_text = f"{partner_name} (Manual)"
                except:
                    pass  # If parsing fails, use the volunteer username
            
            self.assignments_table.setItem(row, 2, QTableWidgetItem(partner_text))
            
            # Status
            status_item = QTableWidgetItem(assignment.get_status_display())
            if assignment.status == 'assigned':
                status_item.setBackground(QBrush(QColor('#8B4500')))  # dark orange
            elif assignment.status == 'picked_up':
                status_item.setBackground(QBrush(QColor('#00008B')))  # dark blue
            elif assignment.status == 'delivered':
                status_item.setBackground(QBrush(QColor('#006400')))  # dark green
            elif assignment.status == 'cancelled':
                status_item.setBackground(QBrush(QColor('#8B0000')))  # dark red
            self.assignments_table.setItem(row, 3, status_item)
            
            # Pickup Time
            pickup_time = assignment.pickup_time.strftime("%b %d, %Y %H:%M")
            self.assignments_table.setItem(row, 4, QTableWidgetItem(pickup_time))
            
            # Delivery Time
            if assignment.delivery_time:
                delivery_time = assignment.delivery_time.strftime("%b %d, %Y %H:%M")
            else:
                delivery_time = "Not delivered yet"
            self.assignments_table.setItem(row, 5, QTableWidgetItem(delivery_time))
            
            # Created
            created_at = assignment.created_at.strftime("%b %d, %Y %H:%M")
            self.assignments_table.setItem(row, 6, QTableWidgetItem(created_at))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            
            update_button = QPushButton("Update")
            update_button.clicked.connect(lambda checked, a=assignment: self.update_assignment_status(a))
            
            actions_layout.addWidget(update_button)
            
            # Only show discard if not already cancelled
            if assignment.status != 'cancelled':
                discard_button = QPushButton("Discard")
                discard_button.setStyleSheet("""
                    background-color: #d32f2f;
                    color: white;
                    border-radius: 3px;
                    padding: 8px 15px;
                    border: none;
                """)
                discard_button.clicked.connect(lambda checked, a=assignment: self.discard_assignment(a))
                actions_layout.addWidget(discard_button)
            
            self.assignments_table.setCellWidget(row, 7, actions_widget)
    
    def update_users_table(self, user_profiles):
        self.users_table.setRowCount(0)  # Clear table
        
        for row, profile in enumerate(user_profiles):
            self.users_table.insertRow(row)
            
            # ID
            self.users_table.setItem(row, 0, QTableWidgetItem(str(profile.user.id)))
            
            # Username
            self.users_table.setItem(row, 1, QTableWidgetItem(profile.user.username))
            
            # Email
            self.users_table.setItem(row, 2, QTableWidgetItem(profile.user.email))
            
            # Name
            name = f"{profile.user.first_name} {profile.user.last_name}".strip()
            if not name:
                name = "-"
            self.users_table.setItem(row, 3, QTableWidgetItem(name))
            
            # Phone
            self.users_table.setItem(row, 4, QTableWidgetItem(profile.phone))
            
            # Address
            address_item = QTableWidgetItem(profile.address)
            address_item.setToolTip(profile.address)  # Show full address on hover
            self.users_table.setItem(row, 5, address_item)
            
            # Roles
            roles = []
            if profile.user.is_superuser:
                roles.append("Admin")
            if profile.is_donor:
                roles.append("Donor")
            if profile.is_volunteer:
                roles.append("Volunteer")
            
            role_item = QTableWidgetItem(", ".join(roles))
            self.users_table.setItem(row, 6, role_item)
            
            # Joined
            joined = profile.user.date_joined.strftime("%b %d, %Y")
            self.users_table.setItem(row, 7, QTableWidgetItem(joined))
    
    def update_volunteers_table(self, volunteers, assignments):
        self.volunteers_table.setRowCount(0)  # Clear table
        
        for row, volunteer in enumerate(volunteers):
            self.volunteers_table.insertRow(row)
            
            # ID
            self.volunteers_table.setItem(row, 0, QTableWidgetItem(str(volunteer.id)))
            
            # Volunteer username
            self.volunteers_table.setItem(row, 1, QTableWidgetItem(volunteer.user.username))
            
            # Phone
            self.volunteers_table.setItem(row, 2, QTableWidgetItem(volunteer.user.userprofile.phone))
            
            # Availability
            availability = "Available" if volunteer.availability else "Not Available"
            availability_item = QTableWidgetItem(availability)
            if volunteer.availability:
                availability_item.setBackground(QBrush(QColor('#006400')))  # dark green
            else:
                availability_item.setBackground(QBrush(QColor('#8B0000')))  # dark red
            self.volunteers_table.setItem(row, 3, availability_item)
            
            # Vehicle Type
            vehicle_type = volunteer.vehicle_type if volunteer.vehicle_type else "Not specified"
            self.volunteers_table.setItem(row, 4, QTableWidgetItem(vehicle_type))
            
            # Service Area
            self.volunteers_table.setItem(row, 5, QTableWidgetItem(volunteer.service_area))
            
            # Active Assignments
            active_count = 0
            for assignment in assignments:
                if assignment.volunteer.id == volunteer.id and assignment.status in ['assigned', 'picked_up']:
                    active_count += 1
            
            active_assignments = f"{active_count} active" if active_count > 0 else "None"
            active_item = QTableWidgetItem(active_assignments)
            if active_count > 0:
                active_item.setBackground(QBrush(QColor('#00008B')))  # dark blue
            self.volunteers_table.setItem(row, 6, active_item)
            
            # Joined
            joined = volunteer.created_at.strftime("%b %d, %Y")
            self.volunteers_table.setItem(row, 7, QTableWidgetItem(joined))
    
    def update_donation_status(self, donation):
        dialog = StatusUpdateDialog(
            self, 
            donation, 
            FoodDonation.STATUS_CHOICES, 
            "donation"
        )
        
        if dialog.exec():
            new_status = dialog.get_selected_status()
            try:
                # Update donation status
                donation.status = new_status
                donation.save()
                
                QMessageBox.information(
                    self, 
                    "Status Updated", 
                    f"Donation status has been updated to {dict(FoodDonation.STATUS_CHOICES)[new_status]}."
                )
                
                # Refresh the data
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    "Error", 
                    f"An error occurred: {str(e)}"
                )
    
    def update_assignment_status(self, assignment):
        dialog = StatusUpdateDialog(
            self, 
            assignment, 
            DeliveryAssignment.STATUS_CHOICES, 
            "assignment"
        )
        
        if dialog.exec():
            new_status = dialog.get_selected_status()
            try:
                # Update assignment status
                assignment.status = new_status
                assignment.save()
                
                # If status is delivered, update the delivery time
                from django.utils import timezone
                if new_status == 'delivered':
                    assignment.delivery_time = timezone.now()
                    assignment.save()
                    
                # Also update the donation status
                if assignment.donation.status != 'delivered':
                    assignment.donation.status = 'delivered'
                    assignment.donation.save()
                
                QMessageBox.information(
                    self, 
                    "Status Updated", 
                    f"Assignment status has been updated to {dict(DeliveryAssignment.STATUS_CHOICES)[new_status]}."
                )
                
                # Refresh the data
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    "Error", 
                    f"An error occurred: {str(e)}"
                )
    
    def assign_delivery_partner(self, donation):
        """Show dialog to assign a delivery partner to a donation"""
        # Check if donation status is not appropriate for delivery
        if donation.status == 'cancelled':
            QMessageBox.warning(
                self, 
                "Cannot Assign Delivery", 
                "Cannot assign delivery for cancelled donations."
            )
            return
        
        dialog = AssignDeliveryDialog(self, donation)
        
        if dialog.exec():
            pickup_time = dialog.get_pickup_time()
            notes = dialog.get_notes()
            
            try:
                # Check if there's an existing assignment
                existing_assignment = DeliveryAssignment.objects.filter(donation=donation).first()
                
                if dialog.tab_widget.currentIndex() == 0 and dialog.selected_volunteer:
                    # Database selection was used
                    volunteer = dialog.selected_volunteer
                    
                    if existing_assignment:
                        # Update existing assignment
                        existing_assignment.volunteer = volunteer
                        existing_assignment.pickup_time = pickup_time
                        existing_assignment.notes = notes
                        existing_assignment.status = 'assigned'  # Reset to assigned status
                        existing_assignment.save()
                        
                        message = f"Delivery reassigned to {volunteer.user.username}"
                    else:
                        # Create new assignment with database volunteer
                        DeliveryAssignment.objects.create(
                            donation=donation,
                            volunteer=volunteer,
                            status='assigned',
                            pickup_time=pickup_time,
                            notes=notes
                        )
                        
                        message = f"Delivery assigned to {volunteer.user.username}"
                else:
                    # Manual name entry was used
                    manual_name = dialog.manual_name
                    manual_phone = dialog.get_manual_phone()
                    
                    # Update notes to include the manual name and phone
                    full_notes = f"Manual delivery partner: {manual_name}"
                    if manual_phone:
                        full_notes += f", Phone: {manual_phone}"
                    if notes:
                        full_notes += f"\nNotes: {notes}"
                    
                    if existing_assignment:
                        # Update existing assignment notes with manual info
                        existing_assignment.notes = full_notes
                        existing_assignment.pickup_time = pickup_time
                        existing_assignment.status = 'assigned'  # Reset to assigned status
                        existing_assignment.save()
                    else:
                        # Find any volunteer (available or not) to associate with the delivery
                        volunteer = None
                        
                        # First try to get any volunteer regardless of availability
                        volunteer = Volunteer.objects.first()
                        
                        if not volunteer:
                            # No volunteers exist in the database at all
                            # Create a dummy system volunteer if no volunteer exists
                            from django.contrib.auth.models import User
                            
                            # Try to find or create system user
                            system_user, created = User.objects.get_or_create(
                                username='system',
                                defaults={
                                    'first_name': 'System',
                                    'last_name': 'Account',
                                    'email': 'system@example.com',
                                    'is_active': True
                                }
                            )
                            
                            # Try to find or create system volunteer
                            volunteer, created = Volunteer.objects.get_or_create(
                                user=system_user,
                                defaults={
                                    'availability': False,
                                    'vehicle_type': 'System',
                                    'service_area': 'System'
                                }
                            )
                            
                            if created:
                                # Also create UserProfile if needed
                                UserProfile.objects.get_or_create(
                                    user=system_user,
                                    defaults={
                                        'phone': '0000000000',
                                        'address': 'System Account',
                                        'is_volunteer': True
                                    }
                                )
                        
                        # Create new assignment with the volunteer but manual notes
                        DeliveryAssignment.objects.create(
                            donation=donation,
                            volunteer=volunteer,
                            status='assigned',
                            pickup_time=pickup_time,
                            notes=full_notes
                        )
                    
                    message = f"Delivery assigned to manually entered partner: {manual_name}"
                
                # Update donation status to "accepted" if it's "pending"
                if donation.status == 'pending':
                    donation.status = 'accepted'
                    donation.save()
                
                QMessageBox.information(
                    self, 
                    "Delivery Assigned", 
                    message
                )
                
                # Refresh the data
                self.refresh_data()
                
                # Switch to Assignments tab to see the new assignment
                self.tabs.setCurrentIndex(1)  # Assuming Assignments is the second tab
                
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    "Error", 
                    f"An error occurred while assigning delivery: {str(e)}"
                )
    
    def discard_donation(self, donation):
        """Mark a donation as cancelled"""
        # Ask for confirmation
        confirm = QMessageBox.question(
            self,
            "Confirm Discard",
            f"Are you sure you want to discard donation #{donation.id}?\nThis will cancel the donation and any associated delivery.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                # Cancel any associated delivery assignment
                assignment = DeliveryAssignment.objects.filter(donation=donation).first()
                if assignment:
                    assignment.status = 'cancelled'
                    assignment.save()
                
                # Cancel the donation
                donation.status = 'cancelled'
                donation.save()
                
                QMessageBox.information(
                    self,
                    "Donation Discarded",
                    f"Donation #{donation.id} has been discarded."
                )
                
                # Refresh the data
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"An error occurred while discarding the donation: {str(e)}"
                )
    
    def discard_assignment(self, assignment):
        """Mark an assignment as cancelled"""
        # Ask for confirmation
        confirm = QMessageBox.question(
            self,
            "Confirm Discard",
            f"Are you sure you want to discard this delivery assignment?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                # Cancel the assignment
                assignment.status = 'cancelled'
                assignment.save()
                
                QMessageBox.information(
                    self,
                    "Assignment Discarded",
                    f"Delivery assignment has been discarded."
                )
                
                # Refresh the data
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"An error occurred while discarding the assignment: {str(e)}"
                )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application-wide dark palette
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(18, 18, 18))
    dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(38, 38, 38))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(30, 30, 30))
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(50, 50, 50))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Link, QColor(56, 142, 60))
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(56, 142, 60))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(dark_palette)
    
    window = AdminApp()
    window.show()
    sys.exit(app.exec()) 