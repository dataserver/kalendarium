import sys
from datetime import datetime

from PySide6 import QtGui
from PySide6.QtCore import QCoreApplication, QDate, QTime
from PySide6.QtGui import QColor


def translate(key: str, context: str) -> str:
    """
    Translates a given string using the specified context and key.

    This function utilizes the Qt framework's translation capabilities
    to return the translated string corresponding to the provided key
    within the given context.

    Context is defined in resources/i18n/[some_name].[lang].qm

    Args:
        key (str): The translation key representing the original text
                   to be translated.
        context (str): The context in which the translation is used,
                       typically representing the source file or module.

    Returns:
        str: The translated string corresponding to the given key in
             the specified context. If no translation is found, the
             original key may be returned.

    Example:
        translated_text = translate("hello", "greetings")
    """
    return QCoreApplication.translate(context, key)


def isWin11():
    return sys.platform == "win32" and sys.getwindowsversion().build >= 22000


def from_ts_to_time_of_day(ts: float):
    dt = datetime.fromtimestamp(ts)
    return dt.strftime("%I%p").lstrip("0")


# Function to convert RGB string to QColor
def rgb_to_qcolor(rgb_str: str | None) -> QColor:
    if not rgb_str:
        return QtGui.QColorConstants.Red
    # Remove the '#' if present
    rgb_str = rgb_str.lstrip("#")

    # Convert the hex string to integer values
    if len(rgb_str) == 6:  # Ensure it's in the correct format
        r = int(rgb_str[0:2], 16)
        g = int(rgb_str[2:4], 16)
        b = int(rgb_str[4:6], 16)
        return QColor(r, g, b)
    else:
        raise ValueError("Invalid RGB string format. Use '#RRGGBB'.")


def adjust_color_intensity(color_str: str, intensity: float) -> str:
    """
    Adjusts the intensity of a given color represented in hex format.

    This function takes a color in hex format (e.g., '#RRGGBB') and
    modifies its intensity based on a specified factor. An intensity
    value of 0 will result in black, while a value of 1 will keep the
    original color unchanged. Values in between will produce a color
    that is a blend of the original color and black.

    Args:
        color_str (str): A string representing the color in hex format
                         (e.g., '#FF5733'). The '#' character is optional.
        intensity (float): A float representing the desired intensity,
                           where 0.0 is completely black and 1.0 is the
                           original color.

    Returns:
        str: The adjusted color in hex format (e.g., '#7F2B19').

    Raises:
        ValueError: If the input color string is not a valid hex color.

    Example:
        adjusted_color = adjust_color_intensity("#FF5733", 0.5)
    """
    # Ensure intensity is in range 0 to 1
    intensity = max(0, min(intensity, 1))

    # Remove the '#' and convert to QColor
    color_str = color_str.lstrip("#")
    r = int(color_str[0:2], 16)
    g = int(color_str[2:4], 16)
    b = int(color_str[4:6], 16)

    # Adjust the intensity
    r = int(r * intensity)
    g = int(g * intensity)
    b = int(b * intensity)

    # Return the new color in hex format
    return "#{:02X}{:02X}{:02X}".format(r, g, b)


def clear_layout(layout):
    """
    Recursively clears all widgets and nested layouts from the given layout.

    This function iterates through the items in the specified layout,
    removing each widget and calling `deleteLater()` on it to ensure
    proper cleanup. If it encounters a nested layout, it calls itself
    recursively to clear that layout as well.

    Args:
        layout (QLayout): The layout to be cleared, which can contain
                          widgets and/or nested layouts.
    """
    while layout.count():
        item = layout.takeAt(0)  # Take the item at index 0
        if item.widget():
            item.widget().deleteLater()  # Schedule the widget for deletion
        elif item.layout():
            clear_layout(item.layout())  # Recursively clear nested layouts


def qdate_qtime_to_datetime(date: QDate, time: QTime) -> datetime:
    """
    Convert a QDate and QTime to a datetime object.

    Args:
        date (QDate): The date component to convert.
        time (QTime): The time component to convert.

    Returns:
        datetime: A datetime object representing the combined date and time.
    """
    return datetime(
        date.year(),
        date.month(),
        date.day(),
        time.hour(),
        time.minute(),
        time.second(),
    )


def datetime_to_qdate(dt: datetime) -> QDate:
    """
    Convert a datetime object to a QDate.

    Args:
        dt (datetime): The datetime object to convert.

    Returns:
        QDate: A QDate object representing the date part of the datetime.
    """
    return QDate(dt.year, dt.month, dt.day)


def datetime_to_qtime(dt: datetime) -> QTime:
    """
    Convert a datetime object to a QTime.

    Args:
        dt (datetime): The datetime object to convert.

    Returns:
        QTime: A QTime object representing the time part of the datetime.
    """
    return QTime(dt.hour, dt.minute, dt.second, dt.microsecond // 1000)


def qdate_to_datetime(qdate: QDate) -> datetime:
    """
    Convert a QDate to a datetime object.

    Args:
        qdate (QDate): The QDate object to convert.

    Returns:
        datetime: A datetime object representing the date in the QDate.
    """
    return datetime(qdate.year(), qdate.month(), qdate.day())


def is_daytime(date_string: str) -> bool:
    """
    Determines whether the given date and time falls within daytime hours.

    This function checks if a specified date and time, provided as a string,
    falls between 6:00 AM and 6:00 PM. If the time is within this range,
    the function returns True; otherwise, it returns False.

    Args:
        date_string (str): A string representing the date and time in
                           the format "YYYY-MM-DD HH:MM" (e.g.,
                           "2024-10-17 08:15").

    Returns:
        bool: True if the time is during the daytime (between 6:00 AM
              and 6:00 PM), False otherwise.

    Example:
        >>> is_daytime("2024-10-17 08:15")
        True
        >>> is_daytime("2024-10-17 19:30")
        False

    Raises:
        ValueError: If the input string is not in the expected format.
    """
    # Parse the date string into a datetime object
    dt = datetime.strptime(date_string, "%Y-%m-%d %H:%M")

    # Define the start and end of the day
    start_of_day = dt.replace(hour=6, minute=0)
    end_of_day = dt.replace(hour=18, minute=0)

    # Check if the time is within the daytime range
    if start_of_day <= dt < end_of_day:
        return True
    else:
        return False


def get_day_of_week(dtime: str | datetime) -> str:
    """
    Get the day of the week from a date string in 'YYYY-MM-DD' format.

    Parameters:
    date_str (str): The input date string in 'YYYY-MM-DD' format.

    Returns:
    str: The day of the week corresponding to the date, or an error message if
         the input format is invalid or the date is not valid.
    """
    try:
        if isinstance(dtime, str):
            dt = fix_date_format(dtime)
            # Parse the date string into a datetime object
            dtime = datetime.strptime(dt, "%Y-%m-%d")
        # return dtime.strftime("%A")
        return translate(dtime.strftime("%A"), "ConstantsFile")
    except ValueError:
        return "Invalid date format"


def fix_date_format(date_str: str) -> str:
    """
    Fix the date string format from 'YYYY-M-D' or 'YYYY-MM-D' to 'YYYY-MM-DD'.

    This function handles cases where either the month or the day may be a single digit,
    adding leading zeros as necessary. It validates the resulting date string to ensure it
    forms a valid date.

    Parameters:
    date_str (str): The input date string in 'YYYY-M-D' or 'YYYY-MM-D' format.

    Returns:
    str: The fixed date string in 'YYYY-MM-DD' format, or an error message if the input
         format is invalid or the date is not valid.
    """

    # Split the input string into its components
    parts = date_str.split("-")

    # Ensure we have exactly three parts (year, month, day)
    if len(parts) != 3:
        return "Invalid date format"

    year, month, day = parts

    # Handle single-digit month or day
    month = month.zfill(2)  # Add leading zero if needed
    day = day.zfill(2)  # Add leading zero if needed

    # Reconstruct the date string
    fixed_date_str = f"{year}-{month}-{day}"

    # Validate the date
    try:
        datetime.strptime(fixed_date_str, "%Y-%m-%d")
        return fixed_date_str
    except ValueError:
        return "Invalid date"
