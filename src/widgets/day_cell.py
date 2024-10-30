from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget

from config.config import cfg
from constants.app_constants import AppAction
from helpers.style_sheet import StyleSheet
from models.event import Event
from signals.signal_bus import signalBus
from widgets.clickable_text import ClickableText


class DayCell(QWidget):
    def __init__(
        self,
        date: datetime,
        events: list[Event],
        is_current_month: bool = True,
    ) -> None:
        super().__init__()
        self.date = date
        is_weekend = self.date.weekday() >= 5

        if is_current_month:
            self.setProperty("class", "active_month")
        else:
            self.setProperty("class", "inactive_month")

        date_label = ClickableText(text=self.date.strftime("%d"), size=12)
        _css_class = "is_weekend_title" if is_weekend else "is_weekday_title"
        date_label.setProperty("class", _css_class)
        date_label.setMinimumSize(100, 40)
        date_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        date_label.clicked.connect(lambda dt=self.date: self._click_month(dt))

        if len(events) > 0:
            events_layout = QVBoxLayout()
            events_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            events_layout.setSpacing(0)  # No spacing between event frames
            events_layout.setContentsMargins(0, 0, 0, 0)  # No margins
            events_container = QWidget()
            events_container.setStyleSheet(f"background-color: transparent;")
            events_container.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
            )
            events_container.setLayout(events_layout)
            for e in events:
                _layout = QVBoxLayout()
                _container = QWidget()
                _container.setLayout(_layout)
                _container.setStyleSheet(f"background-color:{e.color}")
                _container.setSizePolicy(
                    QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
                )
                _container.setContentsMargins(0, 0, 0, 0)  # No margins
                _container.setMinimumHeight(10)  # Set a minimum height if needed
                _time = e.scheduled_at.strftime("%H:%M") if e.scheduled_at else ""
                _title_label = ClickableText(text=f"{_time} - {e.title}", size=14)
                _title_label.setWordWrap(True)
                _title_label.clicked.connect(lambda id=e.id: self._click_event(id))
                _layout.addWidget(_title_label, 0, Qt.AlignmentFlag.AlignTop)
                events_layout.addWidget(_container)

            body_container = QWidget()
            body_container.setLayout(events_layout)
            _css_class = "is_weekdend_body" if is_weekend else "is_weekday_body"
            body_container.setProperty("class", _css_class)

        else:
            empty_label = ClickableText()
            empty_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            empty_label.setWordWrap(True)
            empty_label.setMinimumSize(100, 80)
            empty_label.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )
            _css_class = "is_weekdend_body" if is_weekend else "is_weekday_body"
            empty_label.setProperty("class", _css_class)
            empty_label.clicked.connect(self._click_add_event)

            body_container = empty_label

        # add custom qss for widgets
        StyleSheet.DAY_CELL_WIDGET.apply(date_label)
        StyleSheet.DAY_CELL_WIDGET.apply(body_container)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        main_layout.setContentsMargins(0, 0, 0, 0)  # No margins
        main_layout.setSpacing(0)  # No spacing between widgets
        main_layout.addWidget(date_label)
        main_layout.addWidget(body_container)
        self.setLayout(main_layout)

    def _click_event(self, id: int | None):
        if cfg.get(cfg.action_calendar_to_view) == "CALENDAR_TO_DAY_OVERVIEW":
            signalBus.calendar_actions_signal.emit(
                AppAction.VIEW_OVERVIEW_DAY, None, self.date
            )
        elif cfg.get(cfg.action_calendar_to_view) == "CALENDAR_TO_FORM_VIEW":
            if id and id > 0:
                signalBus.calendar_actions_signal.emit(
                    AppAction.VIEW_FORM_EDIT, id, None
                )
        elif cfg.get(cfg.action_calendar_to_view) == "CALENDAR_TO_NOTHING":
            pass
        else:
            pass

    def _click_month(self, dtime: datetime):
        signalBus.calendar_actions_signal.emit(AppAction.VIEW_OVERVIEW_DAY, None, dtime)

    def _click_add_event(self):
        signalBus.calendar_actions_signal.emit(AppAction.VIEW_FORM_ADD, None, self.date)
