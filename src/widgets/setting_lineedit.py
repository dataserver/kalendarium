from typing import Union

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel
from qfluentwidgets import (
    ExpandSettingCard,
    FluentIcon,
    FluentStyleSheet,
    LineEdit,
    qconfig,
)


class LineEditSettingCard(ExpandSettingCard):
    """Setting card"""

    def __init__(
        self,
        configItem,
        icon: Union[str, QIcon, FluentIcon],
        title,
        content: str | None = None,
        parent=None,
    ):
        super().__init__(icon, title, content, parent)  # type: ignore
        self.configItem = configItem
        self.configName = configItem.name
        self.choiceLabel = QLabel(self)
        self.line_edit = LineEdit()

        self.addWidget(self.choiceLabel)

        self.viewLayout.setSpacing(19)
        self.viewLayout.setContentsMargins(48, 18, 0, 18)

        # initialize layout "viewLayout" from ExpandSettingCard
        self.viewLayout.addWidget(self.line_edit)

        self._adjustViewSize()
        self.line_edit.setText(qconfig.get(self.configItem))
        self.line_edit.setProperty(self.configName, qconfig.get(self.configItem))
        self.line_edit.textChanged.connect(self._on_value_change)

        FluentStyleSheet.SETTING_CARD.apply(self)

    def setValue(self, value: str):
        """set the value of config item"""

        self.line_edit.setProperty(self.configName, value)

    def _on_value_change(self, value: str):
        qconfig.set(self.configItem, value)
