import json
import time
import urllib.parse

import httpx
from PySide6.QtCore import QObject, QRunnable, Signal
from PySide6.QtGui import QImage

from helpers.devtools import debug


def is_valid_json(string):
    try:
        json.loads(string)
        return True
    except (ValueError, TypeError):
        return False


class WorkerManager(QObject):
    """Centralized manager to handle stopping of all workers."""

    stop_all_workers = Signal()

    def __init__(self):
        super().__init__()


class ApiJsonSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    """

    finished = Signal()
    error = Signal(str)
    result = Signal(str)


class WeatherApiJsonWorker(QRunnable):
    """
    Worker thread for weather updates.
    https://www.weatherapi.com/docs/
    """

    signals = ApiJsonSignals()
    is_interrupted = False

    def __init__(
        self,
        latitude: float,
        longitude: float,
        api_token: str,
        lang: str = "en",
    ):
        """
        Args:
            latitude: decimal (-90; 90)
            longitude: decimal (-180; 180)
            api_token: str
        """
        super().__init__()
        self.longitude = longitude
        self.latitude = latitude
        self.api_token = api_token
        self.lang = lang
        self.manager: WorkerManager | None = None  # Reference to the WorkerManager

    def set_manager(self, manager: WorkerManager):
        self.manager = manager
        self.manager.stop_all_workers.connect(self.stop)  # Connect to stop signal

    def run(self):

        if isinstance(self.manager, WorkerManager):
            self.manager.stop_all_workers.connect(self.stop)  # Connect to stop signal
        try:
            if not self.is_interrupted:
                params = dict(
                    key=self.api_token,
                    lang=self.lang,
                    days=3,
                    alerts="yes",
                )  # NEED to remove "en" otherwise you get Arabic
                if self.lang == "en":
                    del params["lang"]
                url = (
                    f"http://api.weatherapi.com/v1/forecast.json?q={self.latitude},{self.longitude}&%s"
                    % urllib.parse.urlencode(params)
                )
                debug(url)
                r = httpx.get(url)
                r.raise_for_status()  # Raises an HTTPStatusError for non-2xx responses
                if self.is_interrupted:
                    return
                self.signals.result.emit(r.text)

        except httpx.HTTPStatusError as e:
            error_message = e.response.text
            if is_valid_json(error_message):
                error = json.loads(error_message)
                self.signals.error.emit(
                    f"""Attempt to contact server failed.\n {error["error"]["message"]}"""
                )
            else:
                self.signals.error.emit(f"HTTP Error: {error_message}")
        except Exception as e:
            self.signals.error.emit(str(e))

        self.signals.finished.emit()

    def stop(self):
        """Method to stop future runs."""
        self.is_interrupted = True


class ImageSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    """

    finished = Signal()
    error = Signal(str)
    result = Signal(QImage, str)


class ImageDownloaderWorker(QRunnable):
    """Worker for downloading images."""

    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self.signals = ImageSignals()
        self.is_interrupted = False
        self.manager: WorkerManager | None = None

    def set_manager(self, manager: WorkerManager):
        self.manager = manager
        self.manager.stop_all_workers.connect(self.stop)  # Connect to stop signal

    def run(self):
        try:
            if not self.is_interrupted:
                with httpx.Client() as client:
                    response = client.get(self.url)
                    response.raise_for_status()  # Raises an HTTPStatusError for non-2xx responses
                    if self.is_interrupted:
                        return
                    image = QImage.fromData(response.content)
                    self.signals.result.emit(image, self.url)

        except httpx.HTTPStatusError as e:
            error_message = e.response.text
            self.signals.error.emit(
                f"Attempt to contact server failed. Try again later."
            )
        except Exception as e:
            self.signals.error.emit(str(e))

        self.signals.finished.emit()

    def stop(self):
        """Method to stop future runs."""
        self.is_interrupted = True
