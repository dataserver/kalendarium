from PySide6 import QtCore
from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from constants.app_constants import (
    COLOR_PALETTES,
    DEFAULT_PALETTE,
    TRANSPARENT_ICON_PATH,
)
from helpers.utility import clear_layout

# 3 palette options: PaletteHorizontal, PaletteVertical, PaletteGrid
__all__ = ["PaletteHorizontal", "PaletteVertical", "PaletteGrid"]


class _PaletteButton(QPushButton):
    """A button that represents a color in the palette.

    Attributes:
        color (str): The background color of the button.
        border_color (str): The border color when selected.
        border_to_selected (bool): Whether to show a border when selected.
    """

    def __init__(
        self, color, border_color: str | None = None, border_to_selected: bool = True
    ):
        """Initializes the color button with specified properties.

        Args:
            color (str): The color of the button.
            border_color (str | None): The color of the border when selected.
            border_to_selected (bool): Determines if a border is shown when selected.
        """
        super().__init__()
        self.setFixedSize(QtCore.QSize(24, 24))
        self.color = color
        self.border_color = border_color or "black"
        self.border_to_selected = border_to_selected
        if self.color == "transparent":
            self.setStyleSheet(f"background-color: transparent;")
            self.setIcon(QIcon(str(TRANSPARENT_ICON_PATH)))
        else:
            self.setStyleSheet(f"background-color: {self.color};")

    def set_selected(self):
        """Sets the button as selected, applying the border style."""
        css_border = (
            f"border:3px solid {self.border_color}" if self.border_to_selected else ""
        )
        if self.color == "transparent":
            self.setStyleSheet(f"background-color: transparent; {css_border};")
        else:
            self.setStyleSheet(f"background-color: {self.color}; {css_border};")

    def set_unselect(self):
        """Resets the button style to unselected (without border)."""
        self.setStyleSheet(f"background-color: {self.color}; border:none;")


class _PaletteLinearBase(QWidget):
    """Base class for linear palettes (horizontal/vertical).

    Attributes:
        selected (Signal): Signal emitted when a color is selected.
    """

    selected = Signal(object)

    def __init__(self, colors=DEFAULT_PALETTE, preselected: str | None = None):
        """Initializes the linear palette with color buttons.

        Args:
            colors (list | str): A list of colors or a palette name.
            preselected (str | None): The color that should be preselected.
        """
        super().__init__()
        self.preselected = preselected

        if colors in COLOR_PALETTES:
            self.colors = COLOR_PALETTES[colors]
        else:
            self.colors = COLOR_PALETTES[DEFAULT_PALETTE]

        self.palette_layout = self._create_layout()
        self.setLayout(self.palette_layout)
        self._populate()

    def _populate(self):
        clear_layout(self.palette_layout)
        self.button_list: list[_PaletteButton] = []
        for color in self.colors:
            btn = _PaletteButton(color)
            if self.preselected == color:
                btn.set_selected()
            btn.pressed.connect(lambda c=color: self._emit_color(c))
            btn.pressed.connect(btn.set_selected)
            self.palette_layout.addWidget(btn)

    def select_color(self, color):
        """Selects a color and unselects others in the palette.

        Args:
            color (str): The color to select.
        """
        for btn in self.button_list:
            if btn.color == color:
                btn.set_selected()
            else:
                btn.set_unselect()

    def set_palette(self, name: str):
        if name in COLOR_PALETTES:
            self.colors = COLOR_PALETTES[name]
            self._populate()

    def _create_layout(self) -> QLayout:
        """Creates the layout for the palette.

        Subclasses should override this method to provide the desired layout type.
        """
        raise NotImplementedError("Subclasses must implement _create_layout.")

    def _emit_color(self, color):
        """Emits the selected color and unselects all buttons.

        Args:
            color (str): The color that was selected.
        """
        for btn in self.button_list:
            btn.set_unselect()
        self.selected.emit(color)


class PaletteHorizontal(_PaletteLinearBase):
    """A horizontal color palette."""

    def _create_layout(self):
        """Creates a horizontal layout."""
        return QHBoxLayout()


class PaletteVertical(_PaletteLinearBase):
    """A vertical color palette."""

    def _create_layout(self):
        """Creates a horizontal layout."""
        return QVBoxLayout()


class PaletteGrid(QWidget):
    """A grid layout for displaying color buttons.

    Attributes:
        selected (Signal): Signal emitted when a color is selected.
    """

    selected = Signal(object)

    def __init__(
        self,
        colors: str = DEFAULT_PALETTE,
        n_columns: int = 5,
        preselected: str | None = None,
        border_color: str | None = None,
        border_to_selected: bool = True,
    ):
        """Initializes the grid palette with color buttons.

        Args:
            colors (list | str): A list of colors or a palette name.
            n_columns (int): The number of columns in the grid.
            preselected (str | None): The color that should be preselected.
            border_color (str | None): The color of the border when selected.
            border_to_selected (bool): Determines if a border is shown when selected.
        """
        super().__init__()

        if colors in COLOR_PALETTES:
            self.colors = COLOR_PALETTES[colors]
        else:
            self.colors = COLOR_PALETTES[DEFAULT_PALETTE]
        self.border_color = border_color
        self.n_columns = n_columns
        self.preselected = preselected
        self.border_to_selected = border_to_selected

        self.palette_layout = QGridLayout()
        self.setLayout(self.palette_layout)
        self._populate()

    def _populate(self):
        clear_layout(self.palette_layout)
        self.button_list: list[_PaletteButton] = []
        row, col = 0, 0
        for color in self.colors:
            btn = _PaletteButton(
                color,
                border_color=self.border_color,
                border_to_selected=self.border_to_selected,
            )
            self.button_list.append(btn)
            if self.preselected == color:
                btn.set_selected()
            btn.pressed.connect(lambda c=color: self._emit_color(c))
            btn.pressed.connect(btn.set_selected)
            self.palette_layout.addWidget(btn, row, col)
            col += 1
            if col == self.n_columns:
                col = 0
                row += 1

    def select_color(self, color):
        """Selects a color and unselects others in the palette.

        Args:
            color (str): The color to select.
        """
        for btn in self.button_list:
            if btn.color == color:
                btn.set_selected()
            else:
                btn.set_unselect()

    def set_palette(self, name: str):
        if name in COLOR_PALETTES:
            self.colors = COLOR_PALETTES[name]
            self._populate()

    def _emit_color(self, color):
        """Emits the selected color and unselects all buttons.

        Args:
            color (str): The color that was selected.
        """
        for btn in self.button_list:
            btn.set_unselect()
        self.selected.emit(color)
