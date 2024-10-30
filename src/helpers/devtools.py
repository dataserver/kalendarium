"""
Make easy to supress/remove dev library from app
"""

from constants.app_constants import DEV_MODE


def _debug_do_nothing(*args):
    pass


if DEV_MODE:
    # class Debug from devtools
    debug = None
    package_name = "devtools"
    class_name = "Debug"
    try:
        module = __import__(package_name)
        _class = getattr(module, class_name)
        debug = _class()
    except ImportError:
        print(f"{package_name} is not installed.")
        debug = _debug_do_nothing
    except AttributeError:
        print(f"{class_name} is not found in {package_name}.")
        debug = _debug_do_nothing
else:
    debug = _debug_do_nothing
