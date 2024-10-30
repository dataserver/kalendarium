from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QVBoxLayout, QWidget
from qfluentwidgets import ScrollArea, StrongBodyLabel

from helpers.utility import clear_layout
from models import repository_events
from widgets.event_card import EventCard
from widgets.weather_forecast import WeatherForecastWidget


class HomeInterface(ScrollArea):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.today = datetime.now()
        self.setObjectName("home_interface")
        self._init_widget()
        self._init_layout()
        self._connect_signals()

    def _init_widget(self):
        self.main_container = QWidget()
        self.main_container.setObjectName("container_view")
        self.main_layout = QVBoxLayout(self.main_container)
        self.main_container.setLayout(self.main_layout)
        # specify the widget that you want to display within the ScrollArea
        self.setWidget(self.main_container)
        self.inner_container = QWidget()
        self.inner_layout = QHBoxLayout(self.inner_container)

        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout()
        self.left_panel.setLayout(self.left_layout)

        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout()
        self.right_panel.setLayout(self.right_layout)

    def _init_layout(self):
        self.enableTransparentBackground()
        self.setViewportMargins(0, 0, 0, 0)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)

        self.inner_container.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.inner_layout.addWidget(self.left_panel, 1, Qt.AlignmentFlag.AlignTop)
        self.inner_layout.addWidget(self.right_panel, 2, Qt.AlignmentFlag.AlignTop)

        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_layout.addWidget(self.inner_container)

        # Initial population
        self.populate()

    def _connect_signals(self):
        pass

    def populate(self):
        """Populate the container with new widgets."""
        clear_layout(self.left_layout)
        clear_layout(self.right_layout)

        # weather
        weather_widget = WeatherForecastWidget()
        self.left_layout.addWidget(weather_widget)

        _day_of_week = self.tr(self.today.strftime("%A"))
        _date = self.today.strftime(f"%Y-%m-%d   ({_day_of_week})")
        self.right_layout.addWidget(StrongBodyLabel(self.tr("Today:") + f" {_date}"))

        events = repository_events.get_for_day(self.today)
        for event in events:
            card = EventCard(event)
            card.hide_buttons()
            card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            card.set_fontsize_title(14)
            self.right_layout.addWidget(card, 1, Qt.AlignmentFlag.AlignTop)
        self.right_layout.update()
