import re
from enum import Enum

from PySide6.QtCore import QLocale
from qfluentwidgets import (
    BoolValidator,
    ConfigItem,
    ConfigSerializer,
    ConfigValidator,
    OptionsConfigItem,
    OptionsValidator,
    QConfig,
    qconfig,
)

from constants.app_constants import (
    ACTION_JUMP_CALENDAR_TO_DAY_VIEW,
    COLOR_PALETTES,
    CONFIG_PATH,
    START_OF_WEEK,
)
from constants.weatherapi import WEATHERAPI_LANGUAGES
from helpers.devtools import debug


class Language(Enum):
    """Language enumeration"""

    # Add your language here.

    # /Add your language here.
    ENGLISH = QLocale(QLocale.Language.English)
    PORTUGUESE_BRAZILIAN = QLocale(
        QLocale.Language.Portuguese, territory=QLocale.Country.Brazil
    )
    AUTO = QLocale()  # This will use the system locale by default


class LanguageSerializer(ConfigSerializer):
    """Language serializer"""

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


class LatitudeCoordinate(ConfigValidator):
    def validate(self, value):
        """
        Validate latitude value.
        Latitude must be between -90 and 90 degrees.
        """
        try:
            lat = float(value)
            return -90 <= lat <= 90
        except ValueError:
            return False


class LongitudeCoordinate(ConfigValidator):
    def validate(self, value):
        """
        Validate longitude value.
        Longitude must be between -180 and 180 degrees.
        """
        try:
            lon = float(value)
            return -180 <= lon <= 180
        except ValueError:
            return False

    # def correct(self, value):
    #     """correct illegal value"""
    #     return value


class ApiValidator(ConfigValidator):
    def validate(self, value):
        pattern = r"^[a-f0-9]+$"
        return bool(re.match(pattern, value))


class Config(QConfig):
    """Config of application"""

    # main window
    language = OptionsConfigItem(
        "General",
        "language",
        Language.AUTO,
        OptionsValidator(Language),
        LanguageSerializer(),
        restart=True,
    )
    dpi_scale = OptionsConfigItem(
        "General",
        "dpi_scale",
        "Auto",
        OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]),
        restart=True,
    )

    # calendar
    action_calendar_to_view = OptionsConfigItem(
        "General",
        "action_calendar_to_view",
        "CALENDAR_TO_DAY_OVERVIEW",
        OptionsValidator(list(ACTION_JUMP_CALENDAR_TO_DAY_VIEW)),
        restart=True,
    )
    start_of_week_options = list(START_OF_WEEK.keys())
    start_of_week = OptionsConfigItem(
        "General",
        "start_of_week",
        "SUNDAY",
        OptionsValidator(start_of_week_options),
        restart=True,
    )
    palette_options = list(COLOR_PALETTES.keys())
    palette_color = OptionsConfigItem(
        "General",
        "palette_color",
        "Tableau10",
        OptionsValidator(palette_options),
        restart=False,
    )

    # weather
    weather_enabled = ConfigItem(
        "Weather",
        "weather_enabled",
        False,
        BoolValidator(),
        restart=True,
    )
    weather_latitude = ConfigItem(
        "Weather",
        "weather_latitude",
        "40.754019",
        LatitudeCoordinate(),
        restart=True,
    )
    weather_longitude = ConfigItem(
        "Weather",
        "weather_longitude",
        "-73.997044",
        LongitudeCoordinate(),
        restart=True,
    )
    weather_units = OptionsConfigItem(
        "Weather",
        "weather_units",
        "imperial",
        OptionsValidator(["metric", "imperial"]),
        restart=True,
    )
    weather_lang = OptionsConfigItem(
        "Weather",
        "weather_lang",
        "en",
        OptionsValidator(WEATHERAPI_LANGUAGES.keys()),
        restart=True,
    )
    weather_api = ConfigItem(
        "Weather",
        "weather_api",
        "",
        ApiValidator(),
        restart=True,
    )


cfg = Config()
qconfig.load(CONFIG_PATH, cfg)
