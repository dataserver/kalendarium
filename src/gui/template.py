import sys
from typing import Union

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QEvent,
    QObject,
    QStandardPaths,
    Qt,
    QUrl,
    Signal,
    Slot,
)
from PySide6.QtGui import (
    QColor,
    QDesktopServices,
    QIcon,
    QPainter,
    QPalette,
    QPen,
    QWheelEvent,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QButtonGroup,
    QCalendarWidget,
    QFileDialog,
    QFontDialog,
    QFrame,
    QHBoxLayout,
    QItemDelegate,
    QLabel,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QStyleOptionViewItem,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import (
    AMTimePicker,
    BodyLabel,
    CalendarPicker,
    CaptionLabel,
    ColorPickerButton,
    ColorSettingCard,
    ComboBoxSettingCard,
    CustomColorSettingCard,
    DatePicker,
    Dialog,
    ExpandLayout,
    ExpandSettingCard,
)
from qfluentwidgets import FluentIcon
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import (
    FluentIconBase,
    FluentStyleSheet,
    FolderListSettingCard,
    HeaderCardWidget,
    HyperlinkCard,
    IconWidget,
    InfoBar,
    OptionsConfigItem,
    OptionsSettingCard,
    PrimaryPushButton,
    PrimaryPushSettingCard,
    PushButton,
    PushSettingCard,
    RadioButton,
    RangeSettingCard,
    ScrollArea,
    SettingCard,
    SettingCardGroup,
    SingleDirectionScrollArea,
    StrongBodyLabel,
    SwitchSettingCard,
    Theme,
    TimePicker,
    TitleLabel,
    ToolButton,
    ToolTipFilter,
    ZhDatePicker,
    isDarkTheme,
    qconfig,
    setFont,
    setTheme,
    setThemeColor,
    toggleTheme,
)

from config.config import cfg
from constants.app_constants import AUTHOR, BASE_PATH, DB_PATH, VERSION, YEAR
from helpers.devtools import debug
from helpers.style_sheet import StyleSheet
from helpers.utility import clear_layout
from signals.signal_bus import signalBus
from widgets.palette import PaletteGrid


class TemplateInterface(ScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("template_interface")
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

        self.counter = 1

    def _init_layout(self):
        self.enableTransparentBackground()
        self.setViewportMargins(0, 120, 0, 20)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)

        self.panel_title_label.move(60, 60)

        self.inner_container.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        self.main_layout.setContentsMargins(60, 10, 60, 0)
        self.main_layout.setSpacing(40)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_layout.addWidget(self.inner_container)

        # Button to refresh content
        refresh_button = PushButton(self.tr("Refresh Content on inner_widget"))
        refresh_button.clicked.connect(self.populate)

        self.main_layout.addWidget(refresh_button)
        self.main_layout.addWidget(self.inner_container)

        # StyleSheet.TEMPLATE_INTERFACE.apply(somewidget)  # will override qfluentwidgets style

        # Initial population
        self.populate()

    def _connect_signals(self):
        pass

    def populate(self):
        """Populate the container with new widgets."""
        clear_layout(self.inner_layout)

        # random samples to test scrolling
        for i in range(10):
            _text = self.counter * " -"
            self.counter += 1
            label = BodyLabel(self.tr("Item") + f" {i + 1} {self.counter}")
            label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            label.setFixedHeight(50)  # Set fixed height for uniformity
            label.setWordWrap(True)
            self.inner_layout.addWidget(label)
