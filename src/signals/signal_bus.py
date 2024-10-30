from datetime import datetime

from PySide6.QtCore import QObject, Signal


class SignalBus(QObject):
    calendar_actions_signal = Signal(str, int, datetime)
    weather_finished = Signal()
    weather_error = Signal(str)
    weather_result = Signal(dict, dict)
    tray_action = Signal(str)

    _instance = None  # Class variable to hold the single instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SignalBus, cls).__new__(cls, *args, **kwargs)
        return cls._instance


signalBus = SignalBus()
