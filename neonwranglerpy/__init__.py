import os
from .lib import *
from neonwranglerpy.lib.tools import get_tables

_ROOT = os.path.abspath(os.path.dirname(__file__))


def get_data(path):
    """helper function to get package data"""
    return os.path.normpath(os.path.join(_ROOT, 'data', path))


get_tables()
