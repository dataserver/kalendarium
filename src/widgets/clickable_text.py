from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from qfluentwidgets import BodyLabel, FluentLabelBase, TitleLabel, getFont


class ClickableText(FluentLabelBase):
    clicked = Signal()

    def __init__(
        self,
        *,
        text: str | None = "",
        size: int = 14,
        bold: bool = False,
        parent=None,
    ):
        self._font_size = size
        self._font_bold = bold
        super().__init__(parent)
        if text:
            self.setText(text)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        # super().mousePressEvent(event)

    # CaptionLabel 12
    # BodyLabel 14
    # StrongBodyLabel 14 bold
    # SubtitleLabel 20 bold
    # TitleLabel 28 bold
    # LargeTitleLabel  40 bold
    # DisplayLabel 68 bold
    def getFont(self):
        size = self._font_size
        if self._font_bold:
            weight = QFont.Weight.Bold
        else:
            if size < 20:
                weight = QFont.Weight.Normal
            elif size >= 20 and size <= 40:
                weight = QFont.Weight.DemiBold
            elif size >= 41:
                weight = QFont.Weight.Bold
            else:
                weight = QFont.Weight.Normal

        return getFont(self._font_size, weight)


class ClickableLabel(BodyLabel):
    clicked = Signal()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()


class ClickableTitleLabel(TitleLabel):
    clicked = Signal()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
