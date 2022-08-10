import pytest
from neonwranglerpy.utilities import __version__


def test_directory_structure():
    """Initial Tests"""
    assert True


def test_version():
    """Test import version"""
    assert __version__.startswith("v")
