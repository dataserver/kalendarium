import sys
from enum import StrEnum, auto, unique
from pathlib import Path

DEV_MODE = False

__version__ = "0.1.21"
APP_TITLE = "Kalendarium"
YEAR = 2024
AUTHOR = "John Doe"
VERSION = __version__

BASE_PATH = Path(__file__).parent.parent
CONFIG_PATH = BASE_PATH / "config" / "config.json"
DB_PATH = BASE_PATH / "models" / "database.sqlite3"
I18N_PATH = BASE_PATH / "resources" / "i18n"
TRANSPARENT_ICON_PATH = BASE_PATH / "resources" / "icon_transparent.png"

if "--dev" in sys.argv:
    DEV_MODE = True
    CONFIG_PATH = BASE_PATH.parent / ".dev" / "config.json"
    DB_PATH = BASE_PATH.parent / ".dev" / "database.sqlite3"


@unique
class AppAction(StrEnum):
    ADD_EVENT = auto()
    EDIT_EVENT = auto()
    UPDATE_EVENT = auto()
    DELETE_EVENT = auto()

    VIEW_OVERVIEW_DAY = auto()
    VIEW_OVERVIEW_MONTH = auto()

    VIEW_FORM_ADD = auto()
    VIEW_FORM_EDIT = auto()


ACTION_JUMP_CALENDAR_TO_DAY_VIEW = {
    "CALENDAR_TO_DAY_OVERVIEW": "Go to Day Overview",
    "CALENDAR_TO_FORM_VIEW": "Go to Event Form",
    "CALENDAR_TO_NOTHING": "Do Nothing",
}
START_OF_WEEK = {
    "SUNDAY": "Sunday",
    "MONDAY": "Monday",
    "TUESDAY": "Tuesday",
    "WEDNESDAY": "Wednesday",
    "THURSDAY": "Thursday",
    "FRIDAY": "Friday",
    "SATURDAY": "Saturday",
}

DAY_OF_WEEK_CODE = {
    "SUNDAY": 0,
    "MONDAY": 1,
    "TUESDAY": 2,
    "WEDNESDAY": 3,
    "THURSDAY": 4,
    "FRIDAY": 5,
    "SATURDAY": 6,
}

DEFAULT_PALETTE = "Tableau10"
COLOR_PALETTES = {
    # https://www.tableau.com/blog/colors-upgrade-tableau-10-56782
    "Tableau10": [
        "transparent",
        "#4a779d",
        "#f38043",
        "#e04c5b",
        "#74b4aa",
        "#5d9a56",
        "#f1c05c",
        "#ab7499",
        "#fd93a1",
        "#996d60",
        "#b9aaa5",
    ],
    # d3 category 10
    "category10": [
        "transparent",
        "#1f77b4",
        "#ff7f0e",
        "#d62728",
        "#17becf",
        "#2ca02c",
        "#bcbd22",
        "#9467bd",
        "#e377c2",
        "#8c564b",
        "#7f7f7f",
    ],
    # 17 undertones https://lospec.com/palette-list/17undertones
    "17undertones": [
        "transparent",
        "#000000",
        "#141923",
        "#414168",
        "#3a7fa7",
        "#35e3e3",
        "#8fd970",
        "#5ebb49",
        "#458352",
        "#dcd37b",
        "#fffee5",
        "#ffd035",
        "#cc9245",
        "#a15c3e",
        "#a42f3b",
        "#f45b7a",
        "#c24998",
        "#81588d",
        "#bcb0c2",
        "#ffffff",
    ],
}
