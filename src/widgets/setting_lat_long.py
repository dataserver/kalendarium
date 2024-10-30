from typing import Union

from PySide6.QtGui import QIcon, QPainter
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget
from qfluentwidgets import (
    ExpandSettingCard,
    FluentIcon,
    FluentStyleSheet,
    IconWidget,
    LineEdit,
    drawIcon,
    qconfig,
)


class SettingIconWidget(IconWidget):

    def paintEvent(self, e):
        painter = QPainter(self)

        if not self.isEnabled():
            painter.setOpacity(0.36)

        painter.setRenderHints(
            QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform
        )
        drawIcon(self._icon, painter, self.rect())


class LatitudeLongitudeSettingCard(ExpandSettingCard):
    """Setting card"""

    def __init__(
        self,
        *,
        lat_configItem,
        lon_configItem,
        icon: Union[str, QIcon, FluentIcon],
        title,
        content: str | None = None,
        parent=None,
    ):
        super().__init__(icon, title, content, parent)  # type: ignore
        self.lat_configItem = lat_configItem
        self.lat_configName = lat_configItem.name
        self.lon_configItem = lon_configItem
        self.lon_configName = lon_configItem.name

        self.choiceLabel = QLabel(self)
        self.latitude_edit = LineEdit()
        self.latitude_edit.setObjectName("latitude")
        self.longitude_edit = LineEdit()
        self.longitude_edit.setObjectName("longitude")

        self.addWidget(self.choiceLabel)

        self.viewLayout.setSpacing(19)
        self.viewLayout.setContentsMargins(48, 18, 0, 18)

        # initialize layout
        row_container = QWidget()
        row_layout = QHBoxLayout()
        row_container.setLayout(row_layout)
        row_layout.addWidget(QLabel(self.tr("Latitude")))
        row_layout.addWidget(self.latitude_edit)
        row_layout.addSpacing(100)
        row_layout.addWidget(QLabel(self.tr("Longitude")))
        row_layout.addWidget(self.longitude_edit)

        self.viewLayout.addWidget(row_container)
        self._adjustViewSize()

        self.latitude_edit.setText(qconfig.get(self.lat_configItem))
        self.latitude_edit.setProperty(
            self.lat_configName, qconfig.get(self.lat_configItem)
        )
        self.latitude_edit.textChanged.connect(self._on_lat_value_change)

        self.longitude_edit.setText(qconfig.get(self.lon_configItem))
        self.longitude_edit.setProperty(
            self.lon_configName, qconfig.get(self.lon_configItem)
        )
        self.longitude_edit.textChanged.connect(self._on_lon_value_change)

        FluentStyleSheet.SETTING_CARD.apply(self)

    def setValue(self, value: str):
        """set the value of config item"""

        self.latitude_edit.setProperty(self.lat_configName, value)
        self.longitude_edit.setProperty(self.lon_configName, value)

    def _on_lat_value_change(self, value: str):
        qconfig.set(self.lat_configItem, value)

    def _on_lon_value_change(self, value: str):
        qconfig.set(self.lon_configItem, value)
