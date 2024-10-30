from PySide6.QtCore import Signal
from PySide6.QtWidgets import QButtonGroup, QHBoxLayout, QLabel, QWidget
from qfluentwidgets import ExpandSettingCard
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import OptionsConfigItem, RadioButton, qconfig

from constants.app_constants import COLOR_PALETTES
from widgets.palette import PaletteGrid


class OptionsSettingPaletteCard(ExpandSettingCard):
    """setting card with a group of options"""

    option_changed = Signal(OptionsConfigItem)

    def __init__(
        self,
        configItem,
        title,
        content: str | None = None,
        parent=None,
    ):
        icon = FIF.PALETTE
        super().__init__(icon, title, content, parent)  # type: ignore
        self.palette_names = list(COLOR_PALETTES.keys())
        self.configItem = configItem
        self.configName = configItem.name
        self.choice_label = QLabel(self)
        self.button_group = QButtonGroup(self)
        self.addWidget(self.choice_label)

        # create buttons
        self.viewLayout.setSpacing(19)
        self.viewLayout.setContentsMargins(48, 18, 0, 18)
        for text, option in zip(self.palette_names, configItem.options):
            _row = QWidget()
            _row_layout = QHBoxLayout()
            _row.setLayout(_row_layout)
            _button = RadioButton(text, self.view)
            _button.setProperty(self.configName, option)
            self.button_group.addButton(_button)
            _row_layout.addWidget(_button)
            _row_layout.addWidget(
                self._create_palette_sample_display(palette_name=text)
            )
            self.viewLayout.addWidget(_row)

        self._adjustViewSize()
        self.setValue(qconfig.get(self.configItem))
        configItem.valueChanged.connect(self.setValue)
        self.button_group.buttonClicked.connect(self._onButtonClicked)

    def setValue(self, value):
        """select button according to the value"""
        qconfig.set(self.configItem, value)

        for button in self.button_group.buttons():
            is_checked = button.property(self.configName) == value
            button.setChecked(is_checked)
            if is_checked:
                self.choice_label.setText(button.text())
                self.choice_label.adjustSize()

    def _onButtonClicked(self, button: RadioButton):
        """button clicked slot"""
        if button.text() == self.choice_label.text():
            return

        value = button.property(self.configName)
        qconfig.set(self.configItem, value)

        self.choice_label.setText(button.text())
        self.choice_label.adjustSize()
        self.option_changed.emit(self.configItem)

    def _create_palette_sample_display(self, palette_name: str):
        palette = PaletteGrid(
            colors=palette_name, n_columns=5, border_to_selected=False
        )
        return palette
