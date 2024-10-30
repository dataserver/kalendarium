import os
import sys

from PySide6.QtCore import QTranslator
from PySide6.QtWidgets import QApplication

from config.config import cfg
from constants.app_constants import BASE_PATH
from gui.main_window import Window

if __name__ == "__main__":
    # enable dpi scale
    if cfg.get(cfg.dpi_scale) != "Auto":
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
        os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpi_scale))
    app = QApplication(sys.argv)

    # internationalization
    locale = cfg.get(cfg.language).value
    translator = QTranslator()
    translator.load(
        locale,
        "general",
        ".",
        str(BASE_PATH / "resources" / "i18n"),
    )
    app.installTranslator(translator)

    # create main window
    w = Window()
    w.show()
    app.exec()
