from datetime import datetime, timedelta

from PySide6.QtCore import Qt, QThreadPool, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import (
    CaptionLabel,
    StrongBodyLabel,
    SubtitleLabel,
    TitleLabel,
    setFont,
)

from config.config import cfg
from helpers.devtools import debug
from helpers.utility import clear_layout
from helpers.worker import ImageDownloaderWorker, WeatherApiJsonWorker, WorkerManager
from models import repository_weatherforecasts
from models.weatherapi_response import ForecastDay
from models.weatherforecast import WeatherForecast


class WeatherForecastWidget(QWidget):
    populateSignal = Signal()

    def __init__(self):
        super().__init__()
        self.forecast = None
        self.is_enabled = cfg.get(cfg.weather_enabled)
        self.latitude = float(cfg.get(cfg.weather_latitude))
        self.longitude = float(cfg.get(cfg.weather_longitude))
        self.api_token = cfg.get(cfg.weather_api)
        self.today = datetime.now()
        self.manager = WorkerManager()

        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(3)  # Limit to 3 concurrent threads
        self.is_warning_messagebox_open = False

        self.todo_works: list[ImageDownloaderWorker] = []
        self.icon_urls: list[str] = []
        self.label_object_names: dict[str, str] = {}

        if self.is_enabled:
            self._init_widget()
            self.populateSignal.connect(self.populate)
            self._check_stored_forecast()

    def _init_widget(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        # inner
        self.inner_layout = QVBoxLayout()
        self.inner_layout.setContentsMargins(0, 0, 0, 0)
        self.inner_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.inner_container = QWidget()
        self.inner_container.setObjectName("inner_container")
        self.inner_container.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        self.inner_container.setLayout(self.inner_layout)
        # add inner to main
        self.main_layout.addWidget(self.inner_container)

    def populate(self):
        clear_layout(self.inner_layout)
        if not self.is_enabled:
            return
        if not self.forecast:
            self.forecast = repository_weatherforecasts.get_for_day(self.today)

        if self.forecast:
            if self.forecast.json_obj is not None:
                condition = (
                    self.forecast.json_obj.current.condition
                )  #  ["current"]["condition"]
                # weather title
                self.title_label = TitleLabel(condition.text)
                self.title_label.setSizePolicy(
                    QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
                )

                # weather icon
                _url = "http:" + condition.icon
                self.ltop_weather_icon_label = QLabel()
                work = ImageDownloaderWorker(_url)
                work.signals.result.connect(self._set_top_weather_icon)
                self.thread_pool.start(work)

                # temperature
                txt_unit_measurement = (
                    f"""{int( self.forecast.json_obj.current.temp_c )} °C"""
                    if cfg.get(cfg.weather_units) == "metric"
                    else f"""{int( self.forecast.json_obj.current.temp_f )} °F"""
                )
                self.temperature_label = TitleLabel(txt_unit_measurement)
                self.temperature_label.setSizePolicy(
                    QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
                )
                self.location_label = StrongBodyLabel(
                    self.forecast.json_obj.location.name
                )
                self.location_label.setSizePolicy(
                    QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
                )

                # last updated
                self.last_updated_label = SubtitleLabel(
                    self.tr("Last Updated")
                    + " : "
                    + self.forecast.json_obj.current.last_updated
                )
                setFont(self.last_updated_label, 12)
                # layout
                self.inner_layout.addWidget(
                    self.title_label, 1, Qt.AlignmentFlag.AlignCenter
                )
                self.inner_layout.addWidget(
                    self.ltop_weather_icon_label, 1, Qt.AlignmentFlag.AlignCenter
                )
                self.inner_layout.addWidget(
                    self.temperature_label, 1, Qt.AlignmentFlag.AlignCenter
                )
                self.inner_layout.addWidget(
                    self.location_label, 1, Qt.AlignmentFlag.AlignCenter
                )
                self.inner_layout.addWidget(
                    self.last_updated_label, 1, Qt.AlignmentFlag.AlignRight
                )
                # days forecast
                forecastdays = self.forecast.json_obj.forecast.forecastday
                for castday in forecastdays:
                    _dtime = datetime.strptime(castday.date, "%Y-%m-%d")
                    _dow = self.tr(_dtime.strftime("%A"))
                    _m = self.tr(_dtime.strftime("%B"))
                    _subtitle = _dtime.strftime(f"%d {_m} - {_dow}")
                    _df = WeatherHoursForecast(castday, self)

                    self.inner_layout.addWidget(StrongBodyLabel(_subtitle))
                    self.inner_layout.addWidget(_df)

                for work in self.todo_works:
                    work.set_manager(self.manager)
                    work.signals.result.connect(self._set_hour_weather_icon)
                    work.signals.error.connect(self._stop_all_workers)
                    work.signals.error.connect(self._warning_message_box)
                    self.thread_pool.start(work)

        else:
            self.inner_layout.addWidget(
                QLabel(self.tr("Unable to retrieve the forecast"))
            )

    def _stop_all_workers(self):
        self.manager.stop_all_workers.emit()

    def _check_stored_forecast(self):

        stored_cast = repository_weatherforecasts.get_for_day(self.today)

        if stored_cast:
            # forecast older than 1 hour
            if (self.today - stored_cast.date) > timedelta(hours=1):
                self._get_weatherapi_json_data()
            else:
                self.forecast = stored_cast
                self.populateSignal.emit()
        else:
            self._get_weatherapi_json_data()

    def _get_weatherapi_json_data(self):
        worker = WeatherApiJsonWorker(
            latitude=self.latitude,
            longitude=self.longitude,
            api_token=self.api_token,
            lang=cfg.get(cfg.weather_lang),
        )
        worker.signals.result.connect(self._insert_json_to_database)
        worker.signals.error.connect(self._warning_message_box)
        self.thread_pool.start(worker)

    def _insert_json_to_database(self, json_str):
        _data = {"date": self.today, "json_obj": json_str}
        self.forecast = WeatherForecast(**_data)
        repository_weatherforecasts.insert(self.forecast)
        self.populateSignal.emit()

    def _warning_message_box(self, message):
        if not self.is_warning_messagebox_open:
            self.is_warning_messagebox_open = True
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText(message)
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QMessageBox.StandardButton.Close)
            button = msg.exec()
            if button == QMessageBox.StandardButton.Close:
                self.is_warning_messagebox_open = False

    def _set_hour_weather_icon(self, image: QImage, url: str):
        for key, value in self.label_object_names.items():
            if value == url:
                label = self.findChild(QLabel, key)
                if label:
                    pixmap = QPixmap.fromImage(image)
                    scaled = pixmap.scaled(
                        22,
                        22,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                    label.setPixmap(scaled)

    def _set_top_weather_icon(self, image: QImage, url: str):
        pixmap = QPixmap.fromImage(image)
        self.ltop_weather_icon_label.setPixmap(pixmap)


class WeatherHoursForecast(QWidget):
    def __init__(self, forecastday: ForecastDay, parent=None):
        super().__init__()
        self.parent = parent  # type: ignore
        self.hours = forecastday.hour

        self._init_widget()
        self._init_layout()

    def _init_widget(self):
        self.main_container = QWidget()
        self.main_layout = QHBoxLayout()
        self.main_container.setLayout(self.main_layout)
        self.setLayout(self.main_layout)

    def _init_layout(self):

        for i in range(0, len(self.hours), 2):
            hour_forecast = self.hours[i]
            # init widgets
            cell_container = QWidget()
            cell_container.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
            )
            cell_layout = QVBoxLayout()
            cell_container.setLayout(cell_layout)

            # variables
            hour_forecast_dt = datetime.strptime(hour_forecast.time, "%Y-%m-%d %H:%M")

            # icon
            _url = "http:" + hour_forecast.condition.icon
            _obj_name = f"weather_icon_id_{len(self.parent.label_object_names)}"
            icon_label = QLabel()
            icon_label.setObjectName(_obj_name)
            if _url not in self.parent.icon_urls:
                _work = ImageDownloaderWorker(_url)
                self.parent.todo_works.append(_work)
                self.parent.icon_urls.append(_url)
            self.parent.label_object_names[_obj_name] = _url

            # hour
            hour_label = CaptionLabel(hour_forecast_dt.strftime("%H"))
            setFont(hour_label, 12)

            # temperature
            _txt = (
                f"""{int(hour_forecast.temp_c)}°C"""
                if cfg.get(cfg.weather_units) == "metric"
                else f"""{int(hour_forecast.temp_f)}°F"""
            )
            temperature_label = CaptionLabel(_txt)
            setFont(temperature_label, 12)

            # add layout
            cell_layout.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignHCenter)
            cell_layout.addWidget(hour_label, 0, Qt.AlignmentFlag.AlignHCenter)
            cell_layout.addWidget(temperature_label, 0, Qt.AlignmentFlag.AlignHCenter)

            self.main_layout.addWidget(cell_container)
