from datetime import datetime

from pydantic import ValidationError
from PySide6.QtCore import QDate, Qt, QTime
from PySide6.QtWidgets import QFormLayout, QSizePolicy, QVBoxLayout, QWidget
from qfluentwidgets import (
    DatePicker,
    Dialog,
    LineEdit,
    PrimaryPushButton,
    ScrollArea,
    StrongBodyLabel,
    TextEdit,
    TimePicker,
    TitleLabel,
)

from config.config import cfg
from constants.app_constants import AppAction
from helpers.utility import (
    datetime_to_qdate,
    datetime_to_qtime,
    qdate_qtime_to_datetime,
)
from models import repository_events
from models.event import Event
from signals.signal_bus import signalBus
from widgets.palette import PaletteGrid


class EventFormInterface(ScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("event_form_interface")

        self.event_data = None
        self.today = datetime.now()
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

        self.panel_title_label = TitleLabel(self.tr("Event Form"), self)
        self.panel_title_label.setObjectName("panel_title")

        self.form_layout = QFormLayout()

    def _init_layout(self):
        self.enableTransparentBackground()
        self.setViewportMargins(0, 120, 0, 20)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)

        self.panel_title_label.move(60, 60)
        self.inner_container.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        self.main_layout.setContentsMargins(60, 10, 60, 120)
        self.main_layout.setSpacing(40)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_layout.addWidget(self.inner_container)

        self.title_input = LineEdit()
        self.title_input.setPlaceholderText(self.tr("Your Title (Required)"))
        self.description_input = TextEdit()
        self.description_input.setPlaceholderText(self.tr("Description (Optional)"))

        # color
        self.color_input_value = None  # store selected color
        self.palette_input = PaletteGrid(
            colors=cfg.get(cfg.palette_color),
            n_columns=12,
            preselected="transparent",
            border_color=cfg.get(cfg.themeColor).name(),
        )
        self.palette_input.selected.connect(self._set_color_input)
        self.scheduled_date_input = DatePicker(format=1, isMonthTight=False)
        self.scheduled_time_input = TimePicker()

        # form
        self.form_layout.addRow(StrongBodyLabel(self.tr("Title")), self.title_input)
        self.form_layout.addRow(
            StrongBodyLabel(self.tr("Description")), self.description_input
        )
        self.form_layout.addRow(StrongBodyLabel(self.tr("Color")), self.palette_input)
        self.form_layout.addRow(
            StrongBodyLabel(self.tr("Scheduled Date")), self.scheduled_date_input
        )
        self.form_layout.addRow(
            StrongBodyLabel(self.tr("Scheduled Time")), self.scheduled_time_input
        )

        self.submit_button = PrimaryPushButton(self.tr("Submit"))
        self.submit_button.setMaximumWidth(150)
        self.submit_button.clicked.connect(self.save)

        self.inner_layout.addLayout(self.form_layout)
        self.inner_layout.addWidget(self.submit_button, 0, Qt.AlignmentFlag.AlignCenter)

    def _connect_signals(self):
        cfg.palette_color.valueChanged.connect(self._refresh_palette)

    def _refresh_palette(self):
        self.palette_input.set_palette(cfg.get(cfg.palette_color))

    def clear_form(self):
        self.title_input.clear()
        self.description_input.clear()
        self.scheduled_date_input.setDate(QDate.currentDate())
        self.scheduled_time_input.setTime(QTime(8, 0, 0))
        self.palette_input.select_color("transparent")
        self.color_input_value = None

    def populate_by_id(self, id: int):
        row = repository_events.get_event_by_id(id)
        self.event_data = Event(**row)
        if self.event_data:
            self.color_input_value = self.event_data.color
            self.title_input.setText(self.event_data.title or "")
            self.description_input.setText(self.event_data.description or "")
            self.palette_input.select_color(self.event_data.color)
            self.scheduled_date_input.setDate(
                datetime_to_qdate(self.event_data.scheduled_at)
            )
            self.scheduled_time_input.setTime(
                datetime_to_qtime(self.event_data.scheduled_at)
            )

    def set_scheduled_date(self, dtime: datetime):
        new_dt = dtime.replace(hour=8, minute=0, second=0)
        self.scheduled_date_input.setDate(datetime_to_qdate(new_dt))
        self.scheduled_time_input.setTime(datetime_to_qtime(new_dt))

    def reset(self):
        """
        Set event_data to None and clear the form
        """
        self.event_data = None
        self.clear_form()

    def save(self):
        data = {}
        if self.event_data:
            # Populate the dictionary based on event data
            if self.event_data.id:
                data["id"] = self.event_data.id
                data["created_at"] = self.event_data.created_at
                data["updated_at"] = datetime.now()
            else:
                data["created_at"] = datetime.now()

        # Fill in the rest of the event details
        data["title"] = self.title_input.text()
        data["description"] = self.description_input.toPlainText()
        data["color"] = self.color_input_value

        # Get scheduled date and time
        data["scheduled_at"] = qdate_qtime_to_datetime(
            self.scheduled_date_input.getDate(),
            self.scheduled_time_input.getTime(),
        )

        try:
            event = Event(**data)
            if event.id:
                repository_events.update(event_id=event.id, event=event)
            else:
                repository_events.insert(event=event)
            signalBus.calendar_actions_signal.emit(
                AppAction.VIEW_OVERVIEW_MONTH, None, None
            )
        except ValidationError as e:
            error_messages = "\n".join([str(err["msg"]) for err in e.errors()])
            self.show_message("Error", error_messages)

    def _set_color_input(self, color: str):
        self.color_input_value = color

    def show_message(self, title, message):
        w = Dialog(title=title, content=message)
        w.yesButton.hide()
        w.buttonLayout.insertStretch(0, 1)
        w.cancelButton.setText("Close")
        w.exec()
