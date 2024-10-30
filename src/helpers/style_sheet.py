from enum import Enum

from qfluentwidgets import StyleSheetBase, Theme, qconfig

from constants.app_constants import BASE_PATH


class StyleSheet(StyleSheetBase, Enum):
    """Style sheet"""

    TEMPLATE_INTERFACE = "template_interface"
    MONTHLY_WIDGET = "monthly_widget"
    DAY_CELL_WIDGET = "day_cell_widget"

    def path(self, theme=Theme.AUTO):
        theme = qconfig.theme if theme == Theme.AUTO else theme
        p = BASE_PATH / "resources" / "qss" / theme.value.lower() / f"{self.value}.qss"
        return str(p)
