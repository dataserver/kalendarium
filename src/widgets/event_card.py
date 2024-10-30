from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout
from qfluentwidgets import FluentIcon, TransparentToolButton, setFont

from config.config import cfg
from constants.app_constants import AppAction
from models import repository_events
from models.event import Event
from signals.signal_bus import signalBus
from widgets.clickable_text import ClickableText


class EventCard(QFrame):
    def __init__(self, event: Event, parent=None):
        super().__init__(parent=parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)
        self.date = event.scheduled_at
        self.event_data = event

        if self.event_data.color:
            self.setStyleSheet("background-color:%s;" % self.event_data.color)

        self.title_label = ClickableText(
            text=f"""{self.event_data.scheduled_at.strftime("%H:%M")} - {self.event_data.title}""",
            size=16,
        )
        self.title_label.setProperty("class", "row_event_title")
        self.title_label.setWordWrap(True)
        self.title_label.clicked.connect(lambda id=event.id: self._click_event(id))

        self.description_label = ClickableText(
            text=self.event_data.description, size=14
        )
        self.description_label.setWordWrap(True)
        self.description_label.clicked.connect(
            lambda id=event.id: self._click_event(id)
        )

        self.delete_button = TransparentToolButton(FluentIcon.DELETE, self)
        self.edit_button = TransparentToolButton(FluentIcon.EDIT, self)
        self.delete_button.setFixedSize(32, 32)
        self.edit_button.setFixedSize(32, 32)

        inner_layout = QVBoxLayout()
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.addWidget(self.title_label, 1, Qt.AlignmentFlag.AlignVCenter)
        inner_layout.addWidget(self.description_label, 0, Qt.AlignmentFlag.AlignVCenter)
        inner_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.main_layout.addLayout(inner_layout, 1)
        self.main_layout.addWidget(self.delete_button, 0, Qt.AlignmentFlag.AlignRight)
        self.main_layout.addWidget(self.edit_button, 0, Qt.AlignmentFlag.AlignRight)

        self._connect_signals()

    def _connect_signals(self):
        self.edit_button.clicked.connect(self._action_edit)
        self.delete_button.clicked.connect(self._action_delete)

    def hide_buttons(self):
        self.delete_button.hide()
        self.edit_button.hide()

    def set_fontsize_title(self, size: int = 14):
        setFont(self.title_label, size)

    def _action_edit(self):
        if self.event_data.id:
            signalBus.calendar_actions_signal.emit(
                AppAction.VIEW_FORM_EDIT, self.event_data.id, None
            )

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

    def _action_delete(self):
        if self.event_data.id:
            repository_events.delete_by_id(id=self.event_data.id)
        signalBus.calendar_actions_signal.emit(
            AppAction.VIEW_OVERVIEW_MONTH, None, None
        )
