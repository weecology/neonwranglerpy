"""API defining checkpoint."""
import os

_ROOT = os.path.abspath(os.path.dirname(__file__))


def get_data(file):
    """Return the path of data file from data directory."""
    return os.path.normpath(os.path.join(_ROOT, "data", file))


# get_tables()
