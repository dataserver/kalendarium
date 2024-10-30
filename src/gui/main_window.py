from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QSystemTrayIcon
from qfluentwidgets import Action
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import (
    FluentWindow,
    NavigationItemPosition,
    SystemThemeListener,
    SystemTrayMenu,
)

from constants.app_constants import APP_TITLE, DB_PATH, AppAction
from gui.eventform import EventFormInterface
from gui.home import HomeInterface
from gui.overview_day import OverviewDayInterface
from gui.overview_month import OverviewMonthInterface
from gui.setting import SettingInterface
from helpers.devtools import debug
from models import repository_events, repository_weatherforecasts
from signals.signal_bus import signalBus


class SystemTrayIcon(QSystemTrayIcon):

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setIcon(parent.windowIcon())

        self.menu = SystemTrayMenu(parent=parent)
        self.menu.addActions(
            [
                Action(self.tr("Restore"), triggered=self._restore),
                Action(self.tr("Quit"), triggered=self._quit),
            ]
        )
        self.setContextMenu(self.menu)

    def _restore(self):
        signalBus.tray_action.emit("restore")

    def _quit(self):
        QApplication.quit()


class Window(FluentWindow):
    """Main Interface"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # create system theme listener
        self._check_db_if_exists()
        self.themeListener = SystemThemeListener()

        self.home_interface = HomeInterface()
        self.setting_interface = SettingInterface()
        self.overview_month_interface = OverviewMonthInterface()
        self.overview_day_interface = OverviewDayInterface()
        self.eventform_interface = EventFormInterface()
        # self.template_interface = TemplateInterface() # example

        self._init_window()
        self._init_navigation()
        self._connect_signals()

        # start theme listener
        self.themeListener.start()

        # tray icon
        self.systemTrayIcon = SystemTrayIcon(self)
        self.systemTrayIcon.show()

    def _init_navigation(self):
        self.addSubInterface(self.home_interface, FIF.HOME, self.tr("Home"))
        self.addSubInterface(
            self.overview_month_interface, FIF.CALENDAR, self.tr("Calendar")
        )
        self.addSubInterface(
            self.setting_interface,
            FIF.SETTING,
            self.tr("Settings"),
            NavigationItemPosition.BOTTOM,
        )

        # add interfaces to stack (but keep hidden)
        self.stackedWidget.addWidget(self.overview_day_interface)
        self.stackedWidget.addWidget(self.eventform_interface)

    def _init_window(self):
        self.resize(1000, 720)
        self.setWindowIcon(self._get_icon("logo/small.png"))
        self.setWindowTitle(APP_TITLE)
        self.center_window()

    def _connect_signals(self):
        signalBus.tray_action.connect(self.on_tray_action)
        signalBus.calendar_actions_signal.connect(self._calendar_actions)

    @Slot(str)
    def on_tray_action(self, reason):
        if reason == "restore":
            self.showNormal()  # Show the window
            self.setWindowState(Qt.WindowState.WindowActive)  # Set the window to active
            self.raise_()  # Bring it to the front
            self.activateWindow()  # Focus on the window

    @Slot(str, object, datetime)
    def _calendar_actions(
        self,
        action: str,
        event_id: int | None,
        date: datetime | None,
    ):
        debug(action, event_id, date)

        if action == AppAction.VIEW_OVERVIEW_DAY and date:
            self.overview_day_interface.set_date(date)
            self.overview_day_interface.populate()
            self.stackedWidget.setCurrentWidget(self.overview_day_interface)
        if action == AppAction.VIEW_OVERVIEW_MONTH:
            self.overview_month_interface.populate()
            self.stackedWidget.setCurrentWidget(self.overview_month_interface)
            self.home_interface.populate()

        if action == AppAction.VIEW_FORM_ADD:
            if not date:
                date = datetime.now()
            self.eventform_interface.reset()
            self.eventform_interface.set_scheduled_date(date)
            self.stackedWidget.setCurrentWidget(self.eventform_interface)
        if action == AppAction.VIEW_FORM_EDIT and event_id and event_id > 0:
            self.stackedWidget.setCurrentWidget(self.eventform_interface)
            self.eventform_interface.populate_by_id(event_id)

    def _check_db_if_exists(self):
        """
        Check if sqlite3 exists. Create database and tables if needed.
        """
        if not DB_PATH.exists():
            print(f"Database {DB_PATH} does not exist, it will be created.")
            repository_events.create_table()
            repository_weatherforecasts.create_table()

    def _get_icon(self, file: str | Path) -> QIcon:
        from constants.app_constants import BASE_PATH

        try:
            p = Path(BASE_PATH, "resources", file)
            if not p.is_file():
                raise Exception(f"file not found: {p}")
            return QIcon(str(p))
        except Exception as e:
            print(f"{e}")
            exit()

    # windows events
    def minimizeEvent(self, event):
        # Hide the window instead of minimizing
        event.ignore()
        self.hide()

    def closeEvent(self, e):
        self.themeListener.terminate()
        self.themeListener.deleteLater()
        super().closeEvent(e)

    def center_window(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_center = screen_geometry.center()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_center)
        self.move(window_geometry.topLeft())
