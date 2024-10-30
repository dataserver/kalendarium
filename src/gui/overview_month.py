from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget
from qfluentwidgets import ScrollArea

from config.config import cfg
from constants.app_constants import DAY_OF_WEEK_CODE
from widgets.monthly_calendar import MonthlyCalendar


class OverviewMonthInterface(ScrollArea):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("calendarInterface")

        self._init_widget()
        self._init_layout()
        self._connect_signal_to_slot()

    def _init_widget(self):
        self.main_container = QWidget()
        self.main_container.setObjectName("main_container")
        self.main_layout = QVBoxLayout(self.main_container)
        self.main_container.setLayout(self.main_layout)
        self.setWidget(self.main_container)
        self.inner_container = QWidget()
        self.inner_layout = QVBoxLayout(self.inner_container)

        # calendar
        start_of_week = DAY_OF_WEEK_CODE[cfg.get(cfg.start_of_week)]
        self.calendar = MonthlyCalendar(start_of_week)
        self.calendar.set_start_of_week(start_of_week)
        self.calendar.setObjectName("calendar")

    def _init_layout(self):
        self.enableTransparentBackground()
        self.setViewportMargins(0, 0, 0, 20)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.inner_container.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.main_layout.addWidget(self.calendar)

    def _connect_signal_to_slot(self):
        pass

    def populate(self):
        self.calendar.populate()
