import calendar
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from qfluentwidgets import PrimaryPushButton, StrongBodyLabel

from constants.app_constants import DAY_OF_WEEK_CODE
from helpers.style_sheet import StyleSheet
from helpers.utility import clear_layout
from models import repository_events
from models.event import Event
from widgets.day_cell import DayCell

IS_CURRENT_MONTH = True
NOT_CURRENT_MONTH = False


class MonthlyCalendar(QWidget):
    """Widget to display a calendar with navigation and event management.

    This widget shows the current month in a grid layout and allows users to
    navigate between months. It also displays events scheduled for each day.

    """

    def __init__(self, start_of_week: int = DAY_OF_WEEK_CODE["SUNDAY"]):
        """
        Initializes the MonthlyCalendar and sets up the layout and event data.

        start of week:

        0 = Sunday, 1 = Monday, ..., 6 = Saturday
        """
        super().__init__()

        # 0 = Sunday, 1 = Monday, ..., 6 = Saturday
        self.start_of_week = start_of_week
        self.current_date = datetime.now()
        self.selected_date = None

        layout = QVBoxLayout()

        self.grid = QGridLayout()
        self.grid.setObjectName("grid_calendar")
        self.grid.setSpacing(5)  # Space between widgets
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        # self.grid.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Header for Month and Year
        _m = self.tr(self.current_date.strftime("%B"))
        self.header = QLabel(self.current_date.strftime(f"{_m} %Y"))
        self.header.setContentsMargins(40, 0, 40, 0)
        self.header.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.header.setProperty("class", "calendar_month_title")

        # Navigation buttons
        self.previous_button = PrimaryPushButton(self.tr("← Previous"))
        self.previous_button.clicked.connect(self._show_previous_month)
        # self.previous_button.setProperty("class", "calendar_nav_button")

        self.next_button = PrimaryPushButton(self.tr("Next →"))
        self.next_button.clicked.connect(self._show_next_month)
        # self.next_button.setProperty("class", "calendar_nav_button")

        # Horizontal layout for navigation buttons
        nav_layout = QHBoxLayout()
        nav_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        nav_layout.addWidget(self.previous_button)
        nav_layout.addWidget(self.header)
        nav_layout.addWidget(self.next_button)

        layout.addLayout(nav_layout)
        layout.addLayout(self.grid)

        self.setLayout(layout)
        StyleSheet.MONTHLY_WIDGET.apply(self)
        self.populate()

        self._connect_signals()

    def _connect_signals(self):
        """Connect custom signals to their respective slots."""
        pass

    def set_start_of_week(self, start_of_week: int):
        self.start_of_week = start_of_week

    def populate(self):
        """Populate the calendar grid with days and corresponding events."""
        # Clear previous grid
        clear_layout(self.grid)

        month = self.current_date.month
        year = self.current_date.year
        self.events = repository_events.get_for_month(
            datetime(year=year, month=month, day=1)
        )

        # Define days of the week
        days_of_week = [
            self.tr("Sun"),
            self.tr("Mon"),
            self.tr("Tue"),
            self.tr("Wed"),
            self.tr("Thu"),
            self.tr("Fri"),
            self.tr("Sat"),
        ]
        # Rotate the list based on start_of_week
        # start_of_week = 0 = Sunday, 1 = Monday... 6 Saturday
        days_of_week = (
            days_of_week[self.start_of_week :] + days_of_week[: self.start_of_week]
        )

        # Add header for the days of the week
        for i, d in enumerate(days_of_week):
            l = StrongBodyLabel(d)
            l.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            l.setProperty("class", "calendar_header_days")
            self.grid.addWidget(l, 0, i)

        # Calculate first day of the month
        first_day = datetime(year, month, 1)
        days_in_month = calendar.monthrange(year, month)[
            1
        ]  # Get number of days in month

        # Get the day of the week (0 = Monday, ..., 6 = Sunday)
        start_day = first_day.weekday()  # 0 = Monday, 6 = Sunday
        start_day = (start_day + 1) % 7  # Adjust to 0 = Sunday, ..., 6 = Saturday

        # Calculate offset based on start_of_week
        start_offset = (start_day - self.start_of_week) % 7

        # Days from the previous month
        previous_month_days = calendar.monthrange(year, month - 1 if month > 1 else 12)[
            1
        ]

        # Fill the grid with 42 buttons (6 rows x 7 columns)
        day_index = 0  # Keep track of the current day index in the grid

        # Add greyed-out buttons for previous month's days
        for day in range(
            previous_month_days - start_offset + 1, previous_month_days + 1
        ):
            if day > 0:  # Ensure day is valid
                _dt = datetime(
                    year=year if month > 1 else year - 1,
                    month=(month - 1 if month > 1 else 12),
                    day=day,
                    hour=8,
                    minute=0,
                )
                _day_widget = DayCell(_dt, [], NOT_CURRENT_MONTH)
                self.grid.addWidget(_day_widget, day_index // 7 + 1, day_index % 7)
                day_index += 1

        # Add current month buttons
        for day in range(1, days_in_month + 1):
            _events = self._get_events_for_date(self.events, datetime(year, month, day))
            _dt = datetime(year=year, month=month, day=day, hour=8, minute=0)
            _day_widget = DayCell(_dt, _events, IS_CURRENT_MONTH)
            self.grid.addWidget(_day_widget, day_index // 7 + 1, day_index % 7)
            day_index += 1

        # Fill the remaining days with next month's greyed-out buttons if needed
        next_month_start = 1
        while day_index < 42:
            _dt = datetime(
                year=year if month < 12 else year + 1,
                month=(month + 1 if month < 12 else 1),
                day=next_month_start,
                hour=8,
                minute=0,
            )
            _day_widget = DayCell(_dt, [], NOT_CURRENT_MONTH)
            self.grid.addWidget(_day_widget, day_index // 7 + 1, day_index % 7)
            day_index += 1
            next_month_start += 1

        # Update header
        month = self.tr(first_day.strftime("%B"))
        self.header.setText(first_day.strftime(f"{month} %Y"))
        self.grid.update()
        self.events = []

    def _show_previous_month(self):
        """Navigate to the previous month in the calendar."""
        self.current_date = self._add_months(self.current_date, -1)
        self.populate()

    def _show_next_month(self):
        """Navigate to the next month in the calendar."""
        self.current_date = self._add_months(self.current_date, 1)
        self.populate()

    @staticmethod
    def _get_events_for_date(events: list[Event], date: datetime) -> list[Event]:
        """Filter events that occur on a specific date.

        Args:
            events (list[Event]): List of events to filter.
            date (datetime): The date to filter events by.

        Returns:
            list[Event]: List of events scheduled for the specified date.
        """
        target_date = date.date()

        # Filter events where scheduled_at matches the target date
        filtered_events = [
            event
            for event in events
            if event.scheduled_at and event.scheduled_at.date() == target_date
        ]

        return filtered_events

    @staticmethod
    def _add_months(current_date: datetime, months_to_add: int):
        new_date = datetime(
            current_date.year + (current_date.month + months_to_add - 1) // 12,
            (current_date.month + months_to_add - 1) % 12 + 1,
            current_date.day,
            current_date.hour,
            current_date.minute,
            current_date.second,
        )
        return new_date
