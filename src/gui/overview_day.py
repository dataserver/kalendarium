from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget
from qfluentwidgets import FluentIcon, PushButton, ScrollArea, TitleLabel

from constants.app_constants import AppAction
from helpers.utility import clear_layout
from models import repository_events
from signals.signal_bus import signalBus
from widgets.event_card import EventCard


class OverviewDayInterface(ScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("day_events_interface")

        self.date: datetime = datetime.now()

        self._init_widget()
        self._init_layout()
        self._connect_signals()

    def _init_widget(self):
        self.main_container = QWidget()
        self.main_container.setObjectName("main_container")
        self.main_layout = QVBoxLayout(self.main_container)
        self.main_container.setLayout(self.main_layout)
        self.setWidget(self.main_container)
        self.inner_container = QWidget()
        self.inner_layout = QVBoxLayout(self.inner_container)

        self.panel_title_label = TitleLabel(self.tr("Template Interface"), self)
        self.panel_title_label.setObjectName("panel_title")
        self.btn_add = PushButton(FluentIcon.ADD, "Add Event", self)

        self.counter = 1

    def _init_layout(self):
        self.enableTransparentBackground()
        self.setViewportMargins(0, 120, 0, 20)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)

        self.panel_title_label.move(60, 60)
        self.btn_add.move(700, 60)
        self.inner_container.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        self.main_layout.setContentsMargins(60, 10, 60, 0)
        self.main_layout.setSpacing(40)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.main_layout.addWidget(self.inner_container)
        self.inner_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Initial population
        self.populate()

    def _connect_signals(self):
        self.btn_add.clicked.connect(self._add_event_today)

    def set_date(self, date: datetime):
        self.date = date
        self.populate()

    def populate(self):
        """Populate the container with new widgets."""
        clear_layout(self.inner_layout)  # Clear existing content

        _day_of_week = self.tr(self.date.strftime("%A"))
        title = self.date.strftime(f"%Y-%m-%d   ({_day_of_week})")
        self.panel_title_label.setText(title)

        events = []
        events = repository_events.get_for_day(self.date)

        for event in events:
            row = EventCard(event)
            self.inner_layout.addWidget(row, 0, Qt.AlignmentFlag.AlignTop)

    def _add_event_today(self):
        signalBus.calendar_actions_signal.emit(AppAction.VIEW_FORM_ADD, None, self.date)
