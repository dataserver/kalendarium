from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget
from qfluentwidgets import ComboBoxSettingCard, CustomColorSettingCard, ExpandLayout
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import (
    HyperlinkCard,
    InfoBar,
    OptionsSettingCard,
    ScrollArea,
    SettingCardGroup,
    SwitchSettingCard,
    TitleLabel,
    setTheme,
)

from config.config import cfg
from constants.app_constants import (
    ACTION_JUMP_CALENDAR_TO_DAY_VIEW,
    AUTHOR,
    START_OF_WEEK,
    VERSION,
    YEAR,
)
from constants.weatherapi import WEATHERAPI_LANGUAGES, WEATHERAPI_UNITS
from helpers.devtools import debug
from widgets.setting_lat_long import LatitudeLongitudeSettingCard
from widgets.setting_lineedit import LineEditSettingCard
from widgets.setting_palette import OptionsSettingPaletteCard


class SettingInterface(ScrollArea):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("setting_interface")

        self.main_container = QWidget()
        self.main_container.setObjectName("main_container")
        self.setWidget(
            self.main_container
        )  # specify the widget that you want to display within the ScrollArea
        self.main_layout = ExpandLayout(self.main_container)

        # page label
        self.panel_title_label = TitleLabel(self.tr("Settings"), self)
        self.panel_title_label.setObjectName("panel_title")

        # theme
        self.theme_group = SettingCardGroup(
            self.tr("Personalization"), self.main_container
        )
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            self.tr("Application theme"),
            self.tr("Change the appearance of your application"),
            texts=[self.tr("Light"), self.tr("Dark"), self.tr("Use system setting")],
            parent=self.theme_group,
        )
        self.theme_color_card = CustomColorSettingCard(
            cfg.themeColor,
            FIF.PALETTE,
            self.tr("Theme color"),
            self.tr("Change the theme color of you application"),
            parent=self.theme_group,
        )
        self.zoom_card = OptionsSettingCard(
            cfg.dpi_scale,
            FIF.ZOOM,
            self.tr("Interface zoom"),
            self.tr("Change the size of widgets and fonts"),
            texts=[
                "100%",
                "125%",
                "150%",
                "175%",
                "200%",
                self.tr("Use system setting"),
            ],
            parent=self.theme_group,
        )
        self.language_card = ComboBoxSettingCard(
            cfg.language,
            FIF.LANGUAGE,
            self.tr("Language"),
            self.tr("Set your preferred language for UI"),
            texts=["Português Brasil", "English", self.tr("Use system setting")],
            parent=self.theme_group,
        )

        # to fix: error message if string has UTF-8 characters (constants languages)
        #   not found in font face. Maybe arial could solve.
        # self.language_card.comboBox.setStyleSheet("font-family: Arial;")

        # calendar
        self.calendar_group = SettingCardGroup(self.tr("Calendar"), self.main_container)

        self.action_calendar_to_overview_card = ComboBoxSettingCard(
            cfg.action_calendar_to_view,
            FIF.APPLICATION,
            self.tr("Calendar Behaviour"),
            self.tr("Choose the behavior that occurs when an event entry is clicked"),
            texts=[self.tr(txt) for txt in ACTION_JUMP_CALENDAR_TO_DAY_VIEW.values()],
            parent=self.calendar_group,
        )

        self.start_of_weekCard = ComboBoxSettingCard(
            cfg.start_of_week,
            FIF.CALENDAR,
            self.tr("Start of Week"),
            self.tr("Select the day that starts the week"),
            texts=[self.tr(txt) for txt in START_OF_WEEK.values()],
            parent=self.calendar_group,
        )
        self.palette_card = OptionsSettingPaletteCard(
            cfg.palette_color,
            self.tr("Color Palette"),
            self.tr("Available colors for setting reminders"),
            self.calendar_group,
        )

        # weather
        self.weather_group = SettingCardGroup(
            self.tr("Weather Forecast"), self.main_container
        )
        self.weatherEnabledCard = SwitchSettingCard(
            icon=FIF.TILES,
            title=self.tr("Add the weather widget to start screen"),
            content=self.tr(
                "Enable weather forecast on the start screen. You need a valid OpenWeather API key"
            ),
            configItem=cfg.weather_enabled,
            parent=self.weather_group,
        )
        self.weather_lat_long_card = LatitudeLongitudeSettingCard(
            lat_configItem=cfg.weather_latitude,
            lon_configItem=cfg.weather_longitude,
            icon=FIF.GLOBE,
            title=self.tr("Location"),
            content=self.tr("Latitude and Longitude of the location for the forecast"),
            parent=self.weather_group,
        )
        self.weather_language_card = ComboBoxSettingCard(
            cfg.weather_lang,
            FIF.LANGUAGE,
            self.tr("Language of weather forecast"),
            self.tr("Choose the language for forecast"),
            texts=WEATHERAPI_LANGUAGES.values(),
            parent=self.weather_group,
        )
        self.weather_units_card = ComboBoxSettingCard(
            cfg.weather_units,
            FIF.UNIT,
            self.tr("Units of measurement"),
            self.tr("Units of measurement for forecast"),
            texts=[self.tr(txt) for txt in WEATHERAPI_UNITS.values()],
            parent=self.weather_group,
        )
        self.weather_api_token_card = LineEditSettingCard(
            cfg.weather_api,
            FIF.FINGERPRINT,
            self.tr("WeatherAPI.com API"),
            self.tr("Your WeatherAPI account's API key"),
            parent=self.weather_group,
        )
        self.visit_weather_dot_com_card = HyperlinkCard(
            title=self.tr("weatherAPI.com"),
            icon=FIF.INFO,
            text=self.tr("Visit weatherapi.com"),
            content=self.tr("Visit weatherapi.com to create a free account"),
            parent=self.weather_group,
            url="https://www.weatherapi.com",
        )

        # about
        self.about_group = SettingCardGroup(self.tr("About"), self.main_container)
        self.about_card = HyperlinkCard(
            "https://github.com/dataserver/kalendarium/",
            self.tr("Check update"),
            FIF.INFO,
            self.tr("About"),
            "© "
            + self.tr("Copyright")
            + f" {YEAR}, {AUTHOR}. "
            + self.tr("Version")
            + f" {VERSION}",
            self.about_group,
        )

        self._init_widget()
        self._init_layout()
        self._connect_signals()

    def _init_widget(self):

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 120, 0, 20)
        self.enableTransparentBackground()
        self.setWidgetResizable(True)

    def _init_layout(self):

        self.panel_title_label.move(60, 60)  # fixed position

        # add cards to group
        # Theme
        self.theme_group.addSettingCard(self.themeCard)
        self.theme_group.addSettingCard(self.theme_color_card)
        self.theme_group.addSettingCard(self.zoom_card)
        self.theme_group.addSettingCard(self.language_card)

        # calendar layout
        self.calendar_group.addSettingCard(self.action_calendar_to_overview_card)
        self.calendar_group.addSettingCard(self.start_of_weekCard)
        self.calendar_group.addSettingCard(self.palette_card)

        # weather
        self.weather_group.addSettingCard(self.weatherEnabledCard)
        self.weather_group.addSettingCard(self.weather_api_token_card)
        self.weather_group.addSettingCard(self.weather_lat_long_card)
        self.weather_group.addSettingCard(self.weather_language_card)
        self.weather_group.addSettingCard(self.weather_units_card)
        self.weather_group.addSettingCard(self.visit_weather_dot_com_card)

        # about
        self.about_group.addSettingCard(self.about_card)

        # add setting card group to layout
        self.main_layout.setSpacing(28)
        self.main_layout.setContentsMargins(60, 10, 60, 0)
        self.main_layout.addWidget(self.theme_group)
        self.main_layout.addWidget(self.calendar_group)
        self.main_layout.addWidget(self.weather_group)
        self.main_layout.addWidget(self.about_group)

    def _connect_signals(self):
        cfg.appRestartSig.connect(self._show_restart_tooltip)
        cfg.themeChanged.connect(setTheme)

    def _show_restart_tooltip(self):
        """show restart tooltip"""
        InfoBar.warning(
            "",
            self.tr("Configuration takes effect after restart"),
            parent=self.window(),
        )
